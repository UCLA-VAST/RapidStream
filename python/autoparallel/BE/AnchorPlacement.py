import logging
import json
import sys
import re

def __getSharedAnchorPlacement(hub, slot_name, backend_run_path):
  """
  In the anchored run, we first extract from neighbor DCPs where are the anchors placed
  Then we directly place those anchors at the exact same location
  As a result, the interface between neighbors will naturally align
  With routing inclusive wrappers, all anchors on each boundary will be shared by the neighbors
  """
  # get neighbors
  dir_to_neighbors = hub['Neighbors'][slot_name]
  dir_to_shared_anchors = hub['PathPlanningWire'][slot_name] # dir -> list of [i/o dir, width (if >1), name]

  anchor_name_to_loc = {}
  for dir, neighbor_slots in dir_to_neighbors.items():
    for neighbor_slot in neighbor_slots:
      # get their anchor placement result
      anchor_placement_json = f'{backend_run_path}/{neighbor_slot}/{neighbor_slot}_anchor_placement.json'
      anchor_placement = json.loads(open(anchor_placement_json, 'r').read())

      shared_anchors = []
      if f'{dir}_IN' in dir_to_shared_anchors:
        shared_anchors += dir_to_shared_anchors[f'{dir}_IN']
      if f'{dir}_OUT' in dir_to_shared_anchors:
        shared_anchors += dir_to_shared_anchors[f'{dir}_OUT']

      for io in shared_anchors:
        if len(io) == 2: # width == 1
          anchor_name = f'{io[-1]}_anchor_reg'

          assert anchor_name in anchor_placement, f'anchor {anchor_name} of slot {slot_name} not found in post-placement records'
          anchor_name_to_loc[anchor_name] = anchor_placement[anchor_name]
        else:
          # io[1] is a string of "[X:0]" or "[a-b:0]"
          width = int(eval(re.search('\[(.+):', io[1]).group(1)) )

          for i in range(width+1): # notice the +1 here
            anchor_name = f'{io[-1]}_anchor_reg[{i}]'

            assert anchor_name in anchor_placement, f'anchor {anchor_name} of slot {slot_name} not found in post-placement records'
            anchor_name_to_loc[anchor_name] = anchor_placement[anchor_name]

  return anchor_name_to_loc

def createAnchorPlacementScript(hub, slot_name, backend_run_path):
  tcl = []

  anchor_name_to_loc = __getSharedAnchorPlacement(hub, slot_name, backend_run_path)
  for anchor_name, loc in anchor_name_to_loc.items():
    # will cause problem in anchored-run. Laguna registers must exist in pair.
    assert 'LAGUNA' not in loc, f'Anchor registers should not be placed on Laguna sites'

    tcl.append(f'place_cell {anchor_name} {loc}')

    # fix the placement of anchors    
    tcl.append(f'set_property IS_BEL_FIXED 1 [get_cells {anchor_name}]')
    tcl.append(f'set_property IS_LOC_FIXED 1 [get_cells {anchor_name}]')

  file = open(f'{backend_run_path}/{slot_name}/{slot_name}_place_anchors.tcl', 'w')
  file.write('\n'.join(tcl))

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]  
  hub = json.loads(open(fe_result_path, 'r').read())
  
  for slot_name in hub['SlotIO'].keys():
    createAnchorPlacementScript(hub, slot_name, backend_run_dir)