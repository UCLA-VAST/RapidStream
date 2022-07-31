import os
from typing import Dict, List


def get_init_place_script(
    config: Dict,
    synth_dir: str,
    hmss_shell_dir: str,
    top_name: str,
    slot_name: str,
    placement_strategy: str = 'EarlyBlockPlacement'
) -> List[str]:
  """"""
  script = []

  script.append(f'open_checkpoint {hmss_shell_dir}')

  bb_cell = f'pfm_top_i/dynamic_region/{top_name}/inst'
  synth_dcp = f'{synth_dir}/{slot_name}/{slot_name}_synth_opt.dcp'
  script.append(f'read_checkpoint -cell {bb_cell} {synth_dcp}')

  # assign anchors to corresponding pblocks
  for orientation, dir_to_name_to_width in config['vertices'][slot_name][
      'orientation_to_dir_to_io_name_to_width'
  ].items():
    script.append(f'create_pblock {orientation}')
    script.append(f'add_cells_to_pblock {orientation} [ get_cells [ list \\')
    for name_to_width in dir_to_name_to_width.values():
      for name in name_to_width.keys():
        script.append(f'  {bb_cell}/{name}_q_reg* \\')
    script.append(f'] ]')
    script.append('')

  script.append(f'place_design -directive {placement_strategy}')
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

  # create pblock on each orientation, assign anchors to the pblocks
  for slot_name in config['vertices'].keys():
    script = get_init_place_script(config, synth_dir, hmss_shell_dir, top_name, slot_name)
    open(f'{init_place_dir}/{slot_name}/{slot_name}_place.tcl', 'w').write('\n'.join(script))

  # TODO: determine the range of each pblock
