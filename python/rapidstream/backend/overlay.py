import click
import json
import os
import shutil
from typing import Dict, List

from .floorplan_const import ISLAND_TO_PBLOCK
from .util import collect_anchor_to_dir_to_locs


@click.command()
@click.option(
  '--overlay-generation-dir',
  required=True,
)
@click.option(
  '--top-name',
  required=True,
)
@click.option(
  '--island-place-opt-dir',
  required=True,
)
def generate_overlay(
    overlay_generation_dir: str,
    top_name: str,
    island_place_opt_dir: str,
):

  generate_overlay_inner(
    overlay_generation_dir,
    top_name,
    island_place_opt_dir,
  )

def generate_overlay_inner(
    overlay_generation_dir: str,
    top_name: str,
    island_place_opt_dir: str,
    nested_dfx_dcp_path: str,
):
  overlay_generation_dir = os.path.abspath(overlay_generation_dir)
  island_place_opt_dir = os.path.abspath(island_place_opt_dir)
  nested_dfx_dcp_path = os.path.abspath(nested_dfx_dcp_path)

  anchor_to_info = collect_anchor_to_dir_to_locs(island_place_opt_dir)

  script = []

  script.append(f'open_checkpoint {nested_dfx_dcp_path}')
  kernel_cell = f'pfm_top_i/dynamic_region/{top_name}/inst'

  # create pblock for each island
  for slot_name, pblock_range in ISLAND_TO_PBLOCK.items():
    script.append(f'create_pblock {slot_name}')
    script.append(f'resize_pblock {slot_name} -add {{ {pblock_range} }}')
    script.append(f'set_property IS_SOFT false [get_pblocks {slot_name}]')
    script.append(f'set_property CONTAIN_ROUTING true [get_pblocks {slot_name}]')
    script.append(f'add_cells_to_pblock {slot_name} [get_cells  pfm_top_i/dynamic_region/{top_name}/inst/{slot_name}]')
    script.append(f'')

  # place_cell all anchors and src/sink cells
  # then the entire design should be in a placed state
  script.append('place_cell { \\')
  for anchor, info in anchor_to_info.items():
    anchor_loc = info['anchor_loc']
    script.append(f'  {kernel_cell}/{anchor} {anchor_loc}')
    for dir in ('input', 'output'):
      loc = info[dir][0]['loc']
      name = info[dir][0]['name']
      script.append(f'  {name} {loc}')
  script.append('}')

  # FIXME directly place_cell instead of place_design, make it more general
  script.append(f'place_design -directive Quick')

  # route_design to get the complete overlay
  script.append(f'catch {{ route_design -directive Quick }} ')
  script.append(f'write_checkpoint {overlay_generation_dir}/overlay.dcp')

  if os.path.exists(overlay_generation_dir):
    shutil.rmtree(overlay_generation_dir)
  os.mkdir(overlay_generation_dir)
  open(f'{overlay_generation_dir}/gen_overlay.tcl', 'w').write('\n'.join(script))


if __name__ == '__main__':
  generate_overlay()
