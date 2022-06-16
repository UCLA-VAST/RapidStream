import logging
from typing import Dict, List, Tuple

_logger = logging.getLogger().getChild(__name__)


def embed_ctrl_unit(config: Dict, target_vertex: str, ctrl_vertex: str) -> None:
  """Create a new vertex that includes the ctrl vertex and one slot vertex"""
  assert target_vertex in config['vertices']
  assert ctrl_vertex in config['vertices']

  # add additional ports to the target island
  ctrl_props = config['vertices'][ctrl_vertex]
  target_props = config['vertices'][target_vertex]

  module_name = target_vertex.replace('WRAPPER_VERTEX', 'CTRL_WRAPPER_VERTEX')
  ctrl_wrapper_props = {
    'module': module_name,
    'instance': f'{module_name}_0',
    'area': target_props['area'],  # FIXME: neglect the area of the ctrl unit
    'category': 'CTRL_WRAPPER',
    'floorplan_region': target_props['floorplan_region'],
    'SLR': target_props['SLR'],
    'sub_vertices': {
      target_vertex: target_props,
      ctrl_vertex: ctrl_props,
    },
    'sub_streams': {},
    'inbound_streams': target_props['inbound_streams'],
    'outbound_streams': target_props['outbound_streams'],

    'port_width_map': {**target_props['port_width_map'], **ctrl_props['port_width_map']},
    'port_wire_map': {
      'axi_ports': ctrl_props['port_wire_map']['axi_ports'] + target_props['port_wire_map'].get('axi_ports', []),
      'ctrl_out': [],
      'ctrl_in': [],
      'constant_out': [],
      'stream_ports': target_props['port_wire_map'].get('stream_ports', {}),
      'passing_streams': target_props['port_wire_map'].get('passing_streams', {}),
    },
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

  # send out constants
  ctrl_wrapper_props['port_wire_map']['constant_out'] = ctrl_props['port_wire_map']['constant_ports']

  config['vertices'][module_name] = ctrl_wrapper_props
