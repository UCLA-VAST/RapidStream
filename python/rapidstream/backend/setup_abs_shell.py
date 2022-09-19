import os
import shutil
from typing import Dict, List

from .util import ParallelManager


def setup_abs_shell(
  config: Dict,
  overlay_dir: str,
  abs_shell_dir: str,
  top_name: str,
):
  overlay_dir = os.path.abspath(overlay_dir)
  abs_shell_dir = os.path.abspath(abs_shell_dir)

  if os.path.exists(abs_shell_dir):
    shutil.rmtree(abs_shell_dir)
  os.mkdir(abs_shell_dir)

  mng = ParallelManager()
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{abs_shell_dir}/{slot_name}')

    script = []
    script.append(f'open_checkpoint {overlay_dir}/overlay.dcp')
    script.append(f'set_param hd.absShellCreationIgnoreDRC true')
    script.append(f'catch {{ write_abstract_shell -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {slot_name}_abs_shell.dcp }}')

    open(f'{abs_shell_dir}/{slot_name}/gen_abs_shell.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{abs_shell_dir}/{slot_name}/', 'gen_abs_shell.tcl')

  open(f'{abs_shell_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))
