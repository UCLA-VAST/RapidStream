import os
from typing import Dict

from rapidstream.rtl_gen.top import get_top_with_one_island
from .util import ParallelManager


def get_synth_script(
    synth_dir,
    fpga_part_name,
    orig_rtl_path,
    slot_name):
  """Assume the top name is f"{slot_name}_backend_top" """
  top_name = f'{slot_name}_backend_top'
  backend_wrapper_file = f'{synth_dir}/{slot_name}/{slot_name}_backend_wrapper.v'

  script = []
  script.append(f'set_param general.maxThreads 8')
  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"')
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]')
  script.append(r'read_verilog ${orig_rtl_files}')

  # read in the backend top wrapper
  script.append(f'read_verilog {backend_wrapper_file}')

  # instantiate IPs used in the RTL. Use "-nocomplain" in case no IP is used
  script.append(r'set orig_ip_files [glob -nocomplain ${ORIG_RTL_PATH}/*.tcl]')
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }')

  # clock xdc
  script.append(f'read_xdc "{synth_dir}/clock.xdc"')

  script.append(f'synth_design -top "{top_name}" -part {fpga_part_name} -mode out_of_context')
  script.append(f'opt_design')

  # FIXME: remove abs path. add LUT1 to all un-used top ports (a DFX requirement)
  script.append('source /share/einsx7/vast-lab-tapa/RapidStream/tcl/insertFFToUnusedPorts.tcl')

  # reset clock because we will insert the checkpoint to DFX environment with pre-defined clocks
  script.append('reset_timing')

  script.append(f'write_checkpoint {synth_dir}/{slot_name}/{slot_name}_synth_opt.dcp')
  script.append(f'exec touch {synth_dir}/{slot_name}/{slot_name}_synth.dcp.done.flag')

  return script


def get_clock_xdc(target_period):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_ports ap_clk]')
  return xdc


def setup_island_synth(
    config: Dict,
    orig_rtl_path: str,
    synth_dir: str,
    clock_period: float = 3,
    use_anchor_wrapper: bool = True,
):
  """
  generate scripts to place & route each slot independently
  orig_rtl_path: rtl generated by vitis hls associated with each task
  wrapper_rtl_path: rapidstream-generated wrappers and the clock xdc
  """
  # create directories
  os.makedirs(synth_dir, exist_ok=True)
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{synth_dir}/{slot_name}')

  # create clock constraint file
  xdc = get_clock_xdc(clock_period)
  open(f'{synth_dir}/clock.xdc', 'w').write('\n'.join(xdc))

  mng = ParallelManager()

  # create Vivado script for each slot
  for slot_name in config['vertices'].keys():
    script = get_synth_script(
      synth_dir,
      config['part_num'],
      orig_rtl_path,
      slot_name)
    open(f'{synth_dir}/{slot_name}/{slot_name}_synth.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{synth_dir}/{slot_name}/', f'{slot_name}_synth.tcl')

  # get parallel synthesis files
  island_name_to_wrapper = get_top_with_one_island(config, use_anchor_wrapper)
  for name, wrapper in island_name_to_wrapper.items():
    open(f'{synth_dir}/{name}/{name}_backend_wrapper.v', 'w').write('\n'.join(wrapper))

  open(f'{synth_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))
