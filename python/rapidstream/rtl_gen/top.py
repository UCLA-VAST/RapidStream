import logging
from typing import Dict, List

from rapidstream.const import *
from rapidstream.rtl_gen.const import *

_logger = logging.getLogger().getChild(__name__)


def get_io_direction(v_props: Dict, portname: str) -> str:
  if portname in v_props['io_dir_to_name_to_width']['input']:
    return 'input'
  elif portname in v_props['io_dir_to_name_to_width']['output']:
    return 'output'
  else:
    assert False


def get_slot_inst(v_props: Dict, module_name_suffix: str) -> List[str]:
  """the instance for each slot
     Change the wire name of input ports to reflect the pipelining
  """
  inst = []
  pw_map = v_props['port_wire_map']

  inst.append('(* dont_touch = "yes" *)')
  inst.append(f'{v_props["module"]}{module_name_suffix} {v_props["instance"]}(')

  # FIXME: consider readonly/writeonly cases
  # no pipelining for AXI interfaces => connect to top IO
  for axi_entry in pw_map['axi_ports']:
    if axi_entry['axi_type'] == 'M_AXI':
      axi_port_name = axi_entry['portname']
      wirename = axi_entry['argname']
      for suffix in M_AXI_INTERFACE.keys():
        inst.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{wirename}_{suffix}),')
    elif axi_entry['axi_type'] == 'S_AXI_LITE':
      for portname, dir_and_width in S_AXI_LITE_INTERFACE.items():
        inst.append(f'  .s_axi_control_{portname}(s_axi_control_{portname}),')

  for argname, wirename in pw_map.get('constant_ports', {}).items():
    inst.append(f'  .{argname}({wirename}_input),')

  for argname in pw_map.get('ctrl_out', []):
    inst.append(f'  .{argname}({argname}_output),')

  for argname in pw_map.get('ctrl_in', []):
    inst.append(f'  .{argname}({argname}_input),')

  for argname in pw_map.get('reset_out', []):
    inst.append(f'  .{argname}({argname}_output),')

  for argname in pw_map.get('constant_out', []):
    inst.append(f'  .{argname}({argname}_output),')

  for stream_pw_map in pw_map.get('stream_ports', {}).values():
    for argname, wirename in stream_pw_map.items():
      direction = get_io_direction(v_props, argname)
      inst.append(f'  .{argname}({wirename}_{direction}),')

  # passing wires
  passing_streams = pw_map.get('passing_streams', {})
  for name, props in passing_streams.items():
    s1 = props['inbound_side_suffix']
    s2 = props['outbound_side_suffix']
    for wire_name in props['wire_to_width'].keys():
      s1_direction = get_io_direction(v_props, f'{wire_name}_{s1}')
      s2_direction = get_io_direction(v_props, f'{wire_name}_{s2}')
      inst.append(f'  .{wire_name}_{s1}({wire_name}_{s1}_{s1_direction}),')
      inst.append(f'  .{wire_name}_{s2}({wire_name}_{s2}_{s2_direction}),')

  if v_props['category'] != 'CTRL_WRAPPER':
    inst.append(f'  .ap_start(ap_start_{v_props["instance"]}_input),')
    inst.append(f'  .ap_done(ap_done_{v_props["instance"]}_output),')
    inst.append(f'  .ap_ready(),')
    inst.append(f'  .ap_idle(),')
    inst.append(f'  .ap_rst_n(ap_rst_n_{v_props["instance"]}_input),')
  else:
    # top level IO
    inst.append(f'  .ap_rst_n(ap_rst_n),')

  # top level IO
  inst.append(f'  .ap_clk(ap_clk)')
  inst.append(f');')

  return inst


def get_task_vertex_insts(config: Dict, use_anchor_wrapper: bool) -> List[str]:
  """Skip ctrl vertex and other conceptual vertices like port vertices"""
  insts = []

  for v_name, v_props in config['vertices'].items():
    if v_props['category'] == 'PORT_VERTEX':
      continue

    elif v_props['category'] == 'CTRL_VERTEX':
      continue

    else:
      module_name_suffix = ANCHOR_WRAPPER_SUFFIX if use_anchor_wrapper else ''
      insts += get_slot_inst(v_props, module_name_suffix) + ['']

  return insts


def get_anchor_reg_decl(config: Dict) -> List[str]:
  """Instantiate the wires between instances and the control signals"""
  wire = []
  for name, width in config['wire_decl'].items():
    wire.append(f'wire {width} {name}_input;')
    wire.append(f'wire {width} {name}_output;')
    wire.append(f'(* dont_touch = "yes" *) reg {width} {name}_q;')
    wire.append(f'always @ (posedge ap_clk) {name}_q <= {name}_output;')
    wire.append(f'assign {name}_input = {name}_q;')

  return wire


def get_io_section(config: Dict, top_name: str) -> List[str]:
  """Get the top-level IOs"""
  io = []
  io.append('`timescale 1 ns / 1 ps')
  io.append('')

  io.append(f'module {top_name} (')
  for name, width in config['input_decl'].items():
    io.append(f'  {name},')

  for name, width in config['output_decl'].items():
    io.append(f'  {name},')

  io[-1] = io[-1].strip(',')
  io.append(');')
  io.append('')

  for name, val in config['parameter_decl'].items():
    io.append(f'parameter {name} = {val};')
  io.append('')

  for name, width in config['input_decl'].items():
    io.append(f'input {width} {name};')

  for name, width in config['output_decl'].items():
    io.append(f'output {width} {name};')

  return io


def set_unused_ports() -> List[str]:
  warning = '  // FIXME: only tested on 2021.2'
  return [
    'assign interrupt = 0;' + warning,
    'assign ap_local_block = 0;' + warning,
  ]


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


def get_top(config: Dict, top_name: str, use_anchor_wrapper: bool) -> List[str]:
  top = []
  top += get_anchor_reg_decl(config) + ['']
  top += get_task_vertex_insts(config, use_anchor_wrapper) + ['']
  top += set_unused_ports()
  top += get_ending() + ['']
  top_sorted = sort_rtl(top)

  top = get_io_section(config, top_name) + [''] + top_sorted + ['']

  return top
