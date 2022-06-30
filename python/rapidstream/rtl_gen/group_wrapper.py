import logging
import re
from math import log2
from typing import Dict, List

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def remove_trailing_comma(rtl: List[str]) -> List[str]:
  rtl[-1] = rtl[-1].strip(',')
  return rtl


def format_io_section(io: List[str], props: Dict, suffix: str = '') -> List[str]:
  io = ['  ' + line for line in io]
  io = [f'module {props["module"]}{suffix} ('] + io
  io = ['`timescale 1 ns / 1 ps'] + io
  io += [');']

  return io


def get_io_section(props: Dict, suffix: str = '') -> List[str]:
  """Get the Input/Output part"""
  _logger.info('generating RTL for non-ctrl wrapper %s', props['module'])

  io = []
  for io_dir, name_to_width in props['io_dir_to_name_to_width'].items():
    for name, width in name_to_width.items():
      io.append(f'{io_dir} {width} {name},')

  io = remove_trailing_comma(io)
  io = format_io_section(io, props, suffix)

  return io


def get_wire_decls(props: Dict) -> List[str]:
  """Instantiate the wires between instances and the control signals"""
  wire = [f'  wire {width} {name};'
            for name, width in props['wire_decl'].items()]
  return wire


def get_passing_wire_pipelines(props: Dict) -> List[str]:
  pp = []
  pp.append('')
  pp.append('// handle passing streams')

  passing_streams = props['port_wire_map'].get('passing_streams', {})
  for name, props in passing_streams.items():
    s_in = props['inbound_side_suffix']
    s_out = props['outbound_side_suffix']
    pp_level = props['pipeline_level']
    for wire_name, width in props['wire_to_width'].items():
      for i in range(pp_level):
        pp.append(f'reg {width} {wire_name}_pipeline_q{i};')

      # declare the pipeline
      for i in range(1, pp_level):
        pp.append(f'always @ (posedge ap_clk) {wire_name}_pipeline_q{i} <= {wire_name}_pipeline_q{i-1};')

      # handle the head and tail
      if pp_level > 0:
        if wire_name.endswith(('_din', '_write')):
          pp.append(f'always @ (posedge ap_clk) {wire_name}_pipeline_q0 <= {wire_name}_{s_in};')
          pp.append(f'assign {wire_name}_{s_out} = {wire_name}_pipeline_q{pp_level-1};')
        elif wire_name.endswith('_full_n'):
          pp.append(f'always @ (posedge ap_clk) {wire_name}_pipeline_q0 <= {wire_name}_{s_out};')
          pp.append(f'assign {wire_name}_{s_in} = {wire_name}_pipeline_q{pp_level-1};')
        else:
          assert False
      else:
        if wire_name.endswith(('_din', '_write')):
          pp.append(f'assign {wire_name}_{s_out} = {wire_name}_{s_in};')
        elif wire_name.endswith('_full_n'):
          pp.append(f'assign {wire_name}_{s_in} = {wire_name}_{s_out};')
        else:
          assert False

  pp.append('')
  return pp


def get_non_ctrl_wrapper_ctrl_signals(props: Dict) -> List[str]:
  decl = []

  # distribute ap_rst_n
  for v_props in props['sub_vertices'].values():
    decl.append(f'(* keep = "true" *) reg ap_rst_n_{v_props["instance"]};')
    decl.append(f'always @ (posedge ap_clk) ap_rst_n_{v_props["instance"]} <= ap_rst_n;')
  for s_name in props['sub_streams'].keys():
    decl.append(f'(* keep = "true" *) reg ap_rst_n_{s_name};')
    decl.append(f'always @ (posedge ap_clk) ap_rst_n_{s_name} <= ap_rst_n;')

  # distribute ap_start
  decl.append(f'(* keep = "true" *) reg ap_start_q0;')
  decl.append('always @ (posedge ap_clk) ap_start_q0 <= ap_start;')
  for v_props in props['sub_vertices'].values():
    decl.append(f'(* keep = "true" *) reg ap_start_{v_props["instance"]};')
    decl.append(f'always @ (posedge ap_clk) ap_start_{v_props["instance"]} <= ap_start_q0;')

  # collect ap_done
  # each vertex will only assert ap_done for one cycle, so we need to hold the value
  # after all vertices have finished, reset the ap_done hold registers
  # FIXME: need to exclude detached vertices
  decl.append(f'(* keep = "true" *) reg ap_done_final_q0;')
  decl.append(f'(* keep = "true" *) reg ap_done_final;')
  for v_props in props['sub_vertices'].values():
    done_signal = f'ap_done_{v_props["instance"]}_q0'

    decl.append(f'wire ap_done_{v_props["instance"]};')
    decl.append(f'(* keep = "true" *) reg {done_signal};')
    decl.append(f'always @ (posedge ap_clk) begin')
    decl.append(f'  if (~ap_rst_n_{v_props["instance"]}) {done_signal} <= 0;')
    decl.append(f'  else if (ap_done_final) {done_signal} <= 0;')
    decl.append(f'  else {done_signal} <= {done_signal} | ap_done_{v_props["instance"]};')
    decl.append(f'end')

  decl.append('always @ (posedge ap_clk) ap_done_final_q0 <= ' +
                ' & '.join(f'ap_done_{v_props["instance"]}_q0'
                  for v_props in props['sub_vertices'].values()) + ';'
             )

  decl.append(f'(* keep = "true" *) reg ap_rst_n_q0;')
  decl.append(f'always @ (posedge ap_clk) ap_rst_n_q0 <= ap_rst_n;')

  decl.append(f'always @ (posedge ap_clk) begin')
  decl.append(f'  if (~ap_rst_n_q0) ap_done_final <= 0;')
  decl.append(f'  else ap_done_final <= ap_done_final_q0;')
  decl.append(f'end')
  decl.append('assign ap_done = ap_done_final;')

  decl.append('')

  return decl


