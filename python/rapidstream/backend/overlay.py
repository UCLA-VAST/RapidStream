import click
import json
import os
import shutil
from typing import Dict, List

from .floorplan_const import ISLAND_TO_PBLOCK
from .util import collect_anchor_to_dir_to_locs


@click.command()
@click.option(
  '--config-path',
  required=True,
  help='Path to the TAPA configuration file.'
)
@click.option(
  '--overlay-generation-dir',
  required=True,
)
@click.option(
  '--dummy-wrapper-rtl-dir',
  required=True,
)
@click.option(
  '--top-name',
  required=True,
)
@click.option(
  '--hmss-shell-dcp-path',
  required=True,
)
@click.option(
  '--island-place-opt-dir',
  required=True,
)
def generate_overlay(
    config_path: str,
    overlay_generation_dir: str,
    dummy_wrapper_rtl_dir: str,
    top_name: str,
    hmss_shell_dcp_path: str,
    island_place_opt_dir: str,
    device: str = 'xcu280-fsvh2892-2L-e',
):
  config_path = os.path.abspath(config_path)
  overlay_generation_dir = os.path.abspath(overlay_generation_dir)
  dummy_wrapper_rtl_dir = os.path.abspath(dummy_wrapper_rtl_dir)
  hmss_shell_dcp_path = os.path.abspath(hmss_shell_dcp_path)
  island_place_opt_dir = os.path.abspath(island_place_opt_dir)

  config = json.loads(open(config_path, 'r').read())
  anchor_to_info = collect_anchor_to_dir_to_locs(island_place_opt_dir)

  script = []

  # synthesize top with dummy islands
  script += get_synth_dummy_islands_script(dummy_wrapper_rtl_dir, top_name, device)
  dummy_island_dcp_name = 'top_with_dummy_islands_synth.dcp'
  script.append(f'write_checkpoint {dummy_island_dcp_name}')

  kernel_cell = f'pfm_top_i/dynamic_region/{top_name}/inst'

  # create next level dfx
  script.append(f'open_checkpoint {hmss_shell_dcp_path}')
  script.append(f'pr_subdivide -cell {kernel_cell} -subcells {{')
  for slot_name in config['vertices'].keys():
    script.append(f'  {kernel_cell}/{slot_name}')
  script.append(f'}} {dummy_island_dcp_name}')
  script.append(f'write_checkpoint {overlay_generation_dir}/after_pr_subdivide.dcp')

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

  # FIXME directly place_cell instead of place_design
  script.append(f'place_design -directive Quick')

  # route_design to get the complete overlay
  script.append(f'route_design')
  script.append(f'write_checkpoint {overlay_generation_dir}/overlay.dcp')

  # generate bitstream for the overlay
  script.append(f'pr_recombine -cell pfm_top_i/dynamic_region/{top_name}/inst')
  script.append(f'pr_recombine -cell pfm_top_i/dynamic_region')
  script.append(f'write_bitstream -cell pfm_top_i/dynamic_region overlay.bit')

  if os.path.exists(overlay_generation_dir):
    shutil.rmtree(overlay_generation_dir)
  os.mkdir(overlay_generation_dir)
  open(f'{overlay_generation_dir}/gen_overlay.tcl', 'w').write('\n'.join(script))


def get_synth_dummy_islands_script(
    dummy_wrapper_rtl_dir: str,
    top_name: str,
    device: str,
):
  script = []

  script.append(f'set_part {device}')
  script.append(f'set rtl_files [glob {dummy_wrapper_rtl_dir}/*.v]')
  script.append(f'read_verilog ${{rtl_files}}')
  script.append(f'synth_design -top "{top_name}" -part {device} -mode out_of_context')
  return script


if __name__ == '__main__':
  generate_overlay()
