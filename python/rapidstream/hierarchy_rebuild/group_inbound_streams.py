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
    # since we only move the inbound streams inside the wrapper
    # only include the wires at the outbound side
    # the wires at the inbound side will connect to the ports of the wrapper
    inner_wire_names += config['edges'][stream]['port_wire_map']['outbound'].values()

  inner_wire_name_to_width = {
    name: config['wire_decl'][name] for name in inner_wire_names
  }

  return inner_wire_name_to_width


def get_group_port_width_map(
  config: Dict,
  vertex_props: Dict,
) -> Dict[str, str]:
  """Must be executed before get_group_port_wire_map"""
  port_width_map = {}

  # axi ports
  for portname, argname in vertex_props['port_wire_map']['axi_ports'].items():
    width = vertex_props['port_width_map'][portname]
    port_width_map[argname] = width

  # outbound stream ports
  for stream in vertex_props['outbound_streams']:
    for portname, argname in vertex_props['port_wire_map']['stream_ports'][stream].items():
      if portname.endswith(('_dout', '_din')):
        port_width_map[argname] = vertex_props['port_width_map'][portname]

  # inbound stream ports
  for stream in vertex_props['inbound_streams']:
    stream_width_int = config['edges'][stream]['width']
    inbound_side_wires = config['edges'][stream]['port_wire_map']['inbound']

    for portname, wirename in inbound_side_wires.items():
      if portname.endswith(('_dout', '_din')):
        port_width_map[wirename] = f'[{stream_width_int-1}:0]'

  # constant ports
  for portname, argname in vertex_props['port_wire_map']['constant_ports'].items():
    width =  vertex_props['port_width_map'][portname]
    port_width_map[argname] = width

  return port_width_map


def get_group_port_wire_map(
  config: Dict,
  vertex_props: Dict,
) -> Dict:
  """vertex_props: the original property of the vertex to be wrapped"""
  port_wire_map = {
    'axi_ports': {
      argname: argname for argname in vertex_props['port_wire_map']['axi_ports'].values()
    },  # for top level AXI connection
    'ctrl_ports': vertex_props['port_wire_map']['ctrl_ports'],  # for ap signals
    'constant_ports': vertex_props['port_wire_map']['constant_ports'],  # for scalar arguments from s_axi_control,
    'stream_ports': {},  # connect to FIFOs
  }

  # ports associated with outbound streams remain the same
  for stream in vertex_props['outbound_streams']:
    port_wire_map['stream_ports'][stream] = \
      vertex_props['port_wire_map']['stream_ports'][stream]

  # update the ports associated with inbound streams
  for stream in vertex_props['inbound_streams']:
    inbound_side_wires = config['edges'][stream]['port_wire_map']['inbound']

    # when we create a new wrapper, the new port is named after
    # the wire that is split into two hiererchies
    port_wire_map['stream_ports'][stream] = {
      wirename: wirename for wirename in inbound_side_wires.values()
    }

  return port_wire_map


def get_group_vertex_props(
  config: Dict,
  target_vertex: str,
) -> Dict:
  """Get the new group vertex including all inbound streams"""
  group_props = {}
  group_props['module'] = None
  group_props['instance'] = None
  group_props['area'] = config['vertices'][target_vertex]['area']
  group_props['category'] = 'INBOUND_STREAM_GROUP_VERTEX',

  group_props['floorplan_region'] = config['vertices'][target_vertex]['floorplan_region']
  group_props['SLR'] = config['vertices'][target_vertex]['SLR']

  group_props['sub_vertices'] = {target_vertex: config['vertices'][target_vertex]}

  group_props['sub_streams'] = {
    name: config['edges'][name] for name in
      config['vertices'][target_vertex]['inbound_streams']
  }

  # we have included all inbound streams inside the vertex
  # now the vertex will connect to other vertices through pure wire
  # for now let's make the inbound_streams property empty
  group_props['inbound_streams'] = []

  group_props['outbound_streams'] = config['vertices'][target_vertex]['outbound_streams']

  # get inner wires, i.e., the interface wires of all inner streams
  group_props['wire_decl'] = get_group_inner_wire_name_to_width(group_props['sub_streams'], config)

  # get the new port/wire map for the group vertex
  group_props['port_width_map'] = get_group_port_width_map(config, config['vertices'][target_vertex])
  group_props['port_wire_map'] = get_group_port_wire_map(config, config['vertices'][target_vertex])

  return group_props


def group_inbound_streams(
  config: Dict,
  target_vertex: str,
) -> None:
  """Create a wrapper to include all inbound streams of an vertex"""
  if target_vertex not in config['vertices']:
    _logger.error('vertex not existing in config')
    exit(1)

  props = config['vertices'][target_vertex]
  in_streams = {name: config['edges'][name] for name in props['inbound_streams']}

  config['vertices'][f'WRAPPER_VERTEX_{target_vertex}'] = get_group_vertex_props(
    config, target_vertex
  )

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

  return
