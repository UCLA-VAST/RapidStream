import logging
import json
import sys

def createFreeRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
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

  # write out results
  script.append(f'exec mkdir {output_path}/{slot_name}_placed_free_run')
  script.append(f'write_checkpoint {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp')
  script.append(f'write_edif {output_path}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.edf')
  
  # extract anchor placement
  script.append(f'source "{output_path}/{slot_name}_print_anchor_placement.tcl"')

  # routing
  script.append(f'source "{output_path}/{slot_name}_floorplan_routing_free_run.tcl"')
  script.append(f'route_design')
  script.append(f'phys_opt_design')

  # lock design
  script.append(f'lock_design -level routing')

  script.append(f'exec mkdir {output_path}/{slot_name}_routed_free_run')
  script.append(f'write_checkpoint -cell {slot_name}_U0 {output_path}/{slot_name}_routed_free_run/{slot_name}_routed_free_run.dcp')
  script.append(f'write_edif -cell {slot_name}_U0 {output_path}/{slot_name}_routed_free_run/{slot_name}_routed_free_run.edf')

  open(f'{output_path}/{slot_name}_free_run.tcl', 'w').write('\n'.join(script))

def createAnchoredRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
  script = []

  script.append(f'open_checkpoint {output_path}/{slot_name}_synth/{slot_name}_synth.dcp')
  
  # add floorplanning constraints for non-neighbor anchors
  script.append(f'source "{output_path}/{slot_name}_floorplan_placement_anchored_run.tcl"')

  script.append(f'opt_design')

  # place shared anchors between neighbors
  script.append(f'source "{output_path}/{slot_name}_place_anchors.tcl"')
  script.append(f'place_design -directive {placement_strategy}')
  script.append(f'phys_opt_design')

  script.append(f'exec mkdir {output_path}/{slot_name}_placed_anchored_run')
  script.append(f'write_checkpoint {output_path}/{slot_name}_placed_anchored_run/{slot_name}_placed_anchored_run.dcp')
  script.append(f'write_edif {output_path}/{slot_name}_placed_anchored_run/{slot_name}_placed_anchored_run.edf')

  # routing
  script.append(f'source "{output_path}/{slot_name}_floorplan_routing_anchored_run.tcl"')
  script.append(f'route_design')
  script.append(f'phys_opt_design')

  script.append(f'lock_design -level routing')

  script.append(f'exec mkdir {output_path}/{slot_name}_routed_anchored_run')
  script.append(f'write_checkpoint -cell {slot_name}_U0 {output_path}/{slot_name}_routed_anchored_run/{slot_name}_routed_anchored_run.dcp')
  script.append(f'write_edif -cell {slot_name}_U0 {output_path}/{slot_name}_routed_anchored_run/{slot_name}_routed_anchored_run.edf')

  open(f'{output_path}/{slot_name}_anchored_run.tcl', 'w').write('\n'.join(script))

def createVivadoRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_name,
    output_path='.',
    placement_strategy='Default'):
  createAnchoredRunScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)
  createFreeRunScript(fpga_part_name, orig_rtl_path, slot_name, output_path, placement_strategy)

def createClockXDC(
    slot_name, 
    output_path='.',
    target_period=3.33, 
    bufg='BUFGCE_X0Y194'):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_ports ap_clk]')
  xdc.append(f'set_property HD.CLK_SRC {bufg} [get_ports ap_clk]')
  open(f'{output_path}/{slot_name}_clk.xdc', 'w').write('\n'.join(xdc))

def createGNUParallelScript(hub, target_dir):
  free_run = []
  anchored_run = []
  for slot_name in hub['SlotIO'].keys():
    free_run.append(f'cd {target_dir}/{slot_name} && vivado -mode batch -source {slot_name}_free_run.tcl')
    anchored_run.append(f'cd {target_dir}/{slot_name} && vivado -mode batch -source {slot_name}_anchored_run.tcl')

  open(f'{target_dir}/parallel-free-run.txt', 'w').write('\n'.join(free_run))
  open(f'{target_dir}/parallel-anchored-run.txt', 'w').write('\n'.join(anchored_run))

  