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
  _logger.debug('generating the IO section of vertex %s', props['module'])

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


def get_passing_constant_pipelines(props: Dict) -> List[str]:
  pp = []
  pp.append('')
  pp.append('// handle passing constants')

  passing_constants = props['port_wire_map'].get('passing_constants', [])
  for pc in passing_constants:
    pp.append(f'reg {pc["input"]}_reg;')
    pp.append(f'always @ (posedge ap_clk) {pc["input"]}_reg <= {pc["input"]};')
    pp.append(f'assign {pc["output"]} = {pc["input"]}_reg;')

  return pp


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


def get_non_ctrl_wrapper_ctrl_signals(props: Dict, is_initial_wrapper: True) -> List[str]:
  """Note that we need to skip the ap_done of detached tasks"""
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
  decl.append(f'(* keep = "true" *) reg ap_done_final_q0;')
  decl.append(f'(* keep = "true" *) reg ap_done_final;')
  ap_done_list = []
  for v_props in props['sub_vertices'].values():
    # do not collect ap_done for detached tasks
    if is_initial_wrapper and v_props['is_detached']:
      continue

    done_signal = f'ap_done_{v_props["instance"]}_q0'

    decl.append(f'wire ap_done_{v_props["instance"]};')
    decl.append(f'(* keep = "true" *) reg {done_signal};')
    decl.append(f'always @ (posedge ap_clk) begin')
    decl.append(f'  if (~ap_rst_n_{v_props["instance"]}) {done_signal} <= 0;')
    decl.append(f'  else if (ap_done_final) {done_signal} <= 0;')
    decl.append(f'  else {done_signal} <= {done_signal} | ap_done_{v_props["instance"]};')
    decl.append(f'end')

    ap_done_list.append(done_signal)

  decl.append('always @ (posedge ap_clk) ap_done_final_q0 <= 1 ' +
                ' '.join(f'& {done}' for done in ap_done_list) + ';')

  decl.append(f'(* keep = "true" *) reg ap_rst_n_q0;')
  decl.append(f'always @ (posedge ap_clk) ap_rst_n_q0 <= ap_rst_n;')

  decl.append(f'always @ (posedge ap_clk) begin')
  decl.append(f'  if (~ap_rst_n_q0) ap_done_final <= 0;')
  decl.append(f'  else ap_done_final <= ap_done_final_q0;')
  decl.append(f'end')
  decl.append('assign ap_done = ap_done_final;')

  decl.append('')

  return decl


def get_sub_vertex_insts(props: Dict, is_initial_wrapper: bool) -> List[str]:
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

        # connect the peek port empty_n and _dout
        # should only works on the RTL gen of wrappers around native tasks
        # consider two cases: either the port ends with _s_empty_n or _empty_n
        if is_initial_wrapper:
          if stream_port.endswith(('_empty_n', '_dout')):
            if stream_port.endswith(('_s_empty_n', '_s_dout')):
              peek_port = stream_port.replace('_s_empty_n', '_peek_empty_n').replace('_s_dout', '_peek_dout')
            else:
              peek_port = stream_port.replace('_empty_n', '_peek_empty_n').replace('_dout', '_peek_dout')

            insts.append(f'  .{peek_port}({stream_wire}),')
            _logger.debug('create peek port %s on %s', peek_port, v_props["instance"])

    for axi_entry in pw_map['axi_ports']:
      axi_port_name = axi_entry['portname']
      axi_wire_name = axi_entry['argname']

      assert axi_entry['axi_type'] == 'M_AXI'
      axi_width = axi_entry['data_width']
      for suffix, props in get_m_axi_interface(axi_width).items():
        # e.g., ".m_axi_mmap_ARADDR(m_axi_a_ARADDR),"
        insts.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{axi_wire_name}_{suffix}),')

    passing_streams = pw_map.get('passing_streams', {})
    for name, props in passing_streams.items():
      s1 = props['inbound_side_suffix']
      s2 = props['outbound_side_suffix']
      for wire_name in props['wire_to_width'].keys():
        insts.append(f'  .{wire_name}_{s1}({wire_name}_{s1}),')
        insts.append(f'  .{wire_name}_{s2}({wire_name}_{s2}),')

    if is_initial_wrapper and v_props['is_detached']:
      insts.append(f'  .ap_done(),  // detached module')
    else:
      insts.append(f'  .ap_done(ap_done_{v_props["instance"]}),')

    insts.append(f'  .ap_start(ap_start_{v_props["instance"]}),')
    insts.append(f'  .ap_idle(),')
    insts.append(f'  .ap_ready(),')
    insts.append(f'  .ap_clk(ap_clk),')
    insts.append(f'  .ap_rst_n(ap_rst_n_{v_props["instance"]})')
    insts.append(');')
    insts.append('')

  return insts


def get_sub_stream_insts(props: Dict, use_anchor_wrapper: bool) -> List[str]:
  """anchor_num_per_crossing should synchronize with anchor wrapper generation"""
  insts = []

  for s_name, s_props in props['sub_streams'].items():
    if use_anchor_wrapper:
      # will wrap around each final island with one layer of registering
      # thus each island crossing involves three anchors, one in the anchor region
      # one each in the two islands on the two sides
      # 1 more latency for the actual FIFO
      anchor_num_per_crossing = 3
    else:
      # only put one anchor register in the anchor region
      anchor_num_per_crossing = 1

    pipeline_level = (len(s_props['path']) - 1) * anchor_num_per_crossing + 1
    width = s_props["width"]

    # need to pipeline the signal going in & out
    grace_period = pipeline_level * 2
    orig_depth = s_props["adjusted_depth"] + grace_period

    # round depth to 32s as the area will be the same
    depth = (int(orig_depth/32)+1) * 32
    _logger.debug('fifo %s is pushed from depth %d to %d', s_name, orig_depth, depth)

    addr_width = int(log2(depth)) + 1

    fifo_type = 'fifo' if pipeline_level == 1 else 'fifo_almost_full'

    insts.append(f'{fifo_type} #(')
    insts.append(f'  .DATA_WIDTH({width}),')
    insts.append(f'  .DEPTH({depth}),')
    insts.append(f'  .ADDR_WIDTH({addr_width})')

    if pipeline_level > 1:
      insts[-1] += ','
      insts.append(f'  .GRACE_PERIOD({grace_period})')

    _logger.debug('stream %s has %d cycles of extra latency due to pipelining', s_name, pipeline_level-1)

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
  use_anchor_wrapper: bool,
  is_initial_wrapper: bool,
) -> List[str]:
  """Create the RTL for the specified Vertex
     If the wrapper is around native task modules, set the is_initial_wrapper to be true.
     Then the codegen will reinstate the peek ports.
     If the wrapper is around other wrappers, set the is_initial_wrapper to be false,
     so that the peek ports will be pruned to avoid unnecessary anchors
     use_anchor_wrapper: the latency of a stream is affected by the number of anchors.
  """

  wrapper = []
  wrapper += get_io_section(group_vertex_props)
  wrapper += get_wire_decls(group_vertex_props)
  wrapper += get_passing_wire_pipelines(group_vertex_props)
  wrapper += get_passing_constant_pipelines(group_vertex_props)
  wrapper += get_non_ctrl_wrapper_ctrl_signals(group_vertex_props, is_initial_wrapper)
  wrapper += get_sub_vertex_insts(group_vertex_props, is_initial_wrapper)
  wrapper += get_sub_stream_insts(group_vertex_props, use_anchor_wrapper)
  wrapper += get_ending()

  return wrapper
