import logging
import re
from typing import Dict, List

from rapidstream.const import *
from rapidstream.rtl_gen.const import *
from rapidstream.rtl_gen.ctrl_wrapper import get_param_decl_section

_logger = logging.getLogger().getChild(__name__)


def get_io_direction(v_props: Dict, portname: str) -> str:
  if portname in v_props['io_dir_to_name_to_width']['input']:
    return 'input'
  elif portname in v_props['io_dir_to_name_to_width']['output']:
    return 'output'
  else:
    assert False


def _get_wire_to_io_of_slot(v_props: Dict) -> Dict[str, str]:
  wire_to_io = {}
  pw_map = v_props['port_wire_map']

  # FIXME: consider readonly/writeonly cases
  # no pipelining for AXI interfaces => connect to top IO
  for axi_entry in pw_map['axi_ports']:
    if axi_entry['axi_type'] == 'M_AXI':
      axi_port_name = axi_entry['portname']
      wirename = axi_entry['argname']
      for suffix in get_m_axi_interface(axi_entry['data_width']).keys():
        # inst.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{wirename}_{suffix}),')
        wire_to_io[f'm_axi_{wirename}_{suffix}'] = f'm_axi_{axi_port_name}_{suffix}'
    elif axi_entry['axi_type'] == 'S_AXI_LITE':
      for portname, dir_and_width in S_AXI_LITE_INTERFACE.items():
        # inst.append(f'  .s_axi_control_{portname}(s_axi_control_{portname}),')
        wire_to_io[f's_axi_control_{portname}'] = f's_axi_control_{portname}'

  for argname, wirename in pw_map.get('constant_ports', {}).items():
    # inst.append(f'  .{argname}({wirename}_input),')
    wire_to_io[f'{wirename}_input'] = argname

  for argname in pw_map.get('ctrl_out', []):
    # inst.append(f'  .{argname}({argname}_output),')
    wire_to_io[f'{argname}_output'] = argname

  for argname in pw_map.get('ctrl_in', []):
    # inst.append(f'  .{argname}({argname}_input),')
    wire_to_io[f'{argname}_input'] = argname

  for argname in pw_map.get('reset_out', []):
    # inst.append(f'  .{argname}({argname}_output),')
    wire_to_io[f'{argname}_output'] = argname

  for argname in pw_map.get('constant_out', []):
    # inst.append(f'  .{argname}({argname}_output),')
    wire_to_io[f'{argname}_output'] = argname

  for stream_pw_map in pw_map.get('stream_ports', {}).values():
    for argname, wirename in stream_pw_map.items():
      direction = get_io_direction(v_props, argname)
      # inst.append(f'  .{argname}({wirename}_{direction}),')
      wire_to_io[f'{wirename}_{direction}'] = argname

  # passing wires
  passing_streams = pw_map.get('passing_streams', {})
  for name, props in passing_streams.items():
    s1 = props['inbound_side_suffix']
    s2 = props['outbound_side_suffix']
    for wire_name in props['wire_to_width'].keys():
      s1_direction = get_io_direction(v_props, f'{wire_name}_{s1}')
      s2_direction = get_io_direction(v_props, f'{wire_name}_{s2}')
      # inst.append(f'  .{wire_name}_{s1}({wire_name}_{s1}_{s1_direction}),')
      # inst.append(f'  .{wire_name}_{s2}({wire_name}_{s2}_{s2_direction}),')
      wire_to_io[f'{wire_name}_{s1}_{s1_direction}'] = f'{wire_name}_{s1}'
      wire_to_io[f'{wire_name}_{s2}_{s2_direction}'] = f'{wire_name}_{s2}'

  # passing constants:
  passing_constants = pw_map.get('passing_constants', {})
  for pc in passing_constants:
    for dir in ('input', 'output'):
      wire_to_io[f'{pc[dir]}_{dir}'] = pc[dir]

  if v_props['category'] != 'CTRL_WRAPPER':
    # inst.append(f'  .ap_start(ap_start_{v_props["instance"]}_input),')
    # inst.append(f'  .ap_done(ap_done_{v_props["instance"]}_output),')
    # inst.append(f'  .ap_rst_n(ap_rst_n_{v_props["instance"]}_input),')
    wire_to_io[f'{pw_map["ctrl_ports"]["ap_start"]}_input'] = 'ap_start'
    wire_to_io[f'{pw_map["ctrl_ports"]["ap_rst_n"]}_input'] = 'ap_rst_n'
    wire_to_io[f'{pw_map["ctrl_ports"]["ap_done"]}_output'] = 'ap_done'
  else:
    # top level IO
    # inst.append(f'  .ap_rst_n(ap_rst_n),')
    wire_to_io['ap_rst_n'] = 'ap_rst_n'

  # top level IO
  # inst.append(f'  .ap_clk(ap_clk)')
  wire_to_io['ap_clk'] = 'ap_clk'

  return wire_to_io


def _get_slot_inst(v_props: Dict, module_name_suffix: str) -> List[str]:
  """the instance for each slot
     Change the wire name of input ports to reflect the pipelining
     module_name_suffix changes the type of the module as we instantiate them
     When we add a register layer around a module, it is generated as a separated file
     and not recorded in the config file. Thus we use module_name_suffix to control
     which version of the module we instantiate
  """
  inst = []

  inst.append('(* dont_touch = "yes" *)')
  inst.append(f'{v_props["module"]}{module_name_suffix} {v_props["instance"]}(')

  wire_to_io = _get_wire_to_io_of_slot(v_props)

  for wire, io in wire_to_io.items():
    inst.append(f'  .{io}({wire}),')

  inst[-1] = inst[-1].strip(',')
  inst.append(f');')

  return inst


