"""Create each sub task in the backend flow"""
import re
from typing import Dict
from rapidstream.platform.const import *
from rapidstream.rtl_gen.top import _get_wire_to_io_of_slot


def get_wire_to_io_of_slot(props: Dict) -> Dict[str, str]:
  wire_with_dir_to_io = _get_wire_to_io_of_slot(props)
  wire_to_io_name = {re.sub('_(in|out)put$', '', wire_with_dir): io_name
    for wire_with_dir, io_name in wire_with_dir_to_io.items()}
  return wire_to_io_name


def annotate_io_orientation(config: Dict) -> None:
  """Extract which IOs are on each orientation
     Note that orientation means North, South, East, or West
     direction means input or output
  """
  pblock_to_island = {props['floorplan_region']: island for island, props in config['vertices'].items()}
  def get_neighbor_island_name(orientation):
    neighbor_pblock = ISLAND_TOPOLOGY[floorplan_region][orientation]
    if not neighbor_pblock:
      return ''
    return pblock_to_island[neighbor_pblock]

  island_to_wire_to_io = {island: get_wire_to_io_of_slot(props) for island, props in config['vertices'].items()}

  # for each island, get the shared io with neighbors in each orientation
  for island, props in config['vertices'].items():
    floorplan_region = props['floorplan_region']
    orientation_to_wire = {}
    for orientation in ISLAND_ORIENTATIONS:
      neighbor_name = get_neighbor_island_name(orientation)

      # at the boundary
      if not neighbor_name:
        continue

      neighbor_props = config['vertices'][neighbor_name]
      orientation_to_wire[orientation] = list(
        island_to_wire_to_io[island].keys() & island_to_wire_to_io[neighbor_name].keys()
      )

    props['orientation_to_wire'] = orientation_to_wire
