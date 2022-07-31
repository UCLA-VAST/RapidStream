import logging
from typing import Dict, List, Tuple

from rapidstream.hierarchy_rebuild.gen_wrapper_io_property import generate_ctrl_vertex_io_list

_logger = logging.getLogger().getChild(__name__)


def get_port_wire_map(config: Dict, target_vertex: str, ctrl_vertex: str) -> Dict:
  ctrl_props = config['vertices'][ctrl_vertex]
  target_props = config['vertices'][target_vertex]

  pw_map = {
    'axi_ports': [],
    'ctrl_out': [],
    'ctrl_in': [],
    'reset_out': [],
    'constant_out': [],
    'stream_ports': {},
    'passing_streams': {},
  }

  # axi interfaces
  for props in (ctrl_props, target_props):
    for axi_entry in props['port_wire_map']['axi_ports']:
      width = axi_entry['data_width']
      argname = axi_entry['argname']
      portname = axi_entry['portname']
      axi_type = axi_entry['axi_type']

      # we name the new ports after the wire being split up
      pw_map['axi_ports'].append(
        {
          'portname': argname,
          'argname': argname,
          'data_width': width,
          'axi_type': axi_type,
        }
      )

  # stream interfaces
  for stream, ports in target_props['port_wire_map']['stream_ports'].items():
    pw_map['stream_ports'][stream] = {
      argname: argname for argname in ports.values()
    }

  # passing streams
  # directly connect passing streams with the inner vertex, and let the inner vertex handle it
  target_props['port_wire_map'].get('passing_streams', {})

  return pw_map


def embed_ctrl_unit(config: Dict, target_vertex: str, ctrl_vertex: str) -> Dict:
  """Create a new vertex that includes the ctrl vertex and one slot vertex"""
  assert target_vertex in config['vertices']
  assert ctrl_vertex in config['vertices']

  # add additional ports to the target island
  ctrl_props = config['vertices'][ctrl_vertex]
  target_props = config['vertices'][target_vertex]

  module_name = target_vertex.replace('WRAPPER_VERTEX', 'CTRL_WRAPPER_VERTEX')
  # do not add the CTRL_ prefix, which causes lots of corner cases downstream
  # module_name = target_vertex

  ctrl_wrapper_props = {
    'module': module_name,
    'instance': f'{module_name}',
    'area': target_props['area'],  # FIXME: neglect the area of the ctrl unit
    'category': 'CTRL_WRAPPER',
    'floorplan_region': target_props['floorplan_region'],
    'SLR': target_props['SLR'],
    'sub_vertices': {
      target_vertex: target_props,
      ctrl_vertex: ctrl_props,
    },
    'sub_streams': {},  # the ctrl wrapper only group the ctrl unit with one exsiting vertex
    'inbound_streams': target_props['inbound_streams'],
    'outbound_streams': target_props['outbound_streams'],
    'wire_decl': {**target_props.get('wire_decl', {}), **ctrl_props.get('wire_decl', {})},
    'port_width_map': {**target_props['port_width_map'], **ctrl_props['port_width_map']},
    'port_wire_map': get_port_wire_map(config, target_vertex, ctrl_vertex),
    'param_map': { **target_props.get('param_map', {}), **ctrl_props.get('param_map', {})},
  }

  config['vertices'].pop(target_vertex)
  config['vertices'].pop(ctrl_vertex)

  # create ap_start and ap_done connection for every island except the target island
  for v_name, v_props in config['vertices'].items():
    if v_props['category']  == 'PORT_VERTEX':
      continue
    ctrl_wrapper_props['port_wire_map']['ctrl_out'].append(f'ap_start_{v_name}')
    ctrl_wrapper_props['port_wire_map']['ctrl_in'].append(f'ap_done_{v_name}')
    ctrl_wrapper_props['port_wire_map']['reset_out'].append(f'ap_rst_n_{v_name}')

    # declare the wire in the upper level
    # FIXME: should add a function to collect all upper level wires
    # based on port_wire_map and port_width_map
    config['wire_decl'][f'ap_start_{v_name}'] = ''
    config['wire_decl'][f'ap_rst_n_{v_name}'] = ''
    config['wire_decl'][f'ap_done_{v_name}'] = ''

  # send out constants
  ctrl_wrapper_props['port_wire_map']['constant_out'] = ctrl_props['port_wire_map']['constant_ports']

  # update the port wire map of the ctrl vertex
  ctrl_props['port_wire_map']['ctrl_ports']['ap_start'] = 'ap_start_orig'
  ctrl_props['port_wire_map']['ctrl_ports']['ap_done'] = 'ap_done_final'
  ctrl_props['port_wire_map']['ctrl_ports']['ap_idle'] = 'ap_done_final'
  ctrl_props['port_wire_map']['ctrl_ports']['ap_ready'] = 'ap_done_final'
  ctrl_props['port_wire_map']['ctrl_ports']['ap_local_deadlock'] = ''
  ctrl_wrapper_props['wire_decl']['ap_start_orig'] = ''
  ctrl_wrapper_props['wire_decl']['ap_done_final'] = ''

  # udpate the port wire map of the wrapper vertex
  ctrl_wrapper_props['wrapper_sub_vertex'] = target_vertex
  ctrl_wrapper_props['ctrl_sub_vertex'] = ctrl_vertex

  config['vertices'][module_name] = ctrl_wrapper_props

  generate_ctrl_vertex_io_list(ctrl_wrapper_props)

  return ctrl_wrapper_props
