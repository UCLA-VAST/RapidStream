import click
import json
from collections import defaultdict
from typing import Dict

from rapidstream.hierarchy_rebuild.group_vertices import group_vertices
from rapidstream.hierarchy_rebuild.group_inbound_streams import group_inbound_streams
from rapidstream.parser.tapa_parser import parse_tapa_output_rtl
from rapidstream.rtl_gen.group_wrapper import get_group_wrapper
from rapidstream.rtl_gen.top import get_top


def islandize_vertices(config: Dict, output_dir: str, top_name: str):
  """Restructure the RTL to form island hierarchies"""
  slot_to_vertices = defaultdict(list)

  for name, props in config['vertices'].items():
    if props['category'] == 'PORT_VERTEX':
      continue

    slot = props.get('floorplan_region', '')
    if slot:
      slot_to_vertices[slot].append(name)

  for slot, vertices in slot_to_vertices.items():
    group_vertex_props = group_vertices(config, vertices, slot)
    group_top = get_group_wrapper(group_vertex_props)
    open(f'{output_dir}/{slot}.v', 'w').write('\n'.join(group_top))

  for slot in slot_to_vertices.keys():
    group_name = f'WRAPPER_VERTEX_{slot}'
    group_vertex_props = group_inbound_streams(config, slot, group_name)
    group_top = get_group_wrapper(group_vertex_props)
    open(f'{output_dir}/{group_name}.v', 'w').write('\n'.join(group_top))

  top = get_top(config, top_name)
  open(f'{output_dir}/{top_name}.v', 'w').write('\n'.join(top))
