import logging
import json
import sys
import os
from autoparallel.BE.CreateAnchorWrapper import getAnchoredIOAndWiredIO, getStrictAnchoredIO
from autoparallel.BE.LegalizeAnchorPlacement import getAnchorSourceNameFromFDRE

def getSlotAnchorPlacement(hub, slot_name, anchor_placement, in_slot_pipeline_style):
  """ get the locations of anchors of the current slot """

  if  in_slot_pipeline_style == 'LUT' or \
      in_slot_pipeline_style == 'WIRE' or \
      in_slot_pipeline_style == 'DOUBLE_REG':
    anchored_io = getAnchoredIOAndWiredIO(hub, slot_name) # note that passing wires are also anchored
  elif in_slot_pipeline_style == 'REG':
    anchored_io = getStrictAnchoredIO(hub, slot_name)
  else:
    assert False

  anchor_names = set(io[-1]+'_q0' for io in anchored_io)

  local_anchor_placement = {}
  for FDRE, loc in anchor_placement.items():
    anchor_source_name = getAnchorSourceNameFromFDRE(FDRE)
    if anchor_source_name in anchor_names:
      local_anchor_placement[FDRE] = loc

  return local_anchor_placement
  
def getSlotPlacementOptScript(hub, slot_name, local_anchor_placement, dcp_path):
  """ optimize the placement of the slot based on the dictated anchor locations """
  script = []

  script.append(f'open_checkpoint {dcp_path}')

  # allow modification
  # should unlock before modifying the pblocks, otherwise vivado may crash
  script.append(f'lock_design -unlock -level placement') # seems that "-level placement" will trigger vivado bug

  # remove the pblocks for anchors
  # because some anchors will be placed inside the main pblock. Avoid potential conflict
  # script.append(f'delete_pblocks [get_pblocks -filter {{ NAME !~ "*{slot_name}*"}} ]')
  script.append(f'set_property EXCLUDE_PLACEMENT 0 [get_pblocks {slot_name} ]')

  script.append(f'unplace_cell [get_cells -regexp .*_q0_reg.*]')

  # apply the placement of anchor registers
  for FDRE, loc in local_anchor_placement.items():
    script.append(f'place_cell {FDRE} {loc}')

  # get rid of the place holder LUTs
  if hub['InSlotPipelineStyle'] == 'LUT':
    script += removeLUTPlaceholders()

  # optimize the slot based on the given anchor placement
  # do placement only so that we could track the change from the log
  script.append(f'phys_opt_design -verbose')
  script.append(f'write_checkpoint -force {slot_name}_post_placed_opt.dcp')

  # routing. Need to relax the pblocks to facilitate the routing near the boundary
  script.append(f'delete_pblock [get_pblocks *]')
  script.append(f'create_pblock {slot_name}')

  pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
  script.append(f'resize_pblock [get_pblocks {slot_name}] -add {pblock_def}')
  
  script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')
  script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_U0]')

  script.append(f'route_design')
  script.append(f'phys_opt_design')

  script.append(f'write_checkpoint -force {slot_name}_final.dcp')

  return script

def removeLUTPlaceholders():
  script = []
  script.append('set all_placeholder_luts [get_cells -hierarchical -filter { PRIMITIVE_TYPE == CLB.LUT.LUT1 && NAME =~  "*_lut*" } ]')
  script.append('foreach lut ${all_placeholder_luts} {set_property DONT_TOUCH 0 $lut}')
  script.append('foreach n [ get_nets -of_objects ${all_placeholder_luts} ] {set_property DONT_TOUCH 0 $n}')
  script.append('opt_design')

  return script

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  
  final_stitch_run_dir = base_dir + '/parallel_stitch'
  parallel_run_dir = base_dir + '/parallel_run'
  final_anchor_placement_path = f'{final_stitch_run_dir}/finalized_anchor_placement.json'
  anchor_placement = json.loads(open(final_anchor_placement_path, 'r').read())
  hub = json.loads(open(hub_path, 'r').read())
  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  opt_dir = base_dir + '/opt_iter1'
  os.mkdir(opt_dir)
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{opt_dir}/{slot_name}')

  parallel_tasks = []
  for slot_name in hub['SlotIO'].keys():
    slot_dir = f'{parallel_run_dir}/{slot_name}'
    slot_placement_dir = f'{slot_dir}/{slot_name}_placed_free_run'
    dcp_path = f'{slot_placement_dir}/{slot_name}_placed_free_run.dcp'

    slot_anchor_placement = getSlotAnchorPlacement(hub, slot_name, anchor_placement, in_slot_pipeline_style)
    opt_script = getSlotPlacementOptScript(hub, slot_name, slot_anchor_placement, dcp_path)
    
    open(f'{opt_dir}/{slot_name}/{slot_name}_placement_opt.tcl', 'w').write('\n'.join(opt_script))

    parallel_tasks.append(f'cd {opt_dir}/{slot_name} && VIV_VER=2020.1 vivado -mode batch -source {slot_name}_placement_opt.tcl')
  
  open(f'{opt_dir}/parallel-opt-placement.txt', 'w').write('\n'.join(parallel_tasks))