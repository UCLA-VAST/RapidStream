import click
import json
import os
import re
import shutil
from typing import Dict, List

from .floorplan_const import *


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
  """"""
  config = json.loads(open(config_path, 'r').read())

  if os.path.exists(anchor_place_dir):
    shutil.rmtree(anchor_place_dir)

  os.mkdir(anchor_place_dir)

  anchor_to_dir_to_cells = {}

  # read in the six json file and merge them
  for root, dirs, files in os.walk(init_place_dir):
    for file in files:
      if file.endswith('.json'):
        anchor_info: Dict[str, List[Dict[str, str]]] = json.loads(open(f'{root}/{file}', 'r').read())
        for anchor, connections in anchor_info.items():
          # strip the path part
          cell_name = anchor.split('/')[-1]

          if cell_name not in anchor_to_dir_to_cells:
            anchor_to_dir_to_cells[cell_name] = {
              'input': [],
              'output': [],
            }

          for cell in connections:
            dir = cell.pop('dir')
            anchor_to_dir_to_cells[cell_name][dir] += [cell]

  open('anchor_to_dir_to_cells.json', 'w').write(json.dumps(anchor_to_dir_to_cells, indent=2))

  # create a placement project for each anchor region
  for slot_name, orientation in ANCHOR_REGIONS:
    os.mkdir(f'{anchor_place_dir}/{slot_name}_{orientation}')

    # create anchor list in each anchor region
    wire_list = config['vertices'][slot_name]['orientation_to_wire'][orientation]
    local_anchor_list = []
    for wire in wire_list:
      if wire == 'ap_clk':
        continue

      length = config['wire_decl'].get(wire, '')
      if not length:
        length = '[0:0]'
      msb = int(re.search(r'\[(.*):', length).group(1))
      if msb == 0:
        local_anchor_list += [f'{wire}_q_reg']
      else:
        local_anchor_list += [f'{wire}_q_reg[{i}]' for i in range(msb+1)]

    local_anchor_to_dir_to_cells = {anchor: anchor_to_dir_to_cells[anchor] for anchor in local_anchor_list}

    anchor_pblock = ISLAND_TO_DIR_TO_ANCHOR_PBLOCK[slot_name][orientation]

    script = get_anchor_placement_script(anchor_pblock, local_anchor_to_dir_to_cells)

    open(f'{anchor_place_dir}/{slot_name}_{orientation}/place_anchor.tcl', 'w').write('\n'.join(script))


def get_anchor_placement_script(
  anchor_pblock: str,
  anchor_to_dir_to_cells: Dict[str, List[Dict[str, str]]],
):
  """each anchor in the anchor list must be an individual anchor, not an array"""
  script = []
  script.append('open_checkpoint /share/einsx7/share/empty_U280.dcp')

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

  # place design
  script.append(f'place_design')

  # extract anchor locations

  return script


if __name__ == '__main__':
  setup_anchor_placement()