def get_slot_insts(config: Dict, module_name_suffix: str) -> List[str]:
  """Skip ctrl vertex and other conceptual vertices like port vertices"""
  insts = []
  for v_name, v_props in config['vertices'].items():
    assert v_props['category'] not in ('PORT_VERTEX', 'CTRL_VERTEX')
    insts += _get_slot_inst(v_props, module_name_suffix) + ['']

  return insts


def _get_anchor_reg_decl(name, width):
  """declare the register and connects it.
      Naming: the anchor xxx will be connected to wires xxx_input and xxx_output
  """
  anchor_decl = []
  anchor_decl.append(f'wire {width} {name}_input;')
  anchor_decl.append(f'wire {width} {name}_output;')
  anchor_decl.append(f'(* dont_touch = "yes" *) reg {width} {name}_q;')
  anchor_decl.append(f'always @ (posedge ap_clk) {name}_q <= {name}_output;')
  anchor_decl.append(f'assign {name}_input = {name}_q;')
  return anchor_decl


def _get_used_wires(config: Dict, slot_insts: List[str]) -> List[str]:
  """filter out wires that do not connect to any slot instants"""
  used_wires = []
  for name, width in config['wire_decl'].items():
    if any(re.search(f'\.{name}[ ]*\(', line) for line in slot_insts):
      used_wires.append(name)
    else:
      _logger.warning('temp hack to remove constant wire %s from top rtl', name)
  return used_wires


def get_anchor_reg_decl(config: Dict, slot_insts: List[str]) -> List[str]:
  """Instantiate the wires between instances and the control signals"""
  anchor_decl = []
  for name in _get_used_wires(config, slot_insts):
    width = config['wire_decl'][name]
    anchor_decl += _get_anchor_reg_decl(name, width)

  return anchor_decl


def get_selected_anchor_reg_decl(config: Dict, selected_wire_to_io: Dict[str, str]) -> List[str]:
  """only instantiated some anchor registers"""
  def get_base_name(wire_name):
    """if a wire is xxx_input or xxx_output, the anchor name is xxx_q"""
    return re.sub('_(in|out)put$', '', wire_name)

  anchor_decl = []
  for wire_name in selected_wire_to_io:
    base_name = get_base_name(wire_name)
    width = config['wire_decl'].get(base_name, '')
    # top-level IO
    if base_name not in config['wire_decl']:
      continue
    anchor_decl += _get_anchor_reg_decl(base_name, width)
  return anchor_decl


def get_io_section(config: Dict, top_name: str) -> List[str]:
  """Get the top-level IOs"""
  io = []
  io.append('`timescale 1 ns / 1 ps')
  io.append('')

  io.append(f'(* dont_touch = "yes" *) module {top_name} (')
  for name, width in config['input_decl'].items():
    io.append(f'  {name},')

  for name, width in config['output_decl'].items():
    io.append(f'  {name},')

  io[-1] = io[-1].strip(',')
  io.append(');')
  io.append('')

  io += get_param_decl_section(config)

  for name, width in config['input_decl'].items():
    io.append(f'input {width} {name};')

  for name, width in config['output_decl'].items():
    io.append(f'output {width} {name};')

  return io


def set_unused_ports(config: Dict, wire_to_io: Dict = {}) -> List[str]:
  """prevent an output port from floating. If wire_to_io is none, only consider assigning
  floating outputs that appear in wire_to_io. If not provided, consider all floating outputs"""
  zero_output = []

  # all wire to io mapping
  if not wire_to_io:
    for v_name, v_props in config['vertices'].items():
      wire_to_io.update(_get_wire_to_io_of_slot(v_props))

  for name, width in config['output_decl'].items():
    if name not in wire_to_io:
      zero_output.append(f'assign {name} = 0;')
      _logger.info('the output port %s is floating, assign it to 0', name)
  return zero_output


def get_ending() -> List[str]:
  return ['endmodule']


def sort_rtl(top: List[str]) -> List[str]:
  """Move all wire and reg declaration to the front"""
  decl = []
  other = []

  for line in top:
    if 'wire ' in line or 'reg ' in line:
      decl.append(line)
    else:
      other.append(line)

  return decl + other


def safety_check(io_section: List[str]) -> bool:
  for port in ('interrupt', 'ap_local_block'):
    if not any(re.search(rf'[ ]+{port}[ ]*,[ ]*', line) for line in io_section):
      _logger.error('Missing top-level port ' + port)
      exit(1)


def _get_top(config: Dict, top_name: str, wrapper_suffix: str) -> List[str]:
  top = []

  slot_insts = get_slot_insts(config, wrapper_suffix) + ['']

  # use the rtl for slot instances to filter out unused wires
  top += get_anchor_reg_decl(config, slot_insts) + ['']
  top += slot_insts + ['']

  top += set_unused_ports(config)
  top += get_ending() + ['']
  top_sorted = sort_rtl(top)

  io_section = get_io_section(config, top_name)
  safety_check(io_section)
  
  return io_section + [''] + top_sorted + ['']
  

def get_top(config: Dict, top_name: str, use_anchor_wrapper: bool) -> List[str]:
  wrapper_suffix = ANCHOR_WRAPPER_SUFFIX if use_anchor_wrapper else ''
  return _get_top(config, top_name, wrapper_suffix)


def get_top_with_empty_islands(config: Dict, top_name: str) -> List[str]:
  """Get the top RTL that instantiate empty dummy islands"""
  return _get_top(config, top_name, DUMMY_WRAPPER_SUFFIX)
