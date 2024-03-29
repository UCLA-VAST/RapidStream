import logging
from collections import defaultdict
from typing import Dict

from rapidstream.hierarchy_rebuild.group_ctrl_unit import embed_ctrl_unit
from rapidstream.hierarchy_rebuild.group_inbound_streams import group_inbound_streams
from rapidstream.hierarchy_rebuild.group_passing_streams import group_passing_streams
from rapidstream.hierarchy_rebuild.group_vertices import group_vertices
from rapidstream.hierarchy_rebuild.embed_ctrl_signals import hard_code_embed_ctrl_signals
from rapidstream.rtl_gen.anchor_wrapper import get_anchor_wrapper, get_empty_island
from rapidstream.rtl_gen.ctrl_wrapper import get_ctrl_wrapper
from rapidstream.rtl_gen.group_wrapper import get_group_wrapper
from rapidstream.rtl_gen.top import get_top, get_top_with_empty_islands

_logger = logging.getLogger().getChild(__name__)


def islandize_vertices(config: Dict, top_name: str, use_anchor_wrapper: bool = True) -> Dict:
  """Restructure the RTL to form island hierarchies
  use_anchor_wrapper: affects which wrapper to instantiate in the top as well as the latency calculation
  """
  slot_to_vertices = defaultdict(list)
  name_to_file = {}
  name_to_dummy_file = {}

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
    group_top = get_group_wrapper(group_vertex_props, use_anchor_wrapper, is_initial_wrapper=True)
    name_to_file[f'{slot}.v'] = group_top

  # group inbound streams
  for slot in slot_to_vertices.keys():
    group_name = f'WRAPPER_VERTEX_{slot}'
    group_inbound_streams(config, slot, group_name)

  # embed passing streams
  group_passing_streams(config, pipeline_level = 1)

  # FIXME: hard code embed ctrl signals
  hard_code_embed_ctrl_signals(config)

  # generate stream-including wrappers
  for v_name, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue
    _logger.debug(v_name)
    group_top = get_group_wrapper(props, use_anchor_wrapper, is_initial_wrapper=False)
    name_to_file[f'{v_name}.v'] = group_top

  # generate ctrl-including wrapper
  ctrl_wrapper_props = embed_ctrl_unit(config, 'WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3', 'CTRL_VERTEX_control_s_axi')
  ctrl_wrapper = get_ctrl_wrapper(config, ctrl_wrapper_props, use_anchor_wrapper)
  name_to_file[f'{ctrl_wrapper_props["module"]}.v'] = ctrl_wrapper

  # get anchor wrapper
  for v_name, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue
    anchor_wrapper = get_anchor_wrapper(config, props)
    name_to_file[f'{v_name}_anchor_wrapper.v'] = anchor_wrapper

    empty_island = get_empty_island(config, props)
    name_to_dummy_file[f'{v_name}.v'] = empty_island

  # generate top rtl
  top = get_top(config, top_name, use_anchor_wrapper)
  name_to_file[f'{top_name}.v'] = top

  # dummy top with the same name
  dummy_top = get_top_with_empty_islands(config, top_name)
  name_to_dummy_file[f'{top_name}.v'] = dummy_top

  return name_to_file, name_to_dummy_file
