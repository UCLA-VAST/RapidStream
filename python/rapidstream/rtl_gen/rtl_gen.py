import logging
from typing import Dict, List

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def get_io_section(props: Dict) -> List[str]:
  """Get the Input/Output part"""
  io = []

  port_wire_map = props['port_wire_map']

  for const_io in port_wire_map['constant_ports']:
    const_width = props['port_width_map'][const_io]
    io.append(f'input {const_width} {const_io},')

  for stream_name, _port_wire_map in port_wire_map['stream_ports']:
    for port in _port_wire_map.keys():
      port_width = props['port_width_map'].get(port, '')

      if port.endswith(('_din', '_write', 'empty_n')):
        direction = 'output'
      elif port.endswith(('_dout', '_read', 'full_n')):
        direction = 'input'

      io.append(f'{direction} {port_width} {port},')

  for axi_port_name, axi_wire_name in port_wire_map['axi_ports'].items():
    axi_data_width = props['port_width_map'][axi_port_name]
    io += get_axi_io_section(axi_data_width)

  # ctrl signals
  io.append(f'input ap_clk,')
  io.append(f'input ap_rst_n,')
  io.append(f'input ap_start,')
  io.append(f'output ap_done,')
  io.append(f'output ap_idle,')
  io.append(f'output ap_ready') # the last IO, no "," at the end

  return io


def gen_rtl_for_non_top_vertex(
  config: Dict,
  name: str,
  props: Dict,
) -> List[str]:
  """Create the RTL for the specified Vertex"""
  rtl = []

  rtl.append(f'{props["module"]} {props["module"]}_0')
