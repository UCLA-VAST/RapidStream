import logging
import os
from typing import Dict, List

from .util import ParallelManager
from .floorplan_const import *

_logger = logging.getLogger().getChild(__name__)


def get_init_place_script(
    config: Dict,
    synth_dir: str,
    init_place_dir: str,
    dummy_abs_shell_dir: str,
    top_name: str,
    slot_name: str,
    placement_strategy: str = '',
) -> List[str]:
  """Note that EarlyBlockPlacement may cause placement error in DFX environment"""
  script = []
  synth_dcp = f'{synth_dir}/{slot_name}/{slot_name}_synth_opt.dcp'

  script.append(f'open_checkpoint {dummy_abs_shell_dir}/{slot_name}/{slot_name}_abs_shell.dcp')
  kernel_cell = f'pfm_top_i/dynamic_region/{top_name}/inst/{slot_name}'
  kernel_cell_addr = f'{kernel_cell}/'
  script.append(f'read_checkpoint -cell {kernel_cell} {synth_dcp}')

  # remove partial reconfiguration settings so it runs faster in placement
  script.append(f'delete_pblock {slot_name}')
  script.append(f'set_property HD.RECONFIGURABLE 0 [get_cells {kernel_cell}]')

  # assign anchors to corresponding pblocks
  for orientation, wire_list in config['vertices'][slot_name]['orientation_to_wire'].items():
    script.append(f'create_pblock {orientation}')
    script.append(f'set_property IS_SOFT false [get_pblocks {orientation}]')
    # note: use EXCLUDE_PLACEMENT will make it extremely slow

    anchor_pblock = ISLAND_TO_DIR_TO_ANCHOR_PBLOCK[slot_name][orientation]
    script.append(f'resize_pblock {orientation} -add {{ {anchor_pblock} }}')

    # with the dummy abs shell, somehow forcing anchors onto lagunas will fail DRC check
    # for now, lets allow the anchors to be placed onto the slices beside the laguan column
    additional_slice_pblock = ISLAND_TO_DIR_TO_SLICES_BESIDE_LAGUNAS[slot_name][orientation]
    if additional_slice_pblock:
      script.append(f'resize_pblock {orientation} -add {{ {additional_slice_pblock} }}')

    script.append(f'add_cells_to_pblock {orientation} [ get_cells [ list \\')
    for name in wire_list:
      script.append(f'  {kernel_cell_addr}{name}_q_reg* \\')
    script.append(f'] ]')
    script.append('')

  script.append(f'create_pblock island')
  script.append(f'resize_pblock island -add {{ {ISLAND_TO_PBLOCK[slot_name]} }}')
  script.append(f'resize_pblock island -remove {{ {SLICE_COLUMNS_BESIDES_LAGUNS} }}')
  script.append(f'add_cells_to_pblock island [get_cells {kernel_cell_addr}{slot_name} ]')
  script.append(f'set_property IS_SOFT false [get_pblocks island]')

  # for better routability. Also PR flow will prohibit those rows for placement
  for row_idx in SLICE_ROWS_ON_SLR_BOUNDARIES:
    script.append(f'set_property PROHIBIT 1 [get_sites SLICE_X*Y{row_idx} -filter {{IS_USED == 0}}]')

  if placement_strategy:
    assert placement_strategy.startswith('-directive ')
  script.append(f'place_design {placement_strategy}')

  # remove the prohibit property after placement
  for row_idx in SLICE_ROWS_ON_SLR_BOUNDARIES:
    script.append(f'set_property PROHIBIT 0 [get_sites SLICE_X*Y{row_idx}]')

  # extract locations of src and dst of each anchor
  script.append(f'set kernel_cell_addr "{kernel_cell_addr}"')
  script.append(f'source /share/einsx7/vast-lab-tapa/RapidStream/tcl/extractSrcAndDstOfAnchors.tcl')

  script.append(f'write_checkpoint {init_place_dir}/{slot_name}/{slot_name}_place.dcp')

  return script

def setup_island_init_placement(
    config: Dict,
    synth_dir: str,
    init_place_dir: str,
    dummy_abs_shell_dir: str,
    top_name: str,
):
  """"""
  # create directories for initial placement
  os.makedirs(init_place_dir, exist_ok=True)
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{init_place_dir}/{slot_name}')

  mng = ParallelManager()

  # create pblock on each orientation, assign anchors to the pblocks
  _logger.info(f'using dummy abs shell in: {dummy_abs_shell_dir}')
  for slot_name in config['vertices'].keys():
    script = get_init_place_script(config, synth_dir, init_place_dir, dummy_abs_shell_dir, top_name, slot_name)
    open(f'{init_place_dir}/{slot_name}/{slot_name}_place.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{init_place_dir}/{slot_name}/', f'{slot_name}_place.tcl')

  open(f'{init_place_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))
