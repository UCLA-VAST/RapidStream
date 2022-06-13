import logging
import re
from typing import Callable, Dict

import pyverilog.vparser.ast as ast
from pyverilog.ast_code_generator import codegen

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def visitor(node: ast.Node, action: Callable, *args) -> None:
  action(node, *args)
  for c in node.children():
    visitor(c, action, *args)


def _get_width(node: ast.Node) -> str:
  """Extract the width as a string in the format of [msb:lsb]"""
  if node.width is None:
    width = ''
  else:
    width = str(codegen.ASTCodeGenerator().visit(node.width))
  return width


def get_wire_info(node: ast.Node, config: Dict):
  """Collect all Wire declarations"""
  if isinstance(node, ast.Wire):
    # collect two types of wires
    # 1. the data wires connecting to all streams
    # 2. the wires connecting to the s_axi_control
    # since tapa duplicates the s_axi_control to each SLR
    # we only collect one ctrl instance by checking the '_slr_0' suffix
    if any(ap in node.name for ap in CTRL_SIGNALS + ('__rst__', '__is_done__')):
      return

    config['wire_decl'][node.name] = _get_width(node)


def get_input_info(node: ast.Node, config: Dict):
  """Collect all Input declarations"""
  if isinstance(node, ast.Input):
    config['input_decl'][node.name] = _get_width(node)


def get_output_info(node: ast.Node, config: Dict):
  """Collect all Output declarations"""
  if isinstance(node, ast.Output):
    config['output_decl'][node.name] = _get_width(node)


def get_params(node: ast.Node, config: Dict):
  """Collect all parameters at the top level"""
  if isinstance(node, ast.Parameter):
    config['parameter_decl'][node.name] = codegen.ASTCodeGenerator().visit(node.value)


def get_decl_info(root: ast.Source, config: Dict):
  for target in ('wire', 'input', 'output', 'parameter'):
    config[f'{target}_decl'] = {}
  visitor(root, get_params, config)
  visitor(root, get_wire_info, config)
  visitor(root, get_input_info, config)
  visitor(root, get_output_info, config)


def get_stream_info(node: ast.Node, config: Dict, wire_to_stream: Dict):
  """Collect all port/wire binding of each stream"""
  if isinstance(node, ast.InstanceList):
    if node.module in STREAM_TYPES:
      instance = node.instances[0]
      edge_name = f'FIFO_EDGE_{instance.name}'
      assert edge_name in config['edges']

      port_wire_map = {
        'inbound': {},
        'outbound': {},
        'others': {}
      }
      for port_arg in instance.portlist:
        portname = str(port_arg.portname)
        argname = str(port_arg.argname)

        if portname in INBOUND_STREAM_PORTS:
          port_wire_map['inbound'][portname] = argname
        elif portname in OUTBOUND_STREAM_PORTS:
          port_wire_map['outbound'][portname] = argname
        elif portname in OTHER_STREAM_PORTS:
          port_wire_map['others'][portname] = argname
        else:
          assert False

        wire_to_stream[argname] = edge_name

      config['edges'][edge_name]['port_wire_map'] = port_wire_map

# track which axi interfaces we have already recorded
axi_visited = set()

def _get_task_vertex_info(
  node: ast.InstanceList,
  config: Dict,
  wire_to_stream: Dict,
) -> None:
  instance = node.instances[0]
  task_name = f'TASK_VERTEX_{instance.name}'
  if task_name not in config['vertices']:
    return

  port_wire_map = {
    'axi_ports': [],  # for top level AXI connection
    'ctrl_ports': {},  # for ap signals
    'constant_ports': {},  # for scalar arguments from s_axi_control,
    'stream_ports': {},  # connect to FIFOs
  }

  for port_arg in instance.portlist:
    portname = str(port_arg.portname)
    argname = str(port_arg.argname)

    if portname.startswith('ap_') and portname not in CTRL_SIGNALS:
      _logger.warning('port %s may trigger a corner case', portname)

    if portname in CTRL_SIGNALS:
      port_wire_map['ctrl_ports'][portname] = argname

    elif portname.startswith('m_axi_'):
      # e.g., m_axi_mmap_BVALID => ['m', 'axi', 'mmap', 'BVALID']
      portname_split = portname.split('_')
      argname_split = argname.split('_')
      assert len(portname_split) == 4 and portname_split[-1].isupper()
      assert len(argname_split) == 4 and argname_split[-1].isupper()

      axi_name_port_side = portname_split[2]
      axi_name_arg_side = argname_split[2]

      # FIXME: collect readonly/writeonly info here
      # axi ports. Use the data width to represent the width for the interface
      # input_decl stores the port name -> width mapping
      if (axi_name_port_side, axi_name_arg_side) not in axi_visited:
        entry = {
          'portname': axi_name_port_side,
          'argname': axi_name_arg_side,
          'data_width': config['input_decl'][f'm_axi_{axi_name_arg_side}_RDATA'],
        }
        port_wire_map['axi_ports'].append(entry)
      axi_visited.add((axi_name_port_side, axi_name_arg_side))

    elif argname in wire_to_stream:
      stream_name = wire_to_stream[argname]
      if stream_name not in port_wire_map['stream_ports']:
        port_wire_map['stream_ports'][stream_name] = {

        }
      port_wire_map['stream_ports'][stream_name][portname] = argname

    # the argname of a peek port may be empty
    elif any(portname.endswith(suffix) for suffix in PEEK_PORT_SUFFIX):
      if argname is None:
        continue

    # constant arg
    else:
      orig_wirename = re.search(f'{instance.name}___(\S+)__q\d+', argname).group(1)
      port_wire_map['constant_ports'][portname] = orig_wirename

  config['vertices'][task_name]['port_wire_map'] = port_wire_map


