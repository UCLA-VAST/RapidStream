import logging
import json
import sys
import math
import re
import os

from autoparallel.BE.Utilities import getAnchorTimingReportScript, getAnchorConectionExtractionScript


def getPlacementScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
  """ stop at placement """

  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # read in the generated wrappers
  script.append(f'set WRAPPER_PATH "{output_path}/rtl"') 
  script.append(r'set wrapper_files [glob ${WRAPPER_PATH}/*.v]') 
  script.append(r'read_verilog ${wrapper_files}') 

  # instantiate IPs used in the RTL. Use "-nocomplain" in case no IP is used
  script.append(r'set orig_ip_files [glob -nocomplain ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # clock xdc
  script.append(f'read_xdc "{output_path}/{slot_name}_clk.xdc"')

  # synth
  script.append(f'exec mkdir {output_path}/{slot_name}_synth')
  script.append(f'synth_design -top "{slot_name}_ctrl_anchored" -part {fpga_part_name} -mode out_of_context')
  script.append(f'write_checkpoint {output_path}/{slot_name}_synth/{slot_name}_synth.dcp')
  # script.append(f'write_edif {output_path}/{slot_name}_synth/{slot_name}_synth.edf')
  
  # add floorplanning constraints
  script.append(f'source "{output_path}/{slot_name}_floorplan_placement_free_run.tcl"')
  
  # placement
  script.append(f'opt_design')
  script.append(f'place_design -directive {placement_strategy}')
  script.append(f'phys_opt_design')

  # lock design
  script.append(f'lock_design -level placement')

  # write out the ctrl wrapper only for anchor placement
  script.append(f'exec mkdir {output_path}/{slot_name}_placed_free_run')
  script.append(f'write_checkpoint -cell {slot_name}_ctrl_U0 {output_path}/{slot_name}_placed_free_run/{slot_name}_ctrl_placed_free_run.dcp')
  # script.append(f'write_edif -cell {slot_name}_U0 {output_path}/{slot_name}_placed_free_run/{slot_name}_ctrl_placed_free_run.edf')
  
  # write out the whole anchored slot
  script.append(f'write_checkpoint {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp')
  # script.append(f'write_edif {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.edf')

  # print out anchor connections for customized ILP anchor placement
  script += getAnchorConectionExtractionScript()

  # get the timing report of anchors. At this point the timing report is meaningless
  # however, we use the report to extract the number of LUTs on the timing paths
  script += getAnchorTimingReportScript()

  # flag to signal the end of process
  script.append(f'exec touch anchor_connections.json.done.flag')

  script.append(f'exec touch {output_path}/{slot_name}_placed_free_run/{slot_name}.placement.done.flag') # signal that the DCP generation is finished

  open(f'{output_path}/{slot_name}_place.tcl', 'w').write('\n'.join(script))


def createClockXDC(
    slot_name, 
    output_path='.',
    target_period=2.50, 
    bufg='BUFGCE_X0Y194'):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_ports ap_clk]')
  xdc.append(f'set_property HD.CLK_SRC {bufg} [get_ports ap_clk]')
  open(f'{output_path}/{slot_name}_clk.xdc', 'w').write('\n'.join(xdc))

def createClockFromBUFGXDC(
    slot_name, 
    output_path='.',
    target_period=2.50, 
    bufg='BUFGCE_X0Y194'):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_pins test_bufg/O]')
  open(f'{output_path}/{slot_name}_clk.xdc', 'w').write('\n'.join(xdc))

def createGNUParallelScript(hub, target_dir):
  place = []
  place_and_route = []
  route_from_dcp = []

  vivado_command = 'VIV_VER=2020.1 vivado -mode batch -source'
  for slot_name in hub['SlotIO'].keys():
    place.append(f'cd {target_dir}/{slot_name} && {vivado_command} {slot_name}_place.tcl')

  open(f'{target_dir}/parallel-place-all.txt', 'w').write('\n'.join(place))


def createMultiServerExecution(hub, target_dir, user_name, server_list):
  """
  spread the tasks to multiple servers
  broadcast the results to all servers
  """
  place = []
  vivado_command = 'VIV_VER=2020.1 vivado -mode batch -source'
  for slot_name in hub['SlotIO'].keys():
    command = f'cd {target_dir}/{slot_name}/ && {vivado_command} {slot_name}_place.tcl'

    # broadcast the results to all servers
    for server in server_list:
      command += f' && rsync -azh --delete -r {target_dir}/{slot_name}/ {user_name}@{server}:{target_dir}/{slot_name}/'

    place.append(command)

  num_job_server = math.ceil(len(place) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = place[i * num_job_server: (i+1) * num_job_server]
    open(f'{target_dir}/parallel-place-all-{server}.txt', 'w').write('\n'.join(local_tasks))