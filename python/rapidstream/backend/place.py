import os
from typing import Dict, List

from .util import ParallelManager

INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y0_NORTH = 'LAGUNA_X0Y0:LAGUNA_X15Y119'
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y0_NORTH = 'LAGUNA_X16Y0:LAGUNA_X25Y119'
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y1_NORTH = 'LAGUNA_X0Y240:LAGUNA_X15Y359'
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y1_NORTH = 'LAGUNA_X16Y240:LAGUNA_X25Y359'

INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y1_SOUTH = INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y0_NORTH
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y1_SOUTH = INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y0_NORTH
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y2_SOUTH = INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y1_NORTH
INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y2_SOUTH = INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y1_NORTH

ANCHOR_PBLOCK_ISLAND_X0Y0_EAST = 'SLICE_X118Y16:SLICE_X119Y239'
ANCHOR_PBLOCK_ISLAND_X0Y1_EAST = 'SLICE_X117Y240:SLICE_X119Y479'
ANCHOR_PBLOCK_ISLAND_X0Y2_EAST = 'SLICE_X118Y480:SLICE_X119Y719'

ANCHOR_PBLOCK_ISLAND_X1Y0_WEST = ANCHOR_PBLOCK_ISLAND_X0Y0_EAST
ANCHOR_PBLOCK_ISLAND_X1Y1_WEST = ANCHOR_PBLOCK_ISLAND_X0Y1_EAST
ANCHOR_PBLOCK_ISLAND_X1Y2_WEST = ANCHOR_PBLOCK_ISLAND_X0Y2_EAST

ISLAND_TO_DIR_TO_ANCHOR_PBLOCK = {
  'WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11': {
    'EAST': ANCHOR_PBLOCK_ISLAND_X0Y2_EAST,
    'SOUTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y2_SOUTH,
  },
  'WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7': {
    'NORTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y1_NORTH,
    'SOUTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y1_SOUTH,
    'EAST': ANCHOR_PBLOCK_ISLAND_X0Y1_EAST,
  },
  'WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3': {
    'NORTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X0Y0_NORTH,
    'EAST': ANCHOR_PBLOCK_ISLAND_X0Y0_EAST,
  },
  'WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11': {
    'WEST': ANCHOR_PBLOCK_ISLAND_X1Y2_WEST,
    'SOUTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y2_SOUTH,
  },
  'WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7': {
    'NORTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y1_NORTH,
    'WEST': ANCHOR_PBLOCK_ISLAND_X1Y1_WEST,
    'SOUTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y1_SOUTH,
  },
  'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3': {
    'NORTH': INIT_PLACEMENT_ANCHOR_PBLOCK_ISLAND_X1Y0_NORTH,
    'WEST': ANCHOR_PBLOCK_ISLAND_X1Y0_WEST,
  },
}

ISLAND_TO_PBLOCK = {
  'WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3': 'SLICE_X0Y16:SLICE_X116Y239 DSP48E2_X0Y2:DSP48E2_X15Y89 RAMB18_X0Y8:RAMB18_X7Y95 RAMB36_X0Y4:RAMB36_X7Y47 URAM288_X0Y8:URAM288_X1Y63',

  'WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7': 'SLICE_X0Y240:SLICE_X116Y479 DSP48E2_X0Y90:DSP48E2_X15Y185 RAMB18_X0Y96:RAMB18_X7Y191 RAMB36_X0Y48:RAMB36_X7Y95 URAM288_X0Y64:URAM288_X1Y127',

  'WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11': 'SLICE_X0Y480:SLICE_X116Y719 DSP48E2_X0Y186:DSP48E2_X15Y281 RAMB18_X0Y192:RAMB18_X7Y287 RAMB36_X0Y96:RAMB36_X7Y143 URAM288_X0Y128:URAM288_X1Y191',

  'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3': 'URAM288_X4Y16:URAM288_X4Y63 URAM288_X2Y4:URAM288_X3Y63 RAMB36_X11Y12:RAMB36_X11Y47 RAMB36_X8Y3:RAMB36_X10Y47 RAMB18_X11Y24:RAMB18_X11Y95 RAMB18_X8Y6:RAMB18_X10Y95 DSP48E2_X25Y18:DSP48E2_X27Y89 DSP48E2_X16Y0:DSP48E2_X24Y89 SLICE_X183Y60:SLICE_X191Y239 SLICE_X182Y60:SLICE_X182Y179 SLICE_X176Y60:SLICE_X181Y239 SLICE_X165Y15:SLICE_X175Y239 SLICE_X164Y15:SLICE_X164Y179 SLICE_X153Y15:SLICE_X163Y239 SLICE_X152Y15:SLICE_X152Y179 SLICE_X140Y15:SLICE_X151Y239 SLICE_X139Y15:SLICE_X139Y179 SLICE_X125Y15:SLICE_X138Y239 SLICE_X124Y15:SLICE_X124Y179 SLICE_X120Y15:SLICE_X123Y239',

  'WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7': 'URAM288_X2Y64:URAM288_X4Y127 RAMB36_X8Y48:RAMB36_X11Y95 RAMB18_X8Y96:RAMB18_X11Y191 DSP48E2_X28Y114:DSP48E2_X28Y161 DSP48E2_X16Y90:DSP48E2_X27Y185 SLICE_X192Y300:SLICE_X198Y419 SLICE_X183Y240:SLICE_X191Y479 SLICE_X182Y300:SLICE_X182Y419 SLICE_X165Y240:SLICE_X181Y479 SLICE_X164Y300:SLICE_X164Y419 SLICE_X153Y240:SLICE_X163Y479 SLICE_X152Y300:SLICE_X152Y419 SLICE_X140Y240:SLICE_X151Y479 SLICE_X139Y300:SLICE_X139Y419 SLICE_X125Y240:SLICE_X138Y479 SLICE_X124Y300:SLICE_X124Y419 SLICE_X120Y240:SLICE_X123Y479',

  'WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11': 'URAM288_X2Y128:URAM288_X4Y191 RAMB36_X8Y96:RAMB36_X11Y143 RAMB18_X8Y192:RAMB18_X11Y287 DSP48E2_X28Y210:DSP48E2_X28Y281 DSP48E2_X16Y186:DSP48E2_X27Y281 SLICE_X195Y540:SLICE_X200Y719 SLICE_X194Y540:SLICE_X194Y659 SLICE_X192Y540:SLICE_X193Y719 SLICE_X183Y480:SLICE_X191Y719 SLICE_X182Y540:SLICE_X182Y659 SLICE_X165Y480:SLICE_X181Y719 SLICE_X164Y540:SLICE_X164Y659 SLICE_X153Y480:SLICE_X163Y719 SLICE_X152Y540:SLICE_X152Y659 SLICE_X140Y480:SLICE_X151Y719 SLICE_X139Y540:SLICE_X139Y659 SLICE_X125Y480:SLICE_X138Y719 SLICE_X124Y540:SLICE_X124Y659 SLICE_X120Y480:SLICE_X123Y719'
}


