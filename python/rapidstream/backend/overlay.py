import click
import json
import os
import shutil
from typing import Dict, List

from .floorplan_const import ISLAND_TO_PBLOCK
from .util import collect_anchor_to_dir_to_locs
from .setup_nested_dfx import setup_next_level_partpin


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
    anchor_place_dir: str,
):

  generate_overlay_inner(
    overlay_generation_dir,
    top_name,
    anchor_place_dir,
  )

def generate_overlay_inner(
    overlay_generation_dir: str,
    top_name: str,
    anchor_place_dir: str,
    nested_dfx_dcp_path: str,
):
  overlay_generation_dir = os.path.abspath(overlay_generation_dir)
  anchor_place_dir = os.path.abspath(anchor_place_dir)
  nested_dfx_dcp_path = os.path.abspath(nested_dfx_dcp_path)

  anchor_to_info = json.load(open(f'{anchor_place_dir}/new_anchor_placement.json', 'r'))

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

  # Directly place_cell instead of place_design
  # the placeholder FF for top-level IOs will be placed on the boundary of the bottom right island
  # the same placement will be reused every time
  script.append('source /share/einsx7/vast-lab-tapa/RapidStream/platform/u280/place_top_io_placeholder_ff.tcl')
  script += setup_next_level_partpin()

  script.append(f'write_checkpoint {overlay_generation_dir}/overlay_placed.dcp')
  script.append(f'write_edif {overlay_generation_dir}/overlay_placed.edf')

  # route_design to get the complete overlay
  script.append(f'catch {{ route_design -directive Quick }} ')
  script.append(f'write_checkpoint {overlay_generation_dir}/overlay.dcp')

  if os.path.exists(overlay_generation_dir):
    shutil.rmtree(overlay_generation_dir)
  os.mkdir(overlay_generation_dir)
  open(f'{overlay_generation_dir}/gen_overlay.tcl', 'w').write('\n'.join(script))

  bitstream_script = gen_overlay_bistream_script()
  open(f'{overlay_generation_dir}/gen_overlay_bitstream.tcl', 'w').write('\n'.join(bitstream_script))


def gen_overlay_bistream_script():
  bitstream_script = []
  bitstream_script.append(f'open_checkpoint overlay.dcp')
  bitstream_script.append(f'pr_recombine -cell pfm_top_i/dynamic_region/gaussian_kernel/inst')
  bitstream_script.append(f'pr_recombine -cell pfm_top_i/dynamic_region')
  bitstream_script.append(f'write_bitstream -cell pfm_top_i/dynamic_region overlay.bit')
  return bitstream_script


if __name__ == '__main__':
  generate_overlay()
