from typing import List, Tuple


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
