import click
import logging
import json
import os
import shutil
from typing import Dict, List

from .floorplan_const import *
from .util import ParallelManager, get_local_anchor_list, collect_anchor_to_dir_to_locs, RAPIDSTREAM_BASE_PATH

_logger = logging.getLogger().getChild(__name__)


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
def setup_anchor_placement(
    config_path: str,
    init_place_dir: str,
    anchor_place_dir: str,
):
  config = json.loads(open(config_path, 'r').read())
  anchor_place_dir = os.path.abspath(anchor_place_dir)
  setup_anchor_placement_inner(config, init_place_dir, anchor_place_dir)

def setup_anchor_placement_inner(
    config: Dict,
    init_place_dir: str,
    anchor_place_dir: str,
):
  """"""
  if os.path.exists(anchor_place_dir):
    shutil.rmtree(anchor_place_dir)

  os.mkdir(anchor_place_dir)

  anchor_to_dir_to_cells = collect_anchor_to_dir_to_locs(init_place_dir)
  open(f'{anchor_place_dir}/anchor_to_dir_to_cells.json', 'w').write(json.dumps(anchor_to_dir_to_cells, indent=2))

  mng = ParallelManager()

  # create a placement project for each anchor region
  for slot_name, orientation in ANCHOR_REGIONS:
    # create anchor list in each anchor region
    local_anchor_list = get_local_anchor_list(config, slot_name, orientation)

    if not local_anchor_list:
      _logger.info(f'No placement result found on the {orientation} side of {slot_name}')
      continue

    # get all anchors belonging to this anchor region, and src/sink cells
    local_anchor_to_dir_to_cells = {anchor: anchor_to_dir_to_cells[anchor] for anchor in local_anchor_list}

    # get the pblock definition
    anchor_pblock = ISLAND_TO_DIR_TO_ANCHOR_PBLOCK[slot_name][orientation]

    script = get_anchor_placement_script(anchor_pblock, local_anchor_to_dir_to_cells)

    os.mkdir(f'{anchor_place_dir}/{slot_name}_{orientation}')
    open(f'{anchor_place_dir}/{slot_name}_{orientation}/place_anchor.tcl', 'w').write('\n'.join(script))

    mng.add_task(f'{anchor_place_dir}/{slot_name}_{orientation}/', 'place_anchor.tcl')

  open(f'{anchor_place_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))


def get_anchor_placement_script(
  anchor_pblock: str,
  anchor_to_dir_to_cells: Dict[str, List[Dict[str, str]]],
):
  """each anchor in the anchor list must be an individual anchor, not an array"""
  script = []
  script.append(f'open_checkpoint {RAPIDSTREAM_BASE_PATH}/platform/u280/empty_U280.dcp')

  # create anchors, src/sink cells
  script.append('create_cell -reference FDRE { \\')
  for anchor in anchor_to_dir_to_cells.keys():
    script.append(f'  {anchor} \\') # note that spaces are not allowed after \
    script.append(f'  {anchor}_input \\')
    script.append(f'  {anchor}_output \\')
  script.append('}')
  script.append('set_property DONT_TOUCH true [get_cells *]')

  # create boundary nets
  script.append('create_net { \\')
  for anchor in anchor_to_dir_to_cells.keys():
    script.append(f'  {anchor}_Q \\')
    script.append(f'  {anchor}_D \\')
  script.append('}')

  # connect anchors with src/sinks
  script.append(f'set nets_to_connect []')
  for anchor in anchor_to_dir_to_cells.keys():
    script.append(f'lappend nets_to_connect [get_nets {anchor}_Q]')
    script.append(f'lappend nets_to_connect [get_pins {anchor}/Q]')

    script.append(f'lappend nets_to_connect [get_nets {anchor}_Q]')
    script.append(f'lappend nets_to_connect [get_pins {anchor}_output/D]')

    script.append(f'lappend nets_to_connect [get_nets {anchor}_D]')
    script.append(f'lappend nets_to_connect [get_pins {anchor}/D]')

    script.append(f'lappend nets_to_connect [get_nets {anchor}_D]')
    script.append(f'lappend nets_to_connect [get_pins {anchor}_input/Q]')
  script.append('connect_net -dict $nets_to_connect')

  # create clock
  script.append('create_cell -reference BUFGCE clock_buffer')
  script.append('place_cell clock_buffer BUFGCE_X0Y194')
  script.append('create_clock -name ap_clk -period 3 [get_pins clock_buffer/O]')

  # connect clock to each anchor and src/sinks
  script.append('create_net ap_clk')
  script.append('connect_net -net ap_clk -objects [get_pins clock_buffer/O]')
  script.append('connect_net -net ap_clk -objects [get_pins */C]')

  # place the src/sinks of anchors
  script.append('place_cell { \\')
  for anchor, dir_to_cells in anchor_to_dir_to_cells.items():
    for dir in ('input', 'output'):
      assert len(dir_to_cells[dir]) == 1
      assert dir_to_cells[dir][0]['type'] == 'REGISTER.SDR.FDRE'
      loc = dir_to_cells[dir][0]['loc']
      script.append(f'  {anchor}_{dir} {loc} \\')
  script.append('}')

  # add anchors to pblock
  script.append(f'create_pblock anchor_pblock')
  script.append(f'resize_pblock anchor_pblock -add {anchor_pblock}')
  script.append(f'set_property IS_SOFT false [get_pblocks anchor_pblock]')
  script.append(f'add_cells_to_pblock anchor_pblock [get_cells * -filter {{STATUS == UNPLACED}}]')

  # add placeholders for pre-used lagunas
  script.append(f'source {RAPIDSTREAM_BASE_PATH}/platform/u280/add_laguna_placeholders.tcl')

  # place design
  script.append(f'place_design')

  # extract anchor locations
  script.append(f'set all_lines []')
  for anchor in anchor_to_dir_to_cells.keys():
    script.append(f'set anchor_loc [get_property LOC [get_cells {anchor}]]')
    script.append(f'set anchor_bel [get_property BEL [get_cells {anchor}]]')
    script.append(f'set anchor_bel [lindex [split $anchor_bel "."] 1]')
    script.append(f'set line "  \\\"{anchor}\\\": \\\"${{anchor_loc}}/${{anchor_bel}}\\\" "')
    script.append(f'lappend all_lines $line')

  # generate json file
  script.append('set file [open "anchor_placement.json" "w"]')
  script.append('puts $file " { "')
  script.append('puts $file [join $all_lines ",\n"]')
  script.append('puts $file " } "')
  script.append('close $file')

  return script


def collect_anchor_placement_result(anchor_place_dir):
  """collect the anchor locations after all anchor placement are done"""
  anchor_to_loc = {}
  for slot_name, orientation in ANCHOR_REGIONS:
    placement_dir = f'{anchor_place_dir}/{slot_name}_{orientation}'

    # in case an anchor region is empty, we should not create a directory for it
    if os.path.isdir(placement_dir):
      local_placement = json.load(open(f'{placement_dir}/anchor_placement.json', 'r'))
      anchor_to_loc.update(local_placement)
    else:
      _logger.info(f'skip collecting placement of anchor on the {orientation} side of {slot_name}')

  old_anchor_placement = json.load(open(f'{anchor_place_dir}/anchor_to_dir_to_cells.json', 'r'))
  for anchor, loc in anchor_to_loc.items():
    old_anchor_placement[anchor]['anchor_loc'] = loc
  open(f'{anchor_place_dir}/new_anchor_placement.json', 'w').write(json.dumps(old_anchor_placement, indent=2))


if __name__ == '__main__':
  setup_anchor_placement()
