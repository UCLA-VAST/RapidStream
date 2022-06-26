import logging
from typing import Dict, List, Tuple
from itertools import chain

from rapidstream.const import RESOURCE_TYPES

_logger = logging.getLogger().getChild(__name__)

# update the json config files to logically wrap task instances together

def check_can_be_grouped(inst_name_to_props: Dict):
  """check if all vertices are floorplanned to the same slot"""
  regions = [props['floorplan_region'] for props in inst_name_to_props.values()]
  if not all(regions[i] == regions[0] for i in range(len(regions))):
    _logger.error('trying to group vertices assigned to different regions')
    exit(1)

  slrs = [props['SLR'] for props in inst_name_to_props.values()]
  if not all(slrs[i] == slrs[0] for i in range(len(slrs))):
    _logger.error('trying to group vertices assigned to different SLRs')
    exit(1)


def get_group_internal_and_external_streams(
  config: Dict, instances: List[str]
) -> Tuple[List[str], List[str]]:
  """The internal & external streams of the grouped vertex"""
  internal_streams = []
  external_streams = []

  instances_set = set(instances)
  for e, props in config['edges'].items():
    src_in = props['produced_by'] in instances_set
    dst_in = props['consumed_by'] in instances_set

    if src_in and dst_in:
      internal_streams.append(e)
    elif src_in != dst_in:
      external_streams.append(e)

  return internal_streams, external_streams


def get_group_io_streams(
  external_streams: List[str],
  inst_name_to_props: Dict,
) -> Tuple[List[str], List[str]]:
  """Get the inbound/outbound streams of the group vertex"""
  in_streams_of_all_vertices = [props['inbound_streams'] for props in inst_name_to_props.values()]
  all_potential_in_streams = list(
    chain(*in_streams_of_all_vertices)
  )

  out_streams_of_all_vertices = [props['outbound_streams'] for props in inst_name_to_props.values()]
  all_potential_out_streams = list(
    chain(*out_streams_of_all_vertices)
  )

  in_streams_of_group = [s for s in external_streams if s in all_potential_in_streams]
  out_streams_of_group = [s for s in external_streams if s in all_potential_out_streams]

  return in_streams_of_group, out_streams_of_group


def get_group_inner_wire_name_to_width(
  internal_streams: List[str],
  config: Dict,
) -> Dict[str, str]:
  """Get the internal wires of the group vertex"""
  inner_wire_names = []
  for stream in internal_streams:
    inner_wire_names += config['edges'][stream]['port_wire_map']['inbound'].values()
    inner_wire_names += config['edges'][stream]['port_wire_map']['outbound'].values()

  inner_wire_name_to_width = {
    name: config['wire_decl'][name] for name in inner_wire_names
  }

  return inner_wire_name_to_width


def get_group_port_width_map(
  inst_name_to_props: Dict,
  external_streams: List[str],
) -> Dict[str, str]:
  """When we create a wrapper around some vertices
     We need to update the port-width map
     New ports will be created and named after the wires on the wrapper module
     This function must runs before get_group_port_wire_map
  """
  port_width_map = {}

  for inst, props in inst_name_to_props.items():
    for stream, ports in props['port_wire_map']['stream_ports'].items():
      if stream in external_streams:
        for portname, argname in ports.items():
          if portname.endswith(('_dout', '_din')):
            width = props['port_width_map'][portname]
            port_width_map[argname] = width
            _logger.debug('stream port %s is recorded to have data width %s', argname, width)

  for inst, props in inst_name_to_props.items():
    for portname, argname in props['port_wire_map']['constant_ports'].items():
      width = props['port_width_map'][portname]
      port_width_map[argname] = width
      _logger.debug('constant port %s is recorded to have data width %s', argname, width)

  return port_width_map


def get_group_port_wire_map(
  inst_name_to_props: Dict,
  external_streams: List[str],
) -> Dict:
  """This must be run after the port-width map has been updated"""
  port_wire_map = {
    'axi_ports': [],  # for top level AXI connection
    'ctrl_ports': {},  # for ap signals
    'constant_ports': {},  # for scalar arguments from s_axi_control,
    'stream_ports': {},  # connect to FIFOs
  }

  for inst, props in inst_name_to_props.items():
    for axi_entry in props['port_wire_map']['axi_ports']:
      width = axi_entry['data_width']
      argname = axi_entry['argname']
      portname = axi_entry['portname']

      # we name the new ports after the wire being split up
      port_wire_map['axi_ports'].append(
        {
          'portname': argname,
          'argname': argname,
          'data_width': width,
          'axi_type': axi_entry['axi_type'],
        }
      )

    port_wire_map['ctrl_ports'] = {
      "ap_clk": None,
      "ap_rst_n": None,
      "ap_start": None,
      "ap_done": None,
      "ap_idle": None,
      "ap_ready": None,
    }
    port_wire_map['constant_ports'].update(
      {argname: argname for portname, argname in
        props['port_wire_map']['constant_ports'].items()
      }
    )

    for stream, ports in props['port_wire_map']['stream_ports'].items():
      if stream in external_streams:
        # When we create a wrapper, the port name changes
        # Suppose in the original vertex, there is a port foo connecting to the wire bar
        # If we create a wrapper around the vertex
        # the wrapper will have a port bar that connects to a wire also named bar
        # in other words, we name the newly created logical port by the name of the wire
        port_wire_map['stream_ports'][stream] = {
          argname: argname for argname in ports.values()
        }

  return port_wire_map


def get_accumulated_area(inst_name_to_props: Dict) -> Dict[str, int]:
  areas = [props['area'] for props in inst_name_to_props.values()]

  # do not use Counter in case all vertices don't have some of them (e.g., URAM)
  # make sure the final acc has all types even if the usage is 0
  acc_area = {r: 0 for r in RESOURCE_TYPES}
  for i in range(len(areas)):
    for r in RESOURCE_TYPES:
      acc_area[r] += areas[i][r]
  return acc_area


def get_group_vertex_props(
  config: Dict,
  inst_name_to_props: Dict,
  internal_streams: List[str],
  external_streams: List[str],
  group_name: str,
) -> Dict:
  # add the new vertex for the group
  group_props = {}
  group_props['module'] = group_name
  group_props['instance'] = f'{group_name}'
  group_props['area'] = get_accumulated_area(inst_name_to_props)
  group_props['category'] = 'GROUP_VERTEX'

  # assume all vertices are floorplaned to the same region
  any_inst = next(iter(inst_name_to_props.keys()))
  group_props['floorplan_region'] = inst_name_to_props[any_inst]['floorplan_region']
  group_props['SLR'] = inst_name_to_props[any_inst]['SLR']

  group_props['sub_vertices'] = inst_name_to_props
  group_props['sub_streams'] = {
    name: config['edges'][name] for name in  internal_streams
  }

  group_props['inbound_streams'], group_props['outbound_streams'] = get_group_io_streams(
    external_streams, inst_name_to_props,
  )

  # get inner wires, i.e., the interface wires of all inner streams
  group_props['wire_decl'] = get_group_inner_wire_name_to_width(internal_streams, config)

  # get the new port/wire map for the group vertex
  group_props['port_width_map'] = get_group_port_width_map(inst_name_to_props, external_streams)
  group_props['port_wire_map'] = get_group_port_wire_map(inst_name_to_props, external_streams)

  return group_props


def group_vertices(
  config: Dict,
  instances: List[str],
  group_name: str,
) -> Dict:
  """Update the config to group a list of vertices into one vertex"""
  if not instances:
    _logger.warning('No instances to group')
    return

  # get the properties of the vertices to be grouped
  inst_name_to_props = {name: config['vertices'][name] for name in instances}
  check_can_be_grouped(inst_name_to_props)

  internal_streams, external_streams = get_group_internal_and_external_streams(
    config, instances
  )

  # add the new group vertex to config
  config['vertices'][group_name] = get_group_vertex_props(
    config, inst_name_to_props, internal_streams, external_streams, group_name
  )

  # remove the inner wires from the external wire list
  # must be before internal streams are removed
  inner_wires = get_group_inner_wire_name_to_width(internal_streams, config)
  for w in inner_wires.keys():
    config['wire_decl'].pop(w)

  # remove the vertices to be grouped
  config['vertices'] = {
    name: props for name, props in config['vertices'].items()
      if name not in instances
  }

  # remove the internal streams in the group
  config['edges'] = {e: props for e, props in config['edges'].items()
    if e not in internal_streams
  }

  return config['vertices'][group_name]
