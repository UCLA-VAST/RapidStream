import logging
import json
import sys

def __getSharedAnchorPlacement(hub, slot_name, backend_run_path):
  # get neighbors
  dir_to_neighbors = hub['Neighbors'][slot_name]
  dir_to_shared_anchors = hub['SharedAnchors'][slot_name] # dir -> wire name -> width

  anchor_name_to_loc = {}
  for dir, neighbor_slots in dir_to_neighbors.items():
    for neighbor_slot in neighbor_slots:
      # get their anchor placement result
      anchor_placement_json = f'{backend_run_path}/{neighbor_slot}/{neighbor_slot}_anchor_placement.json'
      anchor_placement = json.loads(open(anchor_placement_json, 'r').read())

      shared_anchors = {}
      if f'{dir}_IN' in dir_to_shared_anchors:
        shared_anchors.update(dir_to_shared_anchors[f'{dir}_IN'])
      if f'{dir}_OUT' in dir_to_shared_anchors:
        shared_anchors.update(dir_to_shared_anchors[f'{dir}_OUT'])

      for anchor, width in shared_anchors.items():
        if width == 1:
          anchor_name = f'{anchor}_anchor_reg'

          assert anchor_name in anchor_placement, f'anchor {anchor_name} of slot {slot_name} not found in post-placement records'
          anchor_name_to_loc[anchor_name] = anchor_placement[anchor_name]
        else:
          for i in range(width):
            anchor_name = f'{anchor}_anchor_reg[{i}]'

            assert anchor_name in anchor_placement, f'anchor {anchor_name} of slot {slot_name} not found in post-placement records'
            anchor_name_to_loc[anchor_name] = anchor_placement[anchor_name]

  return anchor_name_to_loc

def createAnchorPlacementScript(hub, slot_name, backend_run_path):
  tcl = []

  anchor_name_to_loc = __getSharedAnchorPlacement(hub, slot_name, backend_run_path)
  for anchor_name, loc in anchor_name_to_loc.items():
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