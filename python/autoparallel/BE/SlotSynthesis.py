import json
import logging
import math
import os
import sys

from autoparallel.BE.UniversalWrapperCreater import addAnchorToNonTopIOs


def getAnchorWrapperOfSlot(hub, slot_name):
  """
  Top-level ports will be directly connected
  All other IOs will be registered
  """
  slot_to_io = hub['SlotIO']
  slot_to_rtl = hub['SlotWrapperRTL']
  io_list = slot_to_io[slot_name]

  wrapper = addAnchorToNonTopIOs(hub, f'{slot_name}_ctrl', io_list)

  # add the rtl for the inner module (the slot wrapper)
  # discard the first line (time scale)
  assert 'timescale' in slot_to_rtl[slot_name][0]
  wrapper.append('\n\n')
  wrapper += slot_to_rtl[slot_name][1:]

  return wrapper


def createClockFromBUFGXDC(target_period=2.50):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_pins test_bufg/O]')
  return xdc


def getSynthScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name):
  """ stop at placement """

  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # read in the generated wrappers
  script.append(f'set WRAPPER_PATH "{synth_dir}/{slot_name}/rtl"') 
  script.append(r'set wrapper_files [glob ${WRAPPER_PATH}/*.v]') 
  script.append(r'read_verilog ${wrapper_files}') 

  # instantiate IPs used in the RTL. Use "-nocomplain" in case no IP is used
  script.append(r'set orig_ip_files [glob -nocomplain ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # clock xdc
  script.append(f'read_xdc "{synth_dir}/clock.xdc"')

  # synth
  script.append(f'synth_design -top "{slot_name}_ctrl_anchored" -part {fpga_part_name} -mode out_of_context')

  script.append(f'write_checkpoint {synth_dir}/{slot_name}/{slot_name}_synth.dcp')
  script.append(f'exec touch {synth_dir}/{slot_name}/{slot_name}_synth.dcp.done.flag')

  return script


def setupSlotSynthesis():
  """
  generate scripts to place & route each slot independently
  """
  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']
  assert os.path.isdir(orig_rtl_path)

  xdc = createClockFromBUFGXDC()
  open(f'{synth_dir}/clock.xdc', 'w').write('\n'.join(xdc))  
  
  # note that pure routing slots are also implemented separately
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{synth_dir}/{slot_name}')
    os.mkdir(f'{synth_dir}/{slot_name}/rtl')
    
    # get anchored wrapper
    slot_wrapper_rtl = getAnchorWrapperOfSlot(hub, slot_name)  
    open(f'{synth_dir}/{slot_name}/rtl/{slot_name}_anchored.v', 'w').write('\n'.join(slot_wrapper_rtl))

    # create pblock constraints for each anchored wrapper
    # createPBlockScript(hub, slot_name, output_path=dir)

    # create Vivado script for each slot
    script = getSynthScript(fpga_part_name, 
                          orig_rtl_path, 
                          slot_name)
    open(f'{synth_dir}/{slot_name}/{slot_name}_synth.tcl', 'w').write('\n'.join(script))


def generateParallelScript(hub, user_name, server_list):
  """
  summarize all tasks for gnu parallel
  fire as soon as the neighbor anchors are ready
  """
  all_tasks = []
  slot_names = hub['SlotIO'].keys()

  for slot_name in slot_names:
    vivado = f'VIV_VER={VIV_VER} vivado -mode batch -source {slot_name}_synth.tcl'
    
    # broadcast the results
    transfer = []
    for server in server_list:
      transfer.append(f'rsync -azh --delete -r {synth_dir}/{slot_name}/ {user_name}@{server}:{synth_dir}/{slot_name}/')
    transfer_str = "&&".join(transfer)

    command = f'cd {synth_dir}/{slot_name} && {vivado} && {transfer_str}'
    all_tasks.append(command)

  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]
    open(f'{synth_dir}/parallel-synth-{server}.txt', 'w').write('\n'.join(local_tasks))


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())

  synth_dir = f'{base_dir}/slot_synth'
  os.mkdir(synth_dir)

  VIV_VER='2021.1'

  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']

  setupSlotSynthesis()
  generateParallelScript(hub, user_name, server_list)