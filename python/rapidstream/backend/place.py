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
    script.append(f'set_property IS_SOFT false [get_pblocks {orientation}]')

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
  script.append(f'set kernel_cell_addr "{kernel_cell_addr}"')
  script.append(f'source /share/einsx7/vast-lab-tapa/RapidStream/tcl/extractSrcAndDstOfAnchors.tcl')

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
  _logger.info(f'using hmss shell: {hmss_shell_dir}')
  for slot_name in config['vertices'].keys():
    script = get_init_place_script(config, synth_dir, init_place_dir, hmss_shell_dir, top_name, slot_name)
    open(f'{init_place_dir}/{slot_name}/{slot_name}_place.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{init_place_dir}/{slot_name}/', f'{slot_name}_place.tcl')

  open(f'{init_place_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))
