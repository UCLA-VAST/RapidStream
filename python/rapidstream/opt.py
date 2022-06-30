import json
import logging
from collections import defaultdict
from typing import Dict

from rapidstream.hierarchy_rebuild.group_ctrl_unit import embed_ctrl_unit
from rapidstream.hierarchy_rebuild.group_inbound_streams import group_inbound_streams
from rapidstream.hierarchy_rebuild.group_passing_streams import group_passing_streams
from rapidstream.hierarchy_rebuild.group_vertices import group_vertices
from rapidstream.rtl_gen.anchor_wrapper import get_anchor_wrapper, get_empty_island
from rapidstream.rtl_gen.ctrl_wrapper import get_ctrl_wrapper
from rapidstream.rtl_gen.group_wrapper import get_group_wrapper
from rapidstream.rtl_gen.top import get_top

_logger = logging.getLogger().getChild(__name__)


def islandize_vertices(config: Dict, output_dir: str, top_name: str):
  """Restructure the RTL to form island hierarchies"""
  slot_to_vertices = defaultdict(list)

  # extract floorplan results
  for name, props in config['vertices'].items():
    if props['category'] == 'PORT_VERTEX':
      continue

    slot = props.get('floorplan_region', '')
    if slot:
      slot_to_vertices[slot].append(name)

  # group initial vertices based on floorplanning
  for slot, vertices in slot_to_vertices.items():
    group_vertex_props = group_vertices(config, vertices, slot)
    group_top = get_group_wrapper(group_vertex_props)
    open(f'{output_dir}/{slot}.v', 'w').write('\n'.join(group_top))

  # group inbound streams
  for slot in slot_to_vertices.keys():
    group_name = f'WRAPPER_VERTEX_{slot}'
    group_inbound_streams(config, slot, group_name)

  # embed passing streams
  group_passing_streams(config, pipeline_level = 1)

  # generate stream-including wrappers
  for v_name, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue
    _logger.debug(v_name)
    group_top = get_group_wrapper(props)
    open(f'{output_dir}/{v_name}.v', 'w').write('\n'.join(group_top))

  # generate ctrl-including wrapper
  ctrl_wrapper_props = embed_ctrl_unit(config, 'WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3', 'CTRL_VERTEX_control_s_axi')
  ctrl_wrapper = get_ctrl_wrapper(ctrl_wrapper_props)
  open(f'{output_dir}/{ctrl_wrapper_props["module"]}.v', 'w').write('\n'.join(ctrl_wrapper))

  # get anchor wrapper
  for v_name, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue
    anchor_wrapper = get_anchor_wrapper(props)
    open(f'{output_dir}/{v_name}_anchor_wrapper.v', 'w').write('\n'.join(anchor_wrapper))

    empty_island = get_empty_island(props)
    open(f'{output_dir}/{v_name}_empty_island.v', 'w').write('\n'.join(empty_island))

  # generate top rtl
  top = get_top(config, top_name)
  open(f'{output_dir}/{top_name}.v', 'w').write('\n'.join(top))

  open('test.json', 'w').write(json.dumps(config, indent=2))
