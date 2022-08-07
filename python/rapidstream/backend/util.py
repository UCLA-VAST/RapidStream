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
