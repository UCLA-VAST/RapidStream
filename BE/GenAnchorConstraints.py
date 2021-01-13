#! /usr/bin/python3.6
import logging
import json
import re
import CreateAnchorWrapper

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

def printIOPlacement(hub, slot_name):
  tcl = []
  tcl.append(f'set fileId [open {slot_name}_anchor_placement.json "w"]')
  tcl.append('puts $fileId "{"')

  io_list = hub['SlotIO'][slot_name]
  print_cmd = r'catch {{ puts $fileId [format "  \"%s\" : \"%s/%s\"," {reg_name} [get_property LOC [get_cells {reg_name}]] [lindex [split [get_property BEL [get_cells {reg_name}]] "."] 1] ] }}'
  for io in io_list:
    if CreateAnchorWrapper.isCtrlIO(io[-1]):
      continue

    if len(io) == 2:
      tcl.append(print_cmd.format(reg_name = f'{io[1]}_anchor_reg'))
    elif len(io) == 3:
      width = int(eval(re.search('\[(.+):', io[1]).group(1)) )
      for i in range(width+1): # notice the +1 here
        tcl.append(print_cmd.format(reg_name = f'{io[2]}_anchor_reg[{i}]'))
    else:
      assert False

  # tcl.append(r'puts $fileId "  \"dummy\" : \"dummy\" "')
  tcl[-1] = tcl[-1].replace(',', '')
  tcl.append('puts $fileId "}"')
  tcl.append(f'close $fileId')

  open(f'{slot_name}_print_anchor_placement.tcl', 'w').write('\n'.join(tcl))

if __name__ == '__main__':
  hub = json.loads(open('BE_pass1_anchored.json', 'r').read())
  printIOPlacement(hub, 'CR_X0Y4_To_CR_X3Y7')