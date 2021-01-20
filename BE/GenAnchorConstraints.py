#! /usr/bin/python3.6
import logging
import json
import re
import CreateAnchorWrapper

# generate the Vivado script for each slot 
def createVivadoRunScript(
    fpga_part_name, 
    orig_rtl_path, 
    anchor_wrapper_path,
    slot_name,
    output_path='.'):
  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # instantiate IPs used in the RTL
  script.append(r'set orig_ip_files [glob ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # read in the new wrappers
  script.append(f'read_verilog "{anchor_wrapper_path}"')

  # clock xdc
  script.append(f'read_xdc "{output_path}/{slot_name}_clk.xdc"')

  # synth
  script.append(f'synth_design -top "{slot_name}_anchored" -part {fpga_part_name} -mode out_of_context')
  script.append(f'write_checkpoint ./{slot_name}_synth.dcp')
  script.append(f'write_edif ./{slot_name}_synth.edf')
  
  # add floorplanning constraints
  script.append(f'source "{output_path}/{slot_name}_floorplan.tcl"')
  
  # placement
  script.append(f'opt_design')
  script.append(f'place_design')
  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint ./{slot_name}_placed.dcp')
  script.append(f'write_edif ./{slot_name}_placed.edf')
  script.append(f'source "{output_path}/{slot_name}_print_anchor_placement.tcl"')

  # routing
  script.append(f'route_design')
  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint ./{slot_name}_routed.dcp')
  script.append(f'write_edif ./{slot_name}_routed.edf')

  open(f'{output_path}/{slot_name}_run.tcl', 'w').write('\n'.join(script))

def createClockXDC(
    slot_name, 
    output_path='.',
    target_period=3.0, 
    bufg='BUFGCE_X0Y194'):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_ports ap_clk]')
  xdc.append(f'set_property HD.CLK_SRC {bufg} [get_ports ap_clk]')
  open(f'{output_path}/{slot_name}_clk.xdc', 'w').write('\n'.join(xdc))

def createAnchorPlacementExtractScript(hub, slot_name, output_path):
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

  open(f'{output_path}/{slot_name}_print_anchor_placement.tcl', 'w').write('\n'.join(tcl))

def createPBlockScript(hub, slot_name, output_path='.'):
  tcl = []

  assert re.search(r'CR_X\d+Y\d+_To_CR_X\d+Y\d+', slot_name), f'unexpected format of the slot name {slot_name}'
  DL_x, DL_y, UR_x, UR_y = [int(val) for val in re.findall(r'[XY](\d+)', slot_name)] # DownLeft & UpRight

  slot_wires = hub['PathPlanningWire'][slot_name]

  def addPblock(dir, DL_x, DL_y, UR_x, UR_y):
    pblock_def = f'CLOCKREGION_X{DL_x}Y{DL_y}:CLOCKREGION_X{UR_x}Y{UR_y}'
    pblock_name = pblock_def.replace(':', '_To_')

    # no wire crossing in a certain boundary segment
    if dir != 'BODY' and f'{dir}_IN' not in slot_wires and f'{dir}_OUT' not in slot_wires:
      return

    tcl.append(f'\n# {dir} ')
    tcl.append(f'startgroup ')
    tcl.append(f'  create_pblock {pblock_name}')
    tcl.append(f'  resize_pblock [get_pblocks {pblock_name}] -add {pblock_def}')
    tcl.append(f'  set_property CONTAIN_ROUTING true [get_pblocks {pblock_name}] ')
    tcl.append(f'  set_property EXCLUDE_PLACEMENT true [get_pblocks {pblock_name}] ')
    tcl.append(f'endgroup')

    tcl.append(f'add_cells_to_pblock [get_pblocks {pblock_name}] [get_cells -regexp {{')
    if dir == 'BODY':
      tcl.append(f'  CR_X{DL_x}Y{DL_y}_To_CR_X{UR_x}Y{UR_y}_U0')
    else:
      
      pblock_wires = []
      if f'{dir}_IN' in slot_wires:
        pblock_wires.extend(slot_wires[f'{dir}_IN'])
      if f'{dir}_OUT' in slot_wires:
        pblock_wires.extend(slot_wires[f'{dir}_OUT'])

      for wire in pblock_wires:
        tcl.append(f'  {wire}.*')
    tcl.append(f'}}] -clear_locs ')

  # constrain body
  addPblock('BODY', DL_x, DL_y, UR_x, UR_y)

  # constrain up
  if UR_y < int(hub['CR_NUM_Y']):
    addPblock('UP', DL_x, UR_y+1, UR_x, UR_y+1)

  # down
  if DL_y > 0:
    addPblock('DOWN', DL_x, DL_y-1, UR_x, DL_y-1)
    
  # right
  if UR_x < int(hub['CR_NUM_X']):
    addPblock('RIGHT', UR_x+1, DL_y, UR_x+1, UR_y)

  # left
  if DL_x > 0:
    addPblock('LEFT', DL_x-1, DL_y, DL_x-1, UR_y)

  open(f'{output_path}/{slot_name}_floorplan.tcl', 'w').write('\n'.join(tcl))

def createGNUParallelScript(hub, target_dir):
  gnu_parallel = []
  for slot_name in hub['SlotIO'].keys():
    gnu_parallel.append(f'cd {target_dir}/{slot_name} && vivado -mode batch -source {slot_name}_run.tcl')
  
  open(f'{target_dir}/parallel.txt', 'w').write('\n'.join(gnu_parallel))

if __name__ == '__main__':
  hub = json.loads(open('BE_pass1_anchored.json', 'r').read())
  createPBlockScript(hub, 'CR_X0Y4_To_CR_X3Y7')