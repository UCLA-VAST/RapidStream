import click
import json
import os
import shutil
from typing import Dict


@click.command()
@click.option(
  '--config-path',
  required=True,
  help='Path to the TAPA configuration file.'
)
@click.option(
  '--nested-dfx-generation-dir',
  required=True,
)
@click.option(
  '--dummy-wrapper-rtl-dir',
  required=True,
)
@click.option(
  '--top-name',
  required=True,
)
@click.option(
  '--hmss-shell-dcp-path',
  required=True,
)
def setup_nested_dfx(
    config_path: str,
    nested_dfx_generation_dir: str,
    dummy_wrapper_rtl_dir: str,
    top_name: str,
    hmss_shell_dcp_path: str,
    device: str = 'xcu280-fsvh2892-2L-e',
):
  config_path = os.path.abspath(config_path)
  config = json.loads(open(config_path, 'r').read())

  setup_nested_dfx_inner(
    config,
    nested_dfx_generation_dir,
    dummy_wrapper_rtl_dir,
    top_name,
    hmss_shell_dcp_path,
    device,
  )


def setup_nested_dfx_inner(
    config: Dict,
    nested_dfx_generation_dir: str,
    dummy_wrapper_rtl_dir: str,
    top_name: str,
    hmss_shell_dcp_path: str,
    device: str = 'xcu280-fsvh2892-2L-e',
):
  nested_dfx_generation_dir = os.path.abspath(nested_dfx_generation_dir)
  dummy_wrapper_rtl_dir = os.path.abspath(dummy_wrapper_rtl_dir)
  hmss_shell_dcp_path = os.path.abspath(hmss_shell_dcp_path)

  script = []

  # synthesize top with dummy islands
  script += get_synth_dummy_islands_script(dummy_wrapper_rtl_dir, top_name, device)
  dummy_island_dcp_name = 'top_with_dummy_islands_synth.dcp'
  script.append(f'write_checkpoint {dummy_island_dcp_name}')

  kernel_cell = f'pfm_top_i/dynamic_region/{top_name}/inst'

  # create next level dfx
  script.append(f'open_checkpoint {hmss_shell_dcp_path}')
  script.append(f'pr_subdivide -cell {kernel_cell} -subcells {{')
  for slot_name in config['vertices'].keys():
    script.append(f'  {kernel_cell}/{slot_name}')
  script.append(f'}} {dummy_island_dcp_name}')
  script.append(f'write_checkpoint {nested_dfx_generation_dir}/after_pr_subdivide.dcp')

  if os.path.exists(nested_dfx_generation_dir):
    shutil.rmtree(nested_dfx_generation_dir)
  os.mkdir(nested_dfx_generation_dir)
  open(f'{nested_dfx_generation_dir}/setup_nested_dfx.tcl', 'w').write('\n'.join(script))


def get_synth_dummy_islands_script(
    dummy_wrapper_rtl_dir: str,
    top_name: str,
    device: str,
):
  script = []

  script.append(f'set_part {device}')
  script.append(f'set rtl_files [glob {dummy_wrapper_rtl_dir}/*.v]')
  script.append(f'read_verilog ${{rtl_files}}')
  script.append(f'synth_design -top "{top_name}" -part {device} -mode out_of_context')
  return script


if __name__ == '__main__':
  setup_nested_dfx()
