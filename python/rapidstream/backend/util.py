import re
from typing import List, Tuple, Dict


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
