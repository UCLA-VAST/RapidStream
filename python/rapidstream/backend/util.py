import json
import os
import re
from typing import List, Tuple, Dict

import rapidstream
RAPIDSTREAM_PYTHON_PATH = os.path.dirname(rapidstream.__file__)
RAPIDSTREAM_BASE_PATH = f'{RAPIDSTREAM_PYTHON_PATH}/../../'

class ParallelManager:
  def __init__(self):
    self.tasks: List[Tuple[str, str]] = []

  def add_task(self, work_dir, task):
    self.tasks.append((work_dir, task))

  def get_parallel_script(self, mode = 'batch') -> List[str]:
    """Assume each entry is [work-dir, tcl script]"""
    script = []
    for task in self.tasks:
      script.append(f'cd {task[0]}; vivado -mode {mode} -source {task[1]}')
    return script


def get_local_anchor_list(
  config: Dict,
  slot_name: str,
  orientation: str,
) -> List[str]:
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

  return local_anchor_list


LAGUNA_REG_Y_RANGE = [
  (0, 239),
  (240, 479),
]


def get_pairing_laguna_tx(rx_reg: str) -> str:
  """
  Laguna registers are pair by pair. Given an RX, find the corresponding TX
  """
  match = re.search(r'LAGUNA_X(\d+)Y(\d+)/RX_REG(\d)', rx_reg)
  assert match, f'wrong laguna location: {rx_reg}'

  x = int(match.group(1))
  y = int(match.group(2))
  reg = int(match.group(3))

  def get_ith_slr_boundary(laguna_y):
    for i in range(len(LAGUNA_REG_Y_RANGE)):
      curr_range = LAGUNA_REG_Y_RANGE[i]
      if curr_range[0] <= laguna_y <= curr_range[1]:
        return i

    return None

  if get_ith_slr_boundary(y) == get_ith_slr_boundary(y+120):
    return f'LAGUNA_X{x}Y{y+120}/TX_REG{reg}'
  elif get_ith_slr_boundary(y) == get_ith_slr_boundary(y-120):
    return f'LAGUNA_X{x}Y{y-120}/TX_REG{reg}'
  else:
    assert False


def collect_anchor_to_dir_to_locs(placement_dir: str):
  """
  anchor_to_info: {
    anchor_name: {
      'anchor_loc': xxx,
      'connections': [
        {
          'loc': xxx,
          'type': xxx,
          'name: xxx,
          'dir': xxx
        }, ...
      ]
    },
    ...
  }
  """

  def _get_correct_hier_name(orig_name: str) -> str:
    paths = orig_name.split('/')
    assert paths[-2] == paths[-3]
    new_paths = paths[:-2] + paths[-1:]
    return '/'.join(new_paths)

  anchor_to_dir_to_cells = {}

  # read in the six json file and merge them
  for root, dirs, files in os.walk(placement_dir):
    for file in files:
      if file.endswith('.json'):
        # anchor_name -> {'anchor_loc': xxx, 'connections': [{'name': xxx, 'dir': xxx, 'loc'; xxx}, xxx ] }
        anchor_info = json.loads(open(f'{root}/{file}', 'r').read())
        for anchor, info in anchor_info.items():
          anchor_loc = info['anchor_loc']

          # strip the path part
          cell_name = anchor.split('/')[-1]

          if cell_name not in anchor_to_dir_to_cells:
            anchor_to_dir_to_cells[cell_name] = {
              'anchor_loc': anchor_loc,
              'input': [],
              'output': [],
            }

          for cell in info['connections']:
            dir = cell.pop('dir')

            # FIXME: a temp hack to update cell names
            # now we use the dummy abstract shell for faster placement
            # the original hierarchy name, for example,
            # pfm_top_i/dynamic_region/gaussian_kernel/inst/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3/xxx_anchor_reg
            # becomes
            # pfm_top_i/dynamic_region/gaussian_kernel/inst/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3/xxx_anchor_reg
            # thus we need to remove the extra slot name before generating place_cell script for the final overlay.
            cell['name'] = _get_correct_hier_name(cell['name'])

            anchor_to_dir_to_cells[cell_name][dir] += [cell]

  return anchor_to_dir_to_cells


def mark_false_paths_to_placeholder_ff(slot_name: str) -> List[str]:
  script = []

  # use catch because in abstract shells, some FF will be unconnected, and set_false_path will trigger an ERROR
  # set false path from place holder FFs to top-level IOs
  script.append('set top_io_place_holder_ff [get_cells -hierarchical -regexp -filter { PRIMITIVE_TYPE =~ REGISTER.*.* && NAME =~  ".*_ff$.*" && NAME =~  ".*_axi_.*" } ]')
  script.append('if { [ llength ${top_io_place_holder_ff} ] > 0 } {')
  script.append('  catch { set_false_path -from [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*C"}] }')
  script.append('  catch { set_false_path -to [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*D"}] }')
  script.append('  catch { set_false_path -hold -from [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*C"}] }')
  script.append('  catch { set_false_path -hold -to [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*D"}] }')
  script.append('}')

  # set false path from place holder FFs in other islands
  # if an FDRE has _anchor_reg in its name, and does not have the slot name in its parent cell name
  # then it is a place holder FF in other islands
  script.append(f'set place_holder_ff [get_cells -hierarchical -regexp -filter {{ PRIMITIVE_TYPE =~ REGISTER.*.* && NAME =~  ".*_anchor_reg.*" && PARENT !~  ".*{slot_name}.*" }} ]')
  script.append('if { [ llength ${place_holder_ff} ] > 0 } {')
  script.append('  catch { set_false_path -from [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*C"}] }')
  script.append('  catch { set_false_path -to [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*D"}] }')
  script.append('  catch { set_false_path -hold -from [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*C"}] }')
  script.append('  catch { set_false_path -hold -to [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*D"}] }')
  script.append('}')

  return script
