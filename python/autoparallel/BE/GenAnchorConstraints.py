#! /usr/bin/python3.6
import logging
import json
import re
from autoparallel.BE import CreateAnchorWrapper
from autobridge.Device import DeviceManager

def createAnchorPlacementExtractScript(slot_name, io_list, output_dir):
  """
  after the free run, extract the placement of anchor registers
  create a script for vivado to print the information into a json file
  """
  tcl = []
  tcl.append(f'set fileId [open {slot_name}_anchor_placement.json "w"]')
  tcl.append('puts $fileId "{"')

  print_cmd = r'catch {{ puts $fileId [format "  \"%s\" : \"%s/%s\"," {reg_name} [get_property LOC [get_cells {reg_name}]] [lindex [split [get_property BEL [get_cells {reg_name}]] "."] 1] ] }}'
  for io in io_list:
    if CreateAnchorWrapper.isCtrlIO(io[-1]):
      continue

    if len(io) == 2: # width of io is 1 so the width info is not shown
      tcl.append(print_cmd.format(reg_name = f'{io[1]}_reg')) # append the suffix "_reg" according to vivado naming convention
    elif len(io) == 3:
      width = int(eval(re.search('\[(.+):', io[1]).group(1)) )
      for i in range(width+1): # notice the +1 here
        tcl.append(print_cmd.format(reg_name = f'{io[2]}_reg[{i}]'))
    else:
      assert False

  # tcl.append(r'puts $fileId "  \"dummy\" : \"dummy\" "')
  tcl[-1] = tcl[-1].replace(',', '')
  tcl.append('puts $fileId "}"')
  tcl.append(f'close $fileId')

  open(f'{output_dir}/{slot_name}_print_anchor_placement.tcl', 'w').write('\n'.join(tcl))

def __generateConstraints(pblock_name, pblock_def, targets, comments = [], contain_routing = 1, exclude_laguna = False):
  tcl = []
  tcl += comments
  tcl.append(f'\nstartgroup ')
  tcl.append(f'  create_pblock {pblock_name}')
  tcl.append(f'  resize_pblock [get_pblocks {pblock_name}] -add {{ {pblock_def} }}')
  tcl.append(f'  set_property CONTAIN_ROUTING {contain_routing} [get_pblocks {pblock_name}] ')
  tcl.append(f'  set_property EXCLUDE_PLACEMENT 1 [get_pblocks {pblock_name}] ')

  # keep anchor registers from being placed to laguna 
  if exclude_laguna:
    tcl.append(f'  resize_pblock [get_pblocks {pblock_name}] -remove LAGUNA_X0Y0:LAGUNA_X31Y839')
  tcl.append(f'endgroup')

  tcl.append(f'add_cells_to_pblock [get_pblocks {pblock_name}] [get_cells -regexp {{')
  for target in targets:
    tcl.append(f'  {target}')
  tcl.append(f'}}] -clear_locs ')

  return tcl

def __constrainSlotBody(hub, slot_name, output_path = '.', step = 'ROUTE'):
  pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
  pblock_name = slot_name
  targets = [f'{slot_name}_U0']
  comments = ['# Slot Body']

  # FIXME: only support U250 for now
  if step == 'PLACE':
    assert 'xcu250' in hub['FPGA_PART_NAME'] 
    pblock_def = DeviceManager.DeviceU250.shrinkClockRegionPblock(pblock_def)
  return __generateConstraints(pblock_name, pblock_def, targets, comments)

