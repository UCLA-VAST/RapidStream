#! /usr/bin/python3.6
import logging
import json
import re
from autoparallel.BE import CreateAnchorWrapper

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

def __generateConstraints(pblock_name, pblock_def, targets, comments = []):
  tcl = []
  tcl += comments
  tcl.append(f'\nstartgroup ')
  tcl.append(f'  create_pblock {pblock_name}')
  tcl.append(f'  resize_pblock [get_pblocks {pblock_name}] -add {pblock_def}')
  tcl.append(f'  set_property CONTAIN_ROUTING true [get_pblocks {pblock_name}] ')
  tcl.append(f'  set_property EXCLUDE_PLACEMENT true [get_pblocks {pblock_name}] ')
  tcl.append(f'endgroup')

  tcl.append(f'add_cells_to_pblock [get_pblocks {pblock_name}] [get_cells -regexp {{')
  for target in targets:
    tcl.append(f'  {target}')
  tcl.append(f'}}] -clear_locs ')

  return tcl

def __constrainSlotBody(hub, slot_name, output_path = '.'):
  pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
  pblock_name = slot_name
  targets = [f'{slot_name}_U0']
  comments = ['# Slot Body']
  return __generateConstraints(pblock_name, pblock_def, targets, comments)

def __constrainSlotWires(hub, slot_name, output_path = '.', exclude_shared_anchor = False):
  assert re.search(r'CR_X\d+Y\d+_To_CR_X\d+Y\d+', slot_name), f'unexpected format of the slot name {slot_name}'
  DL_x, DL_y, UR_x, UR_y = [int(val) for val in re.findall(r'[XY](\d+)', slot_name)] # DownLeft & UpRight

  tcl = []
    
  # constrain up
  if UR_y < int(hub['CR_NUM_Y']):
    tcl += __constraintBoundary(hub, slot_name, 'UP', DL_x, UR_y+1, UR_x, UR_y+1, exclude_shared_anchor)

  # down
  if DL_y > 0:
    tcl += __constraintBoundary(hub, slot_name, 'DOWN', DL_x, DL_y-1, UR_x, DL_y-1, exclude_shared_anchor)
    
  # right
  if UR_x < int(hub['CR_NUM_X']):
    tcl += __constraintBoundary(hub, slot_name, 'RIGHT', UR_x+1, DL_y, UR_x+1, UR_y, exclude_shared_anchor)

  # left
  if DL_x > 0:
    tcl += __constraintBoundary(hub, slot_name, 'LEFT', DL_x-1, DL_y, DL_x-1, UR_y, exclude_shared_anchor)

  return tcl
  
def __constraintBoundary(hub, slot_name, dir, DL_x, DL_y, UR_x, UR_y, exclude_shared_anchor):
  slot_wires = hub['PathPlanningWire'][slot_name]
  # no wire crossing in a certain boundary segment
  if f'{dir}_IN' not in slot_wires and f'{dir}_OUT' not in slot_wires:
    return []

  shared_anchors = hub['SharedAnchors'][slot_name]

  # all interface wires
  def getPblockWires(dir):
    pblock_wires = []
    if f'{dir}_IN' in slot_wires:
      pblock_wires += slot_wires[f'{dir}_IN']
    if f'{dir}_OUT' in slot_wires:
      pblock_wires += slot_wires[f'{dir}_OUT']
    
    assert pblock_wires # empty boundary should not appear in the json 
    return pblock_wires

  # exclude wires to immediate neighbors
  def getPblockWiresWithoutSharedAnchors(dir):
    pblock_wires = []
    if f'{dir}_IN' in slot_wires:
      pblock_wires += [wire for wire in slot_wires[f'{dir}_IN'] \
        if wire not in shared_anchors[f'{dir}_IN'] ]
    if f'{dir}_OUT' in slot_wires:
      pblock_wires += [wire for wire in slot_wires[f'{dir}_OUT'] \
        if wire not in shared_anchors[f'{dir}_OUT'] ]

    return pblock_wires    

  if exclude_shared_anchor:
    pblock_wires = getPblockWiresWithoutSharedAnchors(dir)
    if not pblock_wires:
      logging.warning(f'All wires are shared anchors of {slot_name} in boundary {dir}')
      return []
  else:
    pblock_wires = getPblockWires(dir)

  # generate the script
  pblock_def = f'CLOCKREGION_X{DL_x}Y{DL_y}:CLOCKREGION_X{UR_x}Y{UR_y}'
  pblock_name = pblock_def.replace(':', '_To_')
  targets = [f'{wire}.*' for wire in pblock_wires]
  comments = [f'\n# {dir} ']
  return __generateConstraints(pblock_name, pblock_def, targets, comments)

def createPBlockScript(hub, slot_name, output_path='.'):
  tcl = __constrainSlotBody(hub, slot_name, output_path)
  tcl_free_run = tcl + __constrainSlotWires(hub, slot_name, output_path, exclude_shared_anchor=False)
  tcl_anchored_run = tcl + __constrainSlotWires(hub, slot_name, output_path, exclude_shared_anchor=True)

  open(f'{output_path}/{slot_name}_floorplan_free_run.tcl', 'w').write('\n'.join(tcl_free_run))
  open(f'{output_path}/{slot_name}_floorplan_anchored_run.tcl', 'w').write('\n'.join(tcl_anchored_run))

if __name__ == '__main__':
  hub = json.loads(open('BE_pass1_anchored.json', 'r').read())
  createPBlockScript(hub, 'CR_X0Y4_To_CR_X3Y7')