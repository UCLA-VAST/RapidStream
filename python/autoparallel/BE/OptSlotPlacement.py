import logging
import json
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
  script.append(f'lock_design -unlock -level logical') # seems that "-level placement" will trigger vivado bug

  # remove the pblocks for anchors
  # because some anchors will be placed inside the main pblock. Avoid potential conflict
  script.append(f'delete_pblocks [get_pblocks -filter {{ NAME !~ "*{slot_name}*"}} ]')
  script.append(f'set_property EXCLUDE_PLACEMENT 0 [get_pblocks {slot_name} ]')

  script.append(f'unplace_cell [get_cells -regexp .*_q0_reg.*]')

  # apply the placement of anchor registers
  for FDRE, loc in local_anchor_placement.items():
    script.append(f'place_cell {FDRE} {loc}')

  # optimize the slot based on the given anchor placement
  # do placement only so that we could track the change from the log
  script.append(f'phys_opt_design -placement_opt -verbose')
  script.append(f'write_checkpoint post_placed_opt.dcp')

  return script

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  hub_path = '/home/einsx7/auto-parallel/src/e2e_test/cnn_13x16_LUT_style/front_end_result.json'
  base_dir = '/expr/cnn_13x16_test_non_distribute_placement'
  final_stitch_run_dir = base_dir + '/parallel_stitch'
  parallel_run_dir = base_dir + '/parallel_run'
  final_anchor_placement_path = f'{final_stitch_run_dir}/finalized_anchor_placement.json'
  anchor_placement = json.loads(open(final_anchor_placement_path, 'r').read())

  hub = json.loads(open(hub_path, 'r').read())
  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  parallel_tasks = []
  for slot_name in hub['SlotIO'].keys():
    slot_dir = f'{parallel_run_dir}/{slot_name}'
    slot_placement_dir = f'{slot_dir}/{slot_name}_placed_free_run'
    dcp_path = f'{slot_placement_dir}/{slot_name}_placed_free_run.dcp'

    slot_anchor_placement = getSlotAnchorPlacement(hub, slot_name, anchor_placement, in_slot_pipeline_style)
    opt_script = getSlotPlacementOptScript(hub, slot_name, slot_anchor_placement, dcp_path)
    
    opt_script_path = f'{slot_dir}/{slot_name}_placed_free_run/placement_opt.tcl'
    open(opt_script_path, 'w').write('\n'.join(opt_script))

    parallel_tasks.append(f'cd {slot_dir}/{slot_name}_placed_free_run/ && VIV_VER=2020.1 vivado -mode batch -source placement_opt.tcl')
  
  open(f'{parallel_run_dir}/parallel_opt_placement.txt', 'w').write('\n'.join(parallel_tasks))