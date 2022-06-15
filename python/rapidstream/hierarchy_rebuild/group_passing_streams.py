import logging
from typing import Dict, List, Tuple

_logger = logging.getLogger().getChild(__name__)


def embed_stream(config: Dict, stream_name: str, stream_props: Dict, pipeline_level: int) -> None:
  """Given a stream, embed it into the passing islands"""
  slot_path = [f'WRAPPER_VERTEX_{slot_name}' for slot_name in stream_props['path']]

  # the stream_name is between two adjacent islands
  if len(slot_path) == 2:
    _logger.debug(f'skip embedding {stream_name} as it is between adjacent islands')
    return

  _logger.debug(f'Embed {stream_name} into {slot_path[1:-1]}')

  # get the width of the wire to be split (full_n, din, write)
  # always split the inbound side
  inbound_side_wires = list(stream_props['port_wire_map']['inbound'].values())
  wire_to_width = {wire: config['wire_decl'].get(wire, '') for wire in inbound_side_wires}

  # remove the old wires from the upper level wire decl list
  for wire, width in wire_to_width.items():
    assert config['wire_decl'].get(wire, '') == width
    config['wire_decl'].pop(wire)

  # create new wires into the upper level wire decl list
  for wire, width in wire_to_width.items():
    for i in range(len(slot_path) - 1):
      wire_seg_name = f'{wire}_q{i}'
      config['wire_decl'][wire_seg_name] = width

  # update the port wire mapping of the consumer island
  # assume that the stream is already incorporated into the consumer island
  # thus we dont need to change the port-wire mapping of the stream
  consumer_props = config['vertices'][slot_path[-1]]
  assert stream_name in consumer_props['inbound_streams']
  assert stream_name in consumer_props['sub_streams']
  stream_ports = consumer_props['port_wire_map']['stream_ports']

  seg_id = len(slot_path) - 1
  stream_ports[stream_name] = {k: f'{v}_q{seg_id}' for k, v in stream_ports[stream_name].items()}

  # update the port wire mapping of the producer island
  producer_props = config['vertices'][slot_path[0]]
  assert stream_name in producer_props['outbound_streams']
  stream_ports = consumer_props['port_wire_map']['stream_ports']

  seg_id = 0
  stream_ports[stream_name] = {k: f'{v}_q{seg_id}' for k, v in stream_ports[stream_name].items()}

  # create passing ports on the intermediate islands
  for i in range(1, len(slot_path) - 1):
    passing_slot_props = config['vertices'].get(slot_path[i], None)

    # FIXME
    if not passing_slot_props:
      _logger.error('FIXME: The stream is routed to a slot with no record')
      exit(1)

    passing_slot_props['port_wire_map']['passing_streams'] = {
      stream_name: {
        'wire_to_width': wire_to_width,
        'inbound_side_suffix': f'_q{i-1}',
        'outbound_side_suffix': f'_q{i}',
        'pipeline_level': pipeline_level,
      }
    }


def group_passing_streams(config: Dict, pipeline_level: int) -> None:
  """Embed the streams so that each island only have stream interfaces
     to neighbor islands.
     pipeline_level: when a stream passes an islands, how many pipeline stages
     to put inside the passing island
  """

  visited_streams = set()

  for v_name, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue

    for stream_name in props['inbound_streams']:
      assert stream_name not in visited_streams
      visited_streams.add(stream_name)

      # assume that the inbound stream is immediately in the current wrapper
      # this pass must be followed by the group_inbound_streams pass
      stream_props = props['sub_streams'][stream_name]
      embed_stream(config, stream_name, stream_props, pipeline_level)
