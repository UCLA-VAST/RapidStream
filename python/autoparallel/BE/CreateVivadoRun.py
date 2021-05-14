import logging
import json
import sys
import math
import re

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
  script.append(f'synth_design -top "{slot_name}_anchored" -part {fpga_part_name} -mode out_of_context')
  script.append(f'write_checkpoint {output_path}/{slot_name}_synth/{slot_name}_synth.dcp')
  script.append(f'write_edif {output_path}/{slot_name}_synth/{slot_name}_synth.edf')
  
  # add floorplanning constraints
  script.append(f'source "{output_path}/{slot_name}_floorplan_placement_free_run.tcl"')
  
  # placement
  script.append(f'opt_design')
  script.append(f'place_design -directive {placement_strategy}')
  script.append(f'phys_opt_design')

  # lock design
  script.append(f'lock_design -level placement')

  # write out the ctrl wrapper only
  script.append(f'exec mkdir {output_path}/{slot_name}_placed_free_run')
  script.append(f'write_checkpoint -cell {slot_name}_U0 {output_path}/{slot_name}_placed_free_run/{slot_name}_ctrl_placed_free_run.dcp')
  script.append(f'write_edif -cell {slot_name}_U0 {output_path}/{slot_name}_placed_free_run/{slot_name}_ctrl_placed_free_run.edf')
  
  # write out the whole anchored slot
  script.append(f'write_checkpoint {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp')
  script.append(f'write_edif {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.edf')

  script.append(f'exec touch {output_path}/{slot_name}_placed_free_run/{slot_name}.placement.done.flag') # signal that the DCP generation is finished

  return script

def getRoutingScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
  """ continue with the getPlacemetnScript, finish routing"""

  script = []

  # adjust the pblocks
  script.append(f'source "{output_path}/{slot_name}_floorplan_routing_free_run.tcl"')

  script.append(f'route_design')
  script.append(f'phys_opt_design')

  # lock design before writing to checkpoint
  script.append(f'lock_design -unlock -level placement')

  # write out the inner compute wrapper
  script.append(f'exec mkdir {output_path}/{slot_name}_routed_free_run')
  script.append(f'write_checkpoint -cell {slot_name}_U0 {output_path}/{slot_name}_routed_free_run/{slot_name}_ctrl_routed_free_run.dcp')
  script.append(f'write_edif -cell {slot_name}_U0 {output_path}/{slot_name}_routed_free_run/{slot_name}_ctrl_routed_free_run.edf')
  
  # write out the whole anchored slot
  script.append(f'write_checkpoint {output_path}/{slot_name}_routed_free_run/{slot_name}_routed_free_run.dcp')
  script.append(f'write_edif {output_path}/{slot_name}_routed_free_run/{slot_name}_routed_free_run.edf')

  script.append(f'exec touch {output_path}/{slot_name}_routed_free_run/{slot_name}.routing.done.flag') # signal that the DCP generation is finished

  return script

def getRouteFromDCPScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
  """ open checkpoint then do routing"""
  script = []

  script.append(f'open_checkpoint {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp')

  script += getRoutingScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)

  return script

def createVivadoRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):

  placement_script = getPlacementScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)
  routing_script = getRoutingScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)
  routing_from_dcp_script = getRouteFromDCPScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)

  open(f'{output_path}/{slot_name}_place.tcl', 'w').write('\n'.join(placement_script))
  open(f'{output_path}/{slot_name}_place_and_route.tcl', 'w').write('\n'.join(placement_script + routing_script))
  open(f'{output_path}/{slot_name}_route_from_dcp.tcl', 'w').write('\n'.join(routing_from_dcp_script))

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
    place_and_route.append(f'cd {target_dir}/{slot_name} && {vivado_command} {slot_name}_place_and_route.tcl')
    route_from_dcp.append(f'cd {target_dir}/{slot_name} && {vivado_command} {slot_name}_route_from_dcp.tcl')

  open(f'{target_dir}/parallel-place-all.txt', 'w').write('\n'.join(place))
  open(f'{target_dir}/parallel-place-and-route-all.txt', 'w').write('\n'.join(place_and_route))
  open(f'{target_dir}/parallel-route-from-dcp-all.txt', 'w').write('\n'.join(route_from_dcp))

  