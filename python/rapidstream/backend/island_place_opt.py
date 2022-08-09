import click
import json
import os
import shutil
from typing import Dict, List

from .util import ParallelManager, get_local_anchor_list

@click.command()
@click.option(
  '--config-path',
  required=True,
  help='Path to the TAPA configuration file.'
)
@click.option(
  '--init-place-dir',
  required=True,
)
@click.option(
  '--anchor-place-dir',
  required=True,
)
@click.option(
  '--place-opt-dir',
  required=True,
)
@click.option(
  '--top-name',
  required=True,
)
def setup_island_placement_opt(
    config_path: str,
    init_place_dir: str,
    anchor_place_dir: str,
    place_opt_dir: str,
    top_name: str,
):
  """"""
  config = json.loads(open(config_path, 'r').read())

  anchor_place_dir = os.path.abspath(anchor_place_dir)
  init_place_dir = os.path.abspath(init_place_dir)
  place_opt_dir = os.path.abspath(place_opt_dir)

  if os.path.exists(place_opt_dir):
    shutil.rmtree(place_opt_dir)

  os.mkdir(place_opt_dir)

  # collect all anchor locations
  anchor_to_loc = collect_all_anchor_locs(anchor_place_dir)
  open(f'{place_opt_dir}/anchor_locs.json', 'w').write(json.dumps(anchor_to_loc, indent=2))

  mng = ParallelManager()
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{place_opt_dir}/{slot_name}')
    script = get_island_opt_script(
      config, top_name, slot_name, anchor_to_loc, init_place_dir, place_opt_dir
    )
    open(f'{place_opt_dir}/{slot_name}/island_phys_opt.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{place_opt_dir}/{slot_name}/', 'island_phys_opt.tcl')

  open(f'{place_opt_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))


def collect_all_anchor_locs(anchor_place_dir: str) -> Dict[str, str]:
  anchor_to_loc = {}
  for root, dirs, files in os.walk(anchor_place_dir):
    for file in files:
      if file.endswith('json'):
        local_anchor_to_loc = json.loads(open(f'{root}/{file}', 'r').read())
        anchor_to_loc.update(local_anchor_to_loc)
  return anchor_to_loc


def get_local_anchor_to_loc(
    config: Dict,
    slot_name: str,
    anchor_to_loc: Dict[str, str],
) -> Dict[str, str]:
  local_anchor_to_loc = {}
  for orientation in config['vertices'][slot_name]['orientation_to_wire'].keys():
    _local_anchor_list = get_local_anchor_list(config, slot_name, orientation)
    local_anchor_to_loc.update(
      {anchor: anchor_to_loc[anchor] for anchor in _local_anchor_list}
    )
  return local_anchor_to_loc


def get_island_opt_script(
  config: Dict,
  top_name: str,
  slot_name: str,
  anchor_to_loc: Dict[str, str],
  init_place_dir: str,
  place_opt_dir: str,
) -> List[str]:
  script = []

  local_anchor_to_loc = get_local_anchor_to_loc(config, slot_name, anchor_to_loc)

  kernel_cell_addr = f'pfm_top_i/dynamic_region/{top_name}/inst/'
  local_anchor_to_loc = {kernel_cell_addr + anchor : loc for anchor, loc in local_anchor_to_loc.items()}

  script.append(f'open_checkpoint {init_place_dir}/{slot_name}/{slot_name}_place.dcp')

  # remove the location of anchors from last iteration
  script.append('unplace_cell { \\')
  for anchor in local_anchor_to_loc.keys():
    script.append(f'  {anchor} \\')
  script.append('}')

  # dictate the location for each anchor
  script.append('place_cell { \\')
  for anchor, loc in local_anchor_to_loc.items():
    script.append(f'  {anchor} {loc} \\')
  script.append('}')

  script.append('phys_opt_design')

  # extract locations of src and dst of each anchor
  script.append(f'set kernel_cell_addr "{kernel_cell_addr}"')
  script.append(f'source /share/einsx7/vast-lab-tapa/RapidStream/tcl/extractSrcAndDstOfAnchors.tcl')

  script.append(f'write_checkpoint {place_opt_dir}/{slot_name}/{slot_name}_place.dcp')

  kernel_cell = kernel_cell_addr.strip('/')
  script.append(f'write_checkpoint -cell {kernel_cell} {place_opt_dir}/{slot_name}/{slot_name}_place.dcp')

  return script

if __name__ == '__main__':
  setup_island_placement_opt()
