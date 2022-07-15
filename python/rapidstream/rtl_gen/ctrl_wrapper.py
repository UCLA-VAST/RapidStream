import logging
from re import L
from typing import Dict, List

from rapidstream.const import *
from rapidstream.rtl_gen.group_wrapper import (
  get_io_section,
  get_ending,
  get_passing_wire_pipelines,
  get_sub_stream_insts,
  get_sub_vertex_insts,
  get_wire_decls,
)

_logger = logging.getLogger().getChild(__name__)


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


def get_basic_io() -> List[str]:
  io = []
  io.append('input ap_clk,')
  io.append('input ap_rst_n,')
  return io


def get_master_ctrl_signals_io(props: Dict) -> List[str]:
  io = []
  port_wire_map = props['port_wire_map']
  for ap_out in port_wire_map['ctrl_out']:
    io.append(f'output {ap_out},')

  for ap_out in port_wire_map['reset_out']:
    io.append(f'output {ap_out},')

  for ap_in in port_wire_map['ctrl_in']:
    io.append(f'input {ap_in},')

  return io


def get_constant_output_io(props: Dict) -> List[str]:
  io = []
  port_wire_map = props['port_wire_map']
  for c_out in port_wire_map['constant_out'].keys():
    width = props['port_width_map'][c_out]
    io.append(f'output {width} {c_out},')

  return io


def get_s_axi_lite_io(props: Dict) -> List[str]:
  io = []
  port_wire_map = props['port_wire_map']

  for axi_entry in port_wire_map['axi_ports']:
    if axi_entry['axi_type'] == 'S_AXI_LITE':
      for portname, dir_and_width in S_AXI_LITE_INTERFACE.items():
        io.append(f'{dir_and_width[0]} {dir_and_width[1]} s_axi_control_{portname},')

  return io


def get_ctrl_signals(props: Dict) -> List[str]:
  """
  The ctrl wrapper include the ctrl vertex and one normal vertex
  We need to send ctrl signals to the outside as well as to the
  normal vertex within the wrapper
  """
  rtl = []

  # broadcast ap_start to outside
  for ap_out in props['port_wire_map']['ctrl_out']:
    rtl.append(f'reg {ap_out}_q;')
    rtl.append(f'always @ (posedge ap_clk) {ap_out}_q <= ap_start_orig;')
    rtl.append(f'assign {ap_out} = {ap_out}_q;')

  # broadcast ap_rst_n
  for ap_out in props['port_wire_map']['reset_out']:
    rtl.append(f'reg {ap_out}_q;')
    rtl.append(f'always @ (posedge ap_clk) {ap_out}_q <= ap_rst_n;')
    rtl.append(f'assign {ap_out} = {ap_out}_q;')

  # reduce ap_done from outside
  rtl.append(f'reg ap_done_final_q;')
  for ap_in in props['port_wire_map']['ctrl_in']:
    rtl.append(f'reg {ap_in}_q;')
    rtl.append(f'always @ (posedge ap_clk) begin')
    rtl.append(f'  if (~ap_rst_n) {ap_in}_q <= 0;')
    rtl.append(f'  else if (ap_done_final_q) {ap_in}_q <= 0;')
    rtl.append(f'  else {ap_in}_q <= {ap_in} | {ap_in}_q ;')
    rtl.append(f'end')

  # send ap_start to the normal vertex within the wrapper
  wrapper_sub_vertex = props['wrapper_sub_vertex']
  rtl.append(f'wire ap_start_{wrapper_sub_vertex};')
  rtl.append(f'reg ap_start_{wrapper_sub_vertex}_q;')
  rtl.append(f'always @ (posedge ap_clk) ap_start_{wrapper_sub_vertex}_q <= ap_start_orig;')
  rtl.append(f'assign ap_start_{wrapper_sub_vertex} = ap_start_{wrapper_sub_vertex}_q;')

  # get the ap_done from the normal vertex within the wrapper
  rtl.append(f'reg ap_done_{wrapper_sub_vertex}_q;')
  rtl.append(f'wire ap_done_{wrapper_sub_vertex};')
  rtl.append(f'always @ (posedge ap_clk) begin')
  rtl.append(f'  if (~ap_rst_n) ap_done_{wrapper_sub_vertex}_q <= 0;')
  rtl.append(f'  else if (ap_done_final_q) ap_done_{wrapper_sub_vertex}_q <= 0;')
  rtl.append(f'  else ap_done_{wrapper_sub_vertex}_q <= ap_done_{wrapper_sub_vertex} | ap_done_{wrapper_sub_vertex}_q;')
  rtl.append(f'end')

  rtl.append(f'always @ (posedge ap_clk) ap_done_final_q <= 1 & ' +
    ' & '.join(f'{ap_in}_q' for ap_in in props['port_wire_map']['ctrl_in']) +
    f' & ap_done_{wrapper_sub_vertex}_q' +
    ';'
  )
  rtl.append(f'assign ap_done_final = ap_done_final_q;')

  # reset signal for the vertex
  rtl.append(f'reg ap_rst_n_{wrapper_sub_vertex}_q;')
  rtl.append(f'wire ap_rst_n_{wrapper_sub_vertex};')
  rtl.append(f'always @ (posedge ap_clk) ap_rst_n_{wrapper_sub_vertex}_q <= ap_rst_n;')
  rtl.append(f'assign ap_rst_n_{wrapper_sub_vertex} = ap_rst_n_{wrapper_sub_vertex}_q;')

  return rtl


