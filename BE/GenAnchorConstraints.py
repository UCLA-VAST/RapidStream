#! /usr/bin/python3.6
import logging
import json

# generate the Vivado script for each slot 
def createVivadoRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    slot_wrapper_path,
    anchor_wrapper_path,
    clock_xdc_path,
    slot_name):
  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH {orig_rtl_path}') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # instantiate IPs used in the RTL
  script.append(r'set orig_ip_files [glob ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # read in the new wrappers
  script.append(f'read_verilog {anchor_wrapper_path}')

  # clock xdc
  script.append(f'read_xdc {clock_xdc_path}')

  # synth
  script.append(f'synth_design -top "{slot_name}_anchored" -part {fpga_part_name} -mode out_of_context')
  script.append(f'write_checkpoint ./{slot_name}_synth.dcp')
  
  # add floorplanning constraints
  script.append(f'source "{slot_name}_floorplan.tcl"')
  
  # placement and routing
  script.append(f'opt_design')
  script.append(f'place_design')
  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint ./{slot_name}_placed.dcp')
  script.append(f'route_design')
  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint ./{slot_name}_routed.dcp')

  open(f'{slot_name}_run.tcl', 'w').write('\n'.join(script))
