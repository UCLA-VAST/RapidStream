import logging
from typing import Dict, List

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def get_ctrl_inst(config: Dict) -> List[str]:
  """the s_axi_control instance"""
  inst = []

  # additional decl for signals used by the ctrl instance
  inst.append('reg ap_rst_ctrl_s_axi;')
  inst.append('always @ (posedge ap_clk) ap_rst_ctrl_s_axi <= ~ap_rst_n;')
  inst.append('wire ap_start_orig;')
  inst.append('wire ap_idle_final;')
  inst.append('wire ap_ready_final;')
  inst.append('assign ap_idle_final = ap_done_final;')
  inst.append('assign ap_ready_final = ap_done_final;')

  v_props = config['vertices']['CTRL_VERTEX_control_s_axi']
  inst.append(f'{v_props["module"]} #(')

  # parameters of the instance
  for paramname, argname in v_props['param_map'].items():
    inst.append(f'  .{paramname}({argname}),')
  inst[-1] = inst[-1].strip(',')

  # ports of the instance
  inst.append(f') {v_props["module"]}_0 (')

  for portname in v_props['port_wire_map']['axi_ports'].keys():
    inst.append(f'  .{portname}(s_axi_control_{portname}),')

  for portname, argname in v_props['port_wire_map']['constant_ports'].items():
    inst.append(f'  .{portname}({argname}),')

  # basic ports
  inst.append(f'  .ACLK(ap_clk),')
  inst.append(f'  .ARESET(ap_rst_ctrl_s_axi),')
  inst.append(f'  .ACLK_EN(1\'b1),')
  inst.append(f'  .interrupt(interrupt),')

  # sync here with wire declaration
  inst.append(f'  .ap_start(ap_start_orig),')
  inst.append(f'  .ap_done(ap_done_final),')
  inst.append(f'  .ap_idle(ap_idle_final),')
  inst.append(f'  .ap_ready(ap_ready_final),')

  inst[-1] = inst[-1].strip(',')
  inst.append(');')

  return inst


def get_slot_inst(v_props: Dict) -> List[str]:
  """the instance for each slot"""
  inst = []
  pw_map = v_props['port_wire_map']

  inst.append(f'{v_props["module"]} {v_props["module"]}_0(')

  # FIXME: consider readonly/writeonly cases
  for axi_entry in pw_map['axi_ports']:
    axi_port_name = axi_entry['portname']
    wirename = axi_entry['argname']
    for suffix in AXI_INTERFACE.keys():
      inst.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{wirename}_{suffix}),')

  for argname, wirename in pw_map['constant_ports'].items():
    inst.append(f'  .{argname}({wirename}),')

  for stream_pw_map in pw_map['stream_ports'].values():
    for argname, wirename in stream_pw_map.items():
      inst.append(f'  .{argname}({wirename}),')

  inst.append(f'  .ap_clk(ap_clk),')
  inst.append(f'  .ap_rst_n(ap_rst_n_{v_props["module"]}_0),')
  inst.append(f'  .ap_start(ap_start_{v_props["module"]}_0),')
  inst.append(f'  .ap_done(ap_done_{v_props["module"]}_0),')
  inst.append(f'  .ap_ready(),')
  inst.append(f'  .ap_idle()')
  inst.append(f');')

  return inst


def get_task_vertex_insts(config: Dict) -> List[str]:
  """Skip ctrl vertex and other conceptual vertices like port vertices"""
  insts = []

  for v_name, v_props in config['vertices'].items():
    if v_props['category'] == 'PORT_VERTEX':
      continue

    elif v_props['category'] == 'CTRL_VERTEX':
      continue

    else:
      insts += get_slot_inst(v_props) + ['']

  return insts


def get_wire_decl(config: Dict) -> List[str]:
  """Instantiate the wires between instances and the control signals"""
  wire = [f'wire {width} {name};'
            for name, width in config['wire_decl'].items()]
  return wire



def get_ctrl_signals(config: Dict) -> List[str]:
  """Broadcast ap_start and reduce ap_done"""
  decl = []

  decl.append('// declare control signals')
  # distribute ap_rst_n
  for v_props in config['vertices'].values():
    cat = v_props['category']
    if cat == 'PORT_VERTEX':
      continue
    elif cat == 'CTRL_VERTEX':
      decl.append(f'(* keep = "true" *) reg ap_rst_{v_props["instance"]};')
      decl.append(f'always @ (posedge ap_clk) ap_rst_{v_props["instance"]} <= ~ap_rst_n;')
    else:
      decl.append(f'(* keep = "true" *) reg ap_rst_n_{v_props["instance"]};')
      decl.append(f'always @ (posedge ap_clk) ap_rst_n_{v_props["instance"]} <= ap_rst_n;')

  # distribute ap_start
  decl.append(f'(* keep = "true" *) reg ap_start_q0;')
  decl.append('always @ (posedge ap_clk) ap_start_q0 <= ap_start_orig;')
  for v_props in config['vertices'].values():
    if v_props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue

    decl.append(f'(* keep = "true" *) reg ap_start_{v_props["instance"]};')
    decl.append(f'always @ (posedge ap_clk) ap_start_{v_props["instance"]} <= ap_start_q0;')

  # collect ap_done
  # each vertex will only assert ap_done for one cycle, so we need to hold the value
  # after all vertices have finished, reset the ap_done hold registers
  # FIXME: need to exclude detached vertices
  decl.append(f'(* keep = "true" *) reg ap_done_final_q0;')
  decl.append(f'(* keep = "true" *) reg ap_done_final;')
  for v_props in config['vertices'].values():
    if v_props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue

    decl.append(f'wire ap_done_{v_props["instance"]};')
    decl.append(f'(* keep = "true" *) reg ap_done_{v_props["instance"]}_q0;')
    decl.append(f'always @ (posedge ap_clk) begin')
    decl.append(f'  if (~ap_rst_n_{v_props["instance"]}) ap_done_{v_props["instance"]}_q0 <= 0;')
    decl.append(f'  else if (ap_done_final) ap_done_{v_props["instance"]}_q0 <= 0;')
    decl.append(f'  else ap_done_{v_props["instance"]}_q0 <= ap_done_{v_props["instance"]}_q0 | ap_done_{v_props["instance"]};')
    decl.append(f'end')

  reduce = 'always @ (posedge ap_clk) ap_done_final_q0 <= 1\'b1'
  for v_props in config['vertices'].values():
    if v_props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue
    reduce += f' & ap_done_{v_props["instance"]}_q0'
  reduce += ';'
  decl.append(reduce)

  decl.append(f'(* keep = "true" *) reg ap_rst_n_q0;')
  decl.append(f'always @ (posedge ap_clk) ap_rst_n_q0 <= ap_rst_n;')

  decl.append(f'always @ (posedge ap_clk) begin')
  decl.append(f'  if (~ap_rst_n_q0) ap_done_final <= 0;')
  decl.append(f'  else ap_done_final <= ap_done_final_q0;')
  decl.append(f'end')
  decl.append('assign ap_done = ap_done_final;')

  decl.append('')

  return decl


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


def get_top(config: Dict, top_name: str) -> List[str]:
  top = []
  top += get_wire_decl(config) + ['']
  top += get_ctrl_signals(config) + ['']
  top += get_ctrl_inst(config) + ['']
  top += get_task_vertex_insts(config) + ['']
  top += get_ending() + ['']
  top_sorted = sort_rtl(top)

  top = get_io_section(config, top_name) + [''] + top_sorted + ['']

  return top
