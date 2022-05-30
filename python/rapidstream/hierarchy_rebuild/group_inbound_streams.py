import logging
from typing import Dict, List, Tuple

_logger = logging.getLogger().getChild(__name__)


def get_group_inner_wire_name_to_width(
  internal_streams: List[str],
  config: Dict,
) -> Dict[str, str]:
  """Get the internal wires of the group vertex"""
  inner_wire_names = []
  for stream in internal_streams:
    inner_wire_names += config['edges'][stream]['port_wire_map']['inbound']
    inner_wire_names += config['edges'][stream]['port_wire_map']['outbound']

  inner_wire_name_to_width = {
    name: config['wire_decl'][name] for name in inner_wire_names
  }

  return inner_wire_name_to_width


def get_group_port_wire_map(
  config: Dict,
  vertex_props: Dict,
) -> Dict[str, str]:
  port_wire_map = {
    'axi_ports': vertex_props['axi_ports'],  # for top level AXI connection
    'ctrl_ports': vertex_props['axi_ports'],  # for ap signals
    'constant_ports': vertex_props['axi_ports'],  # for scalar arguments from s_axi_control,
    'stream_ports': {},  # connect to FIFOs
  }

  # ports associated with outbound streams remain the same
  for stream in vertex_props['outbound_streams']:
    port_wire_map['stream_ports'][stream] = \
      vertex_props['port_wire_map']['stream_ports'][stream]

  # update the ports associated with inbound streams
  for stream in vertex_props['outbound_streams']:
    port_wire_map['stream_ports'][stream] = \
      config['edges'][stream]['port_wire_map']['inbound']

  return port_wire_map


def get_group_vertex_props(
  config: Dict,
) -> Dict:
  """Get the new group vertex including all inbound streams"""



def group_inbound_edges(
  config: Dict,
  target_vertex: str,
) -> None:
  """Create a wrapper to include all inbound streams of an vertex"""
  if target_vertex not in config['vertices']:
    _logger.error('vertex not existing in config')
    exit(1)

  props = config['vertices'][target_vertex]
  in_streams = {name: config['edges'][name] for name in props['inbound_streams']}

  # remove the current vertex
  config['vertices'].pop(target_vertex)

  # remove the inbound streams
  for name in in_streams.keys():
    config['edges'].pop(name)

  # collect and remove the wires between the vertex and the in streams
  target_wires = {}
  for props in in_streams.values():
    for wire in props['port_wire_map']['outbound'].values():
      target_wires[wire] = config['wire_decl'][wire]
      config['wire_decl'].pop(wire)
