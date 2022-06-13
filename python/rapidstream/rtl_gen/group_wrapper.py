import logging
from math import log2
from typing import Dict, List

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def get_io_section(props: Dict) -> List[str]:
  """Get the Input/Output part"""
  _logger.info('generating RTL for %s', props['module'])

  io = []

  port_wire_map = props['port_wire_map']

  for const_io in port_wire_map['constant_ports']:
    const_width = props['port_width_map'][const_io]
    io.append(f'input {const_width} {const_io},')

  for stream_name, _port_wire_map in port_wire_map['stream_ports'].items():
    if stream_name in props['inbound_streams']:
      _logger.debug('%s is an inbound stream', stream_name)
      stream_dir = 'INBOUND'
    elif stream_name in props['outbound_streams']:
      _logger.debug('%s is an outbound stream', stream_name)
      stream_dir = 'OUTBOUND'
    else:
      stream_dir = 'OUTBOUND'
      _logger.error('direction of stream %s is unknown', stream_name)
      exit(1)

    for port in _port_wire_map.keys():
      port_width = props['port_width_map'].get(port, '')

      # the direction of the ports are determined by if the FIFO is inside
      # or outside the wrapper
      if port.endswith(('_din', '_write', '_full_n')):
        if stream_dir == 'OUTBOUND':
          if port.endswith(('_din', '_write')):
            direction = 'output'
          else:
            direction = 'input'
        else:
          if port.endswith(('_din', '_write')):
            direction = 'input'
          else:
            direction = 'output'

      elif port.endswith(('_dout', '_read', '_empty_n')):
        if stream_dir == 'OUTBOUND':
          if port.endswith(('_dout', '_empty_n')):
            direction = 'output'
          else:
            direction = 'input'
        else:
          if port.endswith(('_dout', '_empty_n')):
            direction = 'input'
          else:
            direction = 'output'
      else:
        assert False

      io.append(f'{direction} {port_width} {port},')

  for axi_entry in port_wire_map['axi_ports']:
    axi_data_width = axi_entry['data_width']
    axi_port_name = axi_entry['portname']
    io += get_axi_io_section(axi_data_width, axi_port_name)

  # ctrl signals
  io.append(f'input ap_clk,')
  io.append(f'input ap_rst_n,')
  io.append(f'input ap_start,')
  io.append(f'output ap_done,')
  io.append(f'output ap_idle,')
  io.append(f'output ap_ready') # the last IO, no "," at the end

  io = ['  ' + line for line in io]
  io = [f'module {props["module"]} ('] + io
  io = ['`timescale 1 ns / 1 ps'] + io
  io += [');']

  return io


def get_wire_decls(props: Dict) -> List[str]:
  """Instantiate the wires between instances and the control signals"""
  wire = [f'  wire {width} {name};'
            for name, width in props['wire_decl'].items()]
  return wire


def get_ctrl_signals(props: Dict) -> List[str]:
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
    insts.append(f'{v_props["module"]} {v_props["module"]}_0 (')

    pw_map = v_props['port_wire_map']
    for const_port, const_wire in pw_map['constant_ports'].items():
      insts.append(f'  .{const_port}({const_wire}),')

    for stream_props in pw_map['stream_ports'].values():
      for stream_port, stream_wire in stream_props.items():
        insts.append(f'  .{stream_port}({stream_wire}),')

    for axi_entry in pw_map['axi_ports']:
      axi_port_name = axi_entry['portname']
      axi_wire_name = axi_entry['argname']
      for suffix, props in AXI_INTERFACE.items():
        insts.append(f'  .m_axi_{axi_port_name}_{suffix}(m_axi_{axi_wire_name}_{suffix}),')

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
    pipeline_level = (len(s_props['path']) - 1)
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
  wrapper += get_ctrl_signals(group_vertex_props)
  wrapper += get_sub_vertex_insts(group_vertex_props)
  wrapper += get_sub_stream_insts(group_vertex_props)
  wrapper += get_ending()

  return wrapper