def __constrainSlotWires(hub, slot_name, output_path = '.'):
  assert re.search(r'CR_X\d+Y\d+_To_CR_X\d+Y\d+', slot_name), f'unexpected format of the slot name {slot_name}'
  DL_x, DL_y, UR_x, UR_y = [int(val) for val in re.findall(r'[XY](\d+)', slot_name)] # DownLeft & UpRight

  tcl = []
    
  # constrain up
  if UR_y < int(hub['CR_NUM_Y']):
    tcl += __constraintBoundary(hub, slot_name, 'UP', DL_x, UR_y+1, UR_x, UR_y+1)

  # down
  if DL_y > 0:
    tcl += __constraintBoundary(hub, slot_name, 'DOWN', DL_x, DL_y-1, UR_x, DL_y-1)
    
  # right
  if UR_x < int(hub['CR_NUM_X']):
    tcl += __constraintBoundary(hub, slot_name, 'RIGHT', UR_x+1, DL_y, UR_x+1, UR_y)

  # left
  if DL_x > 0:
    tcl += __constraintBoundary(hub, slot_name, 'LEFT', DL_x-1, DL_y, DL_x-1, UR_y)

  return tcl
  
def __constraintBoundary(hub, slot_name, dir, DL_x, DL_y, UR_x, UR_y):
  slot_wires = hub['PathPlanningWire'][slot_name]
  # no wire crossing in a certain boundary segment
  if f'{dir}_IN' not in slot_wires and f'{dir}_OUT' not in slot_wires:
    return []

  # all interface wires
  pblock_wires = []
  if f'{dir}_IN' in slot_wires:
    pblock_wires += slot_wires[f'{dir}_IN']
  if f'{dir}_OUT' in slot_wires:
    pblock_wires += slot_wires[f'{dir}_OUT']
  
  assert pblock_wires, f'empty boundary should not appear in the json: {slot_name} -> {dir}' 

  # generate the script
  pblock_def = f'CLOCKREGION_X{DL_x}Y{DL_y}:CLOCKREGION_X{UR_x}Y{UR_y}'
  pblock_name = pblock_def.replace(':', '_To_')
  targets = [f'{wire[-1]}.*' for wire in pblock_wires]
  comments = [f'\n# {dir} ']
  return __generateConstraints(pblock_name, pblock_def, targets, comments, exclude_laguna=True)

def createPBlockScript(hub, slot_name, output_path='.'):
  """
  Need to separately constrain the slot itself and the peripheral anchor registers
  To facilitate routing, the pblock for the slot is smaller in placement
  If we do not use a routing wrapper, then not all anchors are shared between neighbors
  As a result, in the anchored-run, we first place the shared anchors, then set a coarse-grained constraint on the remaining anchors
  Now that we switch to routing-inclusive wrappers, all anchors will be shared with neighbors.
  Thus in a anchored run we only need to constrain the slot body itself. The anchor registesr will be directly placed at specific location.
  FIXME: it is possible that anchors have conflict placement because the pblocks have overlaps. Though it is tentative whether we need anchored-run at all.
  """
  common = ['delete_pblock [get_pblocks *]'] # in case duplicated definition

  constraint_body_place = __constrainSlotBody(hub, slot_name, output_path, 'PLACE')
  constraint_body_route = __constrainSlotBody(hub, slot_name, output_path, 'ROUTE')

  constrain_slot_free_run = __constrainSlotWires(hub, slot_name, output_path)

  with open(f'{output_path}/{slot_name}_floorplan_placement_free_run.tcl', 'w') as fp1:
    fp1.write('\n'.join(
      common + constraint_body_place + constrain_slot_free_run))
    fp1.close()
  with open(f'{output_path}/{slot_name}_floorplan_placement_anchored_run.tcl', 'w') as fp2:
    fp2.write('\n'.join(
      common + constraint_body_place))
    fp2.close()
  with open(f'{output_path}/{slot_name}_floorplan_routing_free_run.tcl', 'w') as fp3:
    fp3.write('\n'.join(
      common + constraint_body_route + constrain_slot_free_run))
    fp3.close()
  with open(f'{output_path}/{slot_name}_floorplan_routing_anchored_run.tcl', 'w') as fp4:
    fp4.write('\n'.join(
      common + constraint_body_route))
    fp4.close()

if __name__ == '__main__':
  hub = json.loads(open('BE_pass1_anchored.json', 'r').read())
  createPBlockScript(hub, 'CR_X0Y4_To_CR_X3Y7')