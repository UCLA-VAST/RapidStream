import click
import logging
import json
from typing import Callable, Dict

import pyverilog.vparser.ast as ast
from pyverilog.ast_code_generator import codegen
from pyverilog.vparser.parser import parse

from rapidstream.util import setup_logging

_logger = logging.getLogger().getChild(__name__)

STREAM_TYPES = (
  'fifo',
  'relay_station',
)

CTRL_SIGNALS = (
  'ap_clk',
  'ap_rst_n',
  'ap_start',
  'ap_done',
  'ap_idle',
  'ap_ready',
  'ap_local_deadlock',
)

PEEK_PORT_SUFFIX = (
  '_peek_read',
  '_peek_dout',
  '_peek_empty_n',
)

INBOUND_STREAM_PORTS = (
  'if_din',
  'if_full_n',
  'if_write',
)
OUTBOUND_STREAM_PORTS = (
  'if_dout',
  'if_empty_n',
  'if_read',
)
OTHER_STREAM_PORTS = (
  'clk',
  'reset',
  'if_read_ce',
  'if_write_ce',
)

S_AXI_LITE_SUFFIX = (
  'AWVALID',
  'AWREADY',
  'AWADDR',
  'WVALID',
  'WREADY',
  'WDATA',
  'WSTRB',
  'ARVALID',
  'ARREADY',
  'ARADDR',
  'RVALID',
  'RREADY',
  'RDATA',
  'RRESP',
  'BVALID',
  'BREADY',
  'BRESP',
)

S_AXI_LITE_BASIC = (
  'ACLK',
  'ARESET',
  'ACLK_EN',
  'interrupt',
)

# collect all wire decl
# collect all wire/port of each FIFO/relay_station
# collect all wire/port of each task instance
# skip control signals

# need a routine to group several instances into one instance
# the new instance should have a consistent interface as other lower-level instances
# the routing should be able to handle a mix of upper-level instance and lower-level instances

# still use json as an IR

# need another routine to embed control signals into an instance
# two cases: 1 the signal just passes by
# 2 the signal will be connected to the internal of the instance


def visitor(ast: ast.Node, action: Callable, *args) -> None:
  action(ast, *args)
  for c in ast.children():
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
    config['wire_decl'][node.name] = _get_width(node)


def get_input_info(node: ast.Node, config: Dict):
  """Collect all Input declarations"""
  if isinstance(node, ast.Input):
    config['input_decl'][node.name] = _get_width(node)


def get_output_info(node: ast.Node, config: Dict):
  """Collect all Output declarations"""
  if isinstance(node, ast.Output):
    config['output_decl'][node.name] = _get_width(node)


def get_decl_info(ast: ast.Source, config: Dict):
  for target in ('wire', 'input', 'output'):
    config[f'{target}_decl'] = {}
  visitor(ast, get_wire_info, config)
  visitor(ast, get_input_info, config)
  visitor(ast, get_output_info, config)


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
def is_peek_port(portname: str):
  return any(portname.endswith(suffix) for suffix in PEEK_PORT_SUFFIX)


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
    'axi_ports': {},  # for top level AXI connection
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

      axi_name_task_side = portname_split[2]
      axi_name_top_side = argname_split[2]

      if axi_name_task_side not in port_wire_map['axi_ports']:
        port_wire_map['axi_ports'][axi_name_task_side] = {
          'axi_name_task_side': axi_name_task_side,
          'axi_name_top_side': axi_name_top_side,
        }

    elif argname in wire_to_stream:
      stream_name = wire_to_stream[argname]
      if stream_name not in port_wire_map['stream_ports']:
        port_wire_map['stream_ports'][stream_name] = {

        }
      port_wire_map['stream_ports'][stream_name][portname] = argname

    # the argname of a peek port may be empty
    elif is_peek_port(portname):
      if argname is None:
        continue

    else:
      port_wire_map['constant_ports'][portname] = argname

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
    }


def get_vertex_info(node: ast.Node, config: Dict, wire_to_stream: Dict):
  """Collect all port/wire binding of each task instance"""
  if isinstance(node, ast.InstanceList):
    if node.module not in STREAM_TYPES:
      _get_task_vertex_info(node, config, wire_to_stream)
      _get_ctrl_vertex_info(node, config)


def check_rtl_format(node: ast.Node):
  if isinstance(node, ast.InstanceList):
    assert len(node.instances) == 1


def collect_in_out_streams(config: Dict):
  """Collect the inbound and outbound streams for each vertex"""
  for edge, props in config['edges'].items():
    if props['category'] == 'FIFO_EDGE':
      src = props['produced_by']
      dst = props['consumed_by']

      if 'outbound_streams' not in config['vertices'][src]:
        config['vertices'][src]['outbound_streams'] = []
      if 'inbound_streams' not in config['vertices'][dst]:
        config['vertices'][dst]['inbound_streams'] = []

      config['vertices'][src]['outbound_streams'].append(edge)
      config['vertices'][dst]['inbound_streams'].append(edge)


@click.command()
@click.option(
  '--top-rtl-path',
  required=True,
  help='Path to the top-level RTL generated by TAPA.'
)
@click.option(
  '--post-floorplan-config-path',
  required=True,
  help='Path to the configuration file generated by AutoBridge.'
)
def get_rtl(
  top_rtl_path: str,
  post_floorplan_config_path: str,
):
  """"""
  setup_logging()

  config = json.load(open(post_floorplan_config_path, 'r'))

  ast, directives = parse([top_rtl_path])
  visitor(ast, check_rtl_format)

  get_decl_info(ast, config)

  wire_to_stream = {}
  visitor(ast, get_stream_info, config, wire_to_stream)

  visitor(ast, get_vertex_info, config, wire_to_stream)

  collect_in_out_streams(config)
  open('test.json', 'w').write(json.dumps(config, indent=2))

if __name__ == '__main__':
  get_rtl()