def get_constant_broadcast(v_props: Dict) -> List[str]:
  """Register the constant from ctrl unit before broadcasting"""
  rtl = []

  for portname, argname in v_props['port_wire_map']['constant_ports'].items():
    width = v_props['port_width_map'][portname]
    # argname is already defined as output port
    # if the inner vertex also uses this constant
    # we need to additionally define it as wire
    rtl.append(f'wire {width} {argname};')

    rtl.append(f'wire {width} {argname}_inner;')
    rtl.append(f'reg  {width} {argname}_q;')
    rtl.append(f'always @ (posedge ap_clk) {argname}_q <= {argname}_inner;')
    rtl.append(f'assign {argname} = {argname}_q;')
    rtl.append('')

  return rtl


def get_ctrl_sub_vertex_inst(v_props: Dict) -> List[str]:
  """the s_axi_control instance"""
  inst = []

  # additional decl for signals used by the ctrl instance
  inst.append('reg ap_rst_ctrl_s_axi;')
  inst.append('always @ (posedge ap_clk) ap_rst_ctrl_s_axi <= ~ap_rst_n;')
  inst.append('wire ap_idle_final;')
  inst.append('wire ap_ready_final;')
  inst.append('assign ap_idle_final = ap_done_final;')
  inst.append('assign ap_ready_final = ap_done_final;')

  inst.append(f'{v_props["module"]} #(')

  # FIXME: hardcoded parameters of the instance
  inst.append(f'  .C_S_AXI_ADDR_WIDTH({C_S_AXI_ADDR_WIDTH}),')
  inst.append(f'  .C_S_AXI_DATA_WIDTH({C_S_AXI_DATA_WIDTH})')

  # ports of the instance
  inst.append(f') {v_props["module"]}_0 (')

  # FIXME: hard code s_axi_control interface
  for suffix in S_AXI_LITE_INTERFACE.keys():
    inst.append(f'  .{suffix}(s_axi_control_{suffix}),')

  # register the constants once
  for portname, argname in v_props['port_wire_map']['constant_ports'].items():
    inst.append(f'  .{portname}({argname}_inner),')

  # basic ports
  inst.append(f'  .ACLK(ap_clk),')
  inst.append(f'  .ARESET(ap_rst_ctrl_s_axi),')
  inst.append(f'  .ACLK_EN(1\'b1),')
  inst.append(f'  .interrupt(),')

  # sync here with wire declaration
  inst.append(f'  .ap_start(ap_start_orig),')
  inst.append(f'  .ap_done(ap_done_final),')
  inst.append(f'  .ap_idle(ap_idle_final),')
  inst.append(f'  .ap_ready(ap_ready_final),')

  inst[-1] = inst[-1].strip(',')
  inst.append(');')

  return inst


def get_ctrl_wrapper(ctrl_wrapper_props: Dict, use_anchor_wrapper: bool) -> List[str]:
  """Create the RTL for the vertex with the ctrl unit in it"""

  wrapper = []
  wrapper += get_wire_decls(ctrl_wrapper_props)
  wrapper += get_passing_wire_pipelines(ctrl_wrapper_props)
  wrapper += get_ctrl_signals(ctrl_wrapper_props)
  wrapper += get_sub_vertex_insts(ctrl_wrapper_props, is_initial_wrapper=False)
  wrapper += get_sub_stream_insts(ctrl_wrapper_props, use_anchor_wrapper)

  ctrl_sub_vertex_name = ctrl_wrapper_props['ctrl_sub_vertex']
  ctrl_sub_vertex_props = ctrl_wrapper_props['sub_vertices'][ctrl_sub_vertex_name]
  wrapper += get_constant_broadcast(ctrl_sub_vertex_props)
  wrapper += get_ctrl_sub_vertex_inst(ctrl_sub_vertex_props)

  wrapper += get_ending()

  # push all wire/reg declaration to the front
  wrapper = sort_rtl(wrapper)

  # add the header after sorting
  wrapper = get_io_section(ctrl_wrapper_props) + wrapper

  return wrapper