def get_sub_vertex_insts(props: Dict) -> List[str]:
  insts = []

  for v_name, v_props in props['sub_vertices'].items():
    if v_props['category'] in ('PORT_VERTEX', 'CTRL_VERTEX'):
      continue

    insts.append(f'{v_props["module"]}')

    if 'param_map' in v_props:
      insts.append(f'#(')
      for param, val in v_props['param_map'].items():
        insts.append(f'  .{param}({val}),')
      insts[-1] = insts[-1].strip(',')
      insts.append(')')

    insts.append(f'{v_props["instance"]} (')

    pw_map = v_props['port_wire_map']
    for const_port, const_wire in pw_map['constant_ports'].items():
      insts.append(f'  .{const_port}({const_wire}),')

    for stream_props in pw_map.get('stream_ports', {}).values():
      for stream_port, stream_wire in stream_props.items():
        insts.append(f'  .{stream_port}({stream_wire}),')

    for axi_entry in pw_map['axi_ports']:
      axi_port_name = axi_entry['portname']
      axi_wire_name = axi_entry['argname']

      assert axi_entry['axi_type'] == 'M_AXI'
      for suffix, props in M_AXI_INTERFACE.items():
        # e.g., ".m_axi_mmap_ARADDR(m_axi_a_ARADDR),"
        insts.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{axi_wire_name}_{suffix}),')

    passing_streams = pw_map.get('passing_streams', {})
    for name, props in passing_streams.items():
      s1 = props['inbound_side_suffix']
      s2 = props['outbound_side_suffix']
      for wire_name in props['wire_to_width'].keys():
        insts.append(f'  .{wire_name}_{s1}({wire_name}_{s1}),')
        insts.append(f'  .{wire_name}_{s2}({wire_name}_{s2}),')

    insts.append(f'  .ap_start(ap_start_{v_props["instance"]}),')
    insts.append(f'  .ap_done(ap_done_{v_props["instance"]}),')
    insts.append(f'  .ap_idle(),')
    insts.append(f'  .ap_ready(),')
    insts.append(f'  .ap_clk(ap_clk),')
    insts.append(f'  .ap_rst_n(ap_rst_n_{v_props["instance"]})')
    insts.append(');')
    insts.append('')

  return insts


def get_sub_stream_insts(props: Dict) -> List[str]:
  insts = []

  for s_name, s_props in props['sub_streams'].items():
    pipeline_level = (len(s_props['path']) - 1) * 2
    width = s_props["width"]

    # need to pipeline the signal going in & out
    grace_period = pipeline_level * 2
    depth = s_props["adjusted_depth"] + grace_period
    addr_width = int(log2(depth)) + 1

    fifo_type = 'fifo' if pipeline_level == 1 else 'fifo_almost_full'

    insts.append(f'{fifo_type} #(')
    insts.append(f'  .DATA_WIDTH({width}),')
    insts.append(f'  .DEPTH({depth}),')
    insts.append(f'  .ADDR_WIDTH({addr_width})')

    if pipeline_level > 1:
      insts[-1] += ','
      insts.append(f'  .GRACE_PERIOD({grace_period})')

    _logger.debug('stream %s has pipeline level %d', s_name, pipeline_level)

    insts.append(f') {s_name} (')
    insts.append(f'  .clk(ap_clk),')
    insts.append(f'  .reset(~ap_rst_n_{s_name}),')

    for portname, wirename in s_props['port_wire_map']['inbound'].items():
      insts.append(f'  .{portname}({wirename}),')
    for portname, wirename in s_props['port_wire_map']['outbound'].items():
      insts.append(f'  .{portname}({wirename}),')

    insts.append(f'  .if_read_ce(1\'b1),')
    insts.append(f'  .if_write_ce(1\'b1)')
    insts.append(');')

  return insts


def get_ending() -> List[str]:
  return ['endmodule']


def get_group_wrapper(
  group_vertex_props: Dict,
) -> List[str]:
  """Create the RTL for the specified Vertex"""

  wrapper = []
  wrapper += get_io_section(group_vertex_props)
  wrapper += get_wire_decls(group_vertex_props)
  wrapper += get_passing_wire_pipelines(group_vertex_props)
  wrapper += get_non_ctrl_wrapper_ctrl_signals(group_vertex_props)
  wrapper += get_sub_vertex_insts(group_vertex_props)
  wrapper += get_sub_stream_insts(group_vertex_props)
  wrapper += get_ending()

  return wrapper
