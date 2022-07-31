"""Create each sub task in the backend flow"""

from typing import Dict
from rapidstream.platform.const import *


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

  # for each island, get the shared io with neighbors in each orientation
  for island, props in config['vertices'].items():
    floorplan_region = props['floorplan_region']
    orientation_to_io_to_width = {}
    for orientation in ISLAND_ORIENTATIONS:
      neighbor_name = get_neighbor_island_name(orientation)

      # at the boundary
      if not neighbor_name:
        continue

      neighbor_props = config['vertices'][neighbor_name]

      dir_to_io_to_width = {
        'input': dict(props['io_dir_to_name_to_width']['input'].items() &
                         neighbor_props['io_dir_to_name_to_width']['output'].items()),
        'output': dict(props['io_dir_to_name_to_width']['output'].items() &
                         neighbor_props['io_dir_to_name_to_width']['input'].items()),
      }

      orientation_to_io_to_width[orientation] = dir_to_io_to_width

    props['orientation_to_dir_to_io_name_to_width'] = orientation_to_io_to_width