def _get_ctrl_vertex_info(
  node: ast.InstanceList, config: Dict
) -> None:
  if node.module.endswith('_control_s_axi'):
    instance = node.instances[0]
    task_name = 'CTRL_VERTEX_control_s_axi'
    if task_name in config['vertices']:
      return

    port_wire_map = {
      'axi_ports': {},  # for top level AXI connection
      'ctrl_ports': {},  # for ap signals
      'basic_ports': {},  # clk, reset
      'constant_ports': {},  # for scalar arguments from s_axi_control,
    }

    param_map = {}
    for param_arg in instance.parameterlist:
      param_map[param_arg.paramname] = param_arg.argname.name

    for port_arg in instance.portlist:
      portname = str(port_arg.portname)
      argname = str(port_arg.argname)

      if portname.startswith('ap_') and portname not in CTRL_SIGNALS:
        _logger.warning('port %s may trigger a corner case', portname)

      if portname in CTRL_SIGNALS:
        port_wire_map['ctrl_ports'][portname] = argname
      elif portname in S_AXI_LITE_SUFFIX:
        port_wire_map['axi_ports'][portname] = argname
      elif portname in S_AXI_LITE_BASIC:
        port_wire_map['basic_ports'][portname] = argname
      else:
        _logger.info('treat port %s in the s_axi_control as a constant port', portname)
        port_wire_map['constant_ports'][portname] = argname

    config['vertices'][task_name] = {
      'module': node.module,
      'instance': None,
      "area": {
        "BRAM": 0,
        "DSP": 0,
        "FF": 1000,
        "LUT": 1000,
        "URAM": 0
      },
      'category': 'CTRL_VERTEX',
      'port_wire_map': port_wire_map,
      'param_map': param_map,
    }


def get_vertex_info(node: ast.Node, config: Dict, wire_to_stream: Dict) -> None:
  """Collect all port/wire binding of each task instance"""
  if isinstance(node, ast.InstanceList):
    if node.module not in STREAM_TYPES:
      _get_task_vertex_info(node, config, wire_to_stream)
      _get_ctrl_vertex_info(node, config)


def check_rtl_format(node: ast.Node) -> None:
  if isinstance(node, ast.InstanceList):
    assert len(node.instances) == 1

  if isinstance(node, ast.Wire):
    if node.name.endswith('_slr_0'):
      _logger.error('Please disable the s_axi_ctrl duplication in tapa')
      exit(1)


def collect_in_out_streams(config: Dict) -> None:
  """Collect the inbound and outbound streams for each vertex"""
  for vertex, props in config['vertices'].items():
    props['inbound_streams'] = []
    props['outbound_streams'] = []

  for edge, props in config['edges'].items():
    if props['category'] == 'FIFO_EDGE':
      src = props['produced_by']
      dst = props['consumed_by']
      config['vertices'][src]['outbound_streams'].append(edge)
      config['vertices'][dst]['inbound_streams'].append(edge)


def annotate_width_to_port_wire_map(config: Dict) -> None:
  """Annotate the width info to the port-wire map of every vertex
     Assume non-existing ports are of width 1
  """
  for v_name, props in config['vertices'].items():
    if props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue

    port_wire_map = props['port_wire_map']
    port_width_map = {}

    # constant scalar ports
    for scalar_name, scalar_wire_name in port_wire_map['constant_ports'].items():
      # assume the axi address space is 64-bit
      if scalar_name.endswith('_offset'):
        port_width_map[scalar_name] = '[63:0]'
      else:
        port_width_map[scalar_name] = config['wire_decl'][scalar_name]

    # stream ports
    for stream_name, _port_wire_map in port_wire_map['stream_ports'].items():
      data_width_int = config['edges'][stream_name]['width']
      for portname, wirename in _port_wire_map.items():
        if portname.endswith('_din') or portname.endswith('_dout'):
          port_width_map[portname] = f'[{data_width_int-1}:0]'

    # all ctrl ports have the width 1

    props['port_width_map'] = port_width_map


def remove_unused_peek_ports(config):
  """If the _peek_read port is not connected, remove the _peek_empty_n and _peek_dout ports"""
  for v_name, props in config['vertices'].items():
    if props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue

    stream_port_info = props['port_wire_map']['stream_ports']

    # if xxx_peek_dout exists, check if xxx_peek_read exists.
    # if not, then prune the port
    # tapa-generated RTL will leave xxx_peek_read() float if peek is not used
    for stream_name, orig_port_wire_map in stream_port_info.items():
      filter_unused_peek = {}
      for portname, argname in orig_port_wire_map.items():
        if portname.endswith(('_peek_dout', '_peek_empty_n')):
          base_name = portname.split('_peek_')[0]
          if f'{base_name}_peek_read' not in orig_port_wire_map:
            _logger.info('prune unused peek port %s from %s', portname, v_name)
            continue
        else:
          filter_unused_peek[portname] = argname

      stream_port_info[stream_name] = filter_unused_peek


def parse_tapa_output_rtl(
  config: Dict,
  root: ast.Source,
) -> Dict:
  """Extract all info needed from the top RTL generated by TAPA"""

  # check if format is correct
  visitor(root, check_rtl_format)

  # get all declarations (wire, input, output)
  get_decl_info(root, config)

  # get the info related to streams
  # get the mapping from wire to a stream that it connects to
  wire_to_stream = {}
  visitor(root, get_stream_info, config, wire_to_stream)

  # get the inbound streams and outbound streams for each vertex
  collect_in_out_streams(config)

  # get the info related to vertices
  visitor(root, get_vertex_info, config, wire_to_stream)

  # add width info into the properties of each vertex
  annotate_width_to_port_wire_map(config)

  remove_unused_peek_ports(config)

  return config