def get_init_place_script(
    config: Dict,
    synth_dir: str,
    init_place_dir: str,
    hmss_shell_dir: str,
    top_name: str,
    slot_name: str,
    placement_strategy: str = 'Default',
    clock_period: float = 3,
) -> List[str]:
  """Note that EarlyBlockPlacement may cause placement error in DFX environment"""
  script = []
  synth_dcp = f'{synth_dir}/{slot_name}/{slot_name}_synth_opt.dcp'

  if slot_name == 'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3':
    script.append(f'open_checkpoint {hmss_shell_dir}')
    kernel_cell = f'pfm_top_i/dynamic_region/{top_name}/inst'
    kernel_cell_addr = f'{kernel_cell}/'
    script.append(f'read_checkpoint -cell {kernel_cell} {synth_dcp}')
  else:
    kernel_cell_addr = ''
    script.append(f'open_checkpoint {synth_dcp}')
    script.append(f'create_clock -name ap_clk -period {clock_period} [get_ports ap_clk]')
    script.append(f'set_property HD.CLK_SRC BUFGCE_X0Y194 [get_ports ap_clk]')


  # assign anchors to corresponding pblocks
  for orientation, wire_list in config['vertices'][slot_name]['orientation_to_wire'].items():
    script.append(f'create_pblock {orientation}')

    anchor_pblock = ISLAND_TO_DIR_TO_ANCHOR_PBLOCK[slot_name][orientation]
    script.append(f'resize_pblock {orientation} -add {{ {anchor_pblock} }}')

    script.append(f'add_cells_to_pblock {orientation} [ get_cells [ list \\')
    for name in wire_list:
      script.append(f'  {kernel_cell_addr}{name}_q_reg* \\')
    script.append(f'] ]')
    script.append('')

  script.append(f'create_pblock island')
  script.append(f'resize_pblock island -add {{ {ISLAND_TO_PBLOCK[slot_name]} }}')
  script.append(f'add_cells_to_pblock island [get_cells {kernel_cell_addr}{slot_name} ]')

  script.append(f'place_design -directive {placement_strategy}')

  # extract locations of src and dst of each anchor
  script.append(f'source /share/einsx7/vast-lab-tapa/RapidStream/tcl/extractSrcAndDstOfAnchors.tcl {kernel_cell_addr}')

  script.append(f'write_checkpoint {init_place_dir}/{slot_name}/{slot_name}_place.dcp')

  return script

def setup_island_init_placement(
    config: Dict,
    synth_dir: str,
    init_place_dir: str,
    hmss_shell_dir: str,
    top_name: str,
):
  """"""
  # create directories for initial placement
  os.makedirs(init_place_dir, exist_ok=True)
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{init_place_dir}/{slot_name}')

  mng = ParallelManager()

  # create pblock on each orientation, assign anchors to the pblocks
  for slot_name in config['vertices'].keys():
    script = get_init_place_script(config, synth_dir, init_place_dir, hmss_shell_dir, top_name, slot_name)
    open(f'{init_place_dir}/{slot_name}/{slot_name}_place.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{init_place_dir}/{slot_name}/', f'{slot_name}_place.tcl')

  open(f'{init_place_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))
