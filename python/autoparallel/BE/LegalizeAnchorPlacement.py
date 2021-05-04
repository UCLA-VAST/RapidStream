import logging
import json
import glob
from autoparallel.BE.CreatePairwiseWrapper import getTopIOAndInnerConnectionOfPair, getConnection

def getAnchorSourceNameFromFDRE(FDRE_name):
  """
  get the valid anchor placement
  note that each anchor corresponds to multiple 1-bit registers
  with suffix "_reg[...]"
  note that we must not use '_reg[' to split, because 1-bit variables does not have '[...]' at the end
  """
  if FDRE_name.endswith('_reg'):
    return FDRE_name[:-4]
  else:
    assert '_reg[' in FDRE_name
    return FDRE_name.split('_reg[')[0]

def createAnchorAdjustmentScript(
    hub,
    slot1_name, 
    slot2_name,
    wrapper_name,
    all_placed_anchor_reg2loc, 
    all_idle_anchor_reg2loc,
    pair_wrapper_proj_dir):
  """
  for the given pair, determine which anchors are in valid position
  and which ones are in conflict with others
  In the wrapper we only include anchors between the two slots
  Here we also include anchors between each of the slot with other slots outside
  We create a placeholder cell for each of those anchors to prevent further conflict
  At this point, only the conflict anchors between the two slots are unplaced
  Run placement again to determine their new location, which should resolve the confliction
  """
  assert len(all_placed_anchor_reg2loc.values()) == len(set(all_placed_anchor_reg2loc.values()))

  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  # get the anchors between the two slots
  wrapper_io, inner_connection = getTopIOAndInnerConnectionOfPair(hub, slot1_name, slot2_name)
  _, local_anchors = getConnection(inner_connection, 1, in_slot_pipeline_style)
  local_anchor_names = [anchor[-1] for anchor in local_anchors]

  # get the anchors beween either slot with other slots outside the wrapper
  top_ports = hub['TopIO']
  extern_anchor_names = [f'{io_name}_q0' for io_name in wrapper_io if io_name not in top_ports]

  local_anchor_reg2loc = {reg : loc for reg, loc in all_placed_anchor_reg2loc.items() \
                          if getAnchorSourceNameFromFDRE(reg) in local_anchor_names}

  # get the placement of external anchors, i.e. between on slot and outside
  extern_anchor_reg2loc = {reg : loc for reg, loc in all_placed_anchor_reg2loc.items() \
                          if getAnchorSourceNameFromFDRE(reg) in extern_anchor_names}

  # get which anchors are in conflict and their locations
  local_conflict_anchor_reg2loc = {reg : loc for reg, loc in all_idle_anchor_reg2loc.items() \
                          if getAnchorSourceNameFromFDRE(reg) in local_anchor_names}

  script = []

  if local_conflict_anchor_reg2loc:
    logging.info(f'{wrapper_name} needs to adjust {len(local_conflict_anchor_reg2loc)} anchor registers')

    script.append(f'open_checkpoint {wrapper_name}_placed.dcp')

    # unplace the anchors with conflict. Should be very small
    for reg, loc in local_conflict_anchor_reg2loc.items():
      script.append(f'unplace_cell {reg} ;# unplace conflict anchors')

    # dictate the placement of valid anchors
    for reg, loc in local_anchor_reg2loc.items():
      script.append(f'place_cell {reg} {loc} ;# place valid anchors')

    # create placeholders for external anchors. Split the loop for locality concern
    # if not, the replaced anchors may conflict again
    for reg, loc in extern_anchor_reg2loc.items():
      script.append(f'create_cell -reference FDRE placeholder_{reg} ;# placeholder for extern anchors')
    for reg, loc in extern_anchor_reg2loc.items():
      script.append(f'place_cell placeholder_{reg} {loc} ;# placeholder for extern anchors')

    # block the conflict location if they are not yet occupied by the considered external anchors
    for reg, loc in local_conflict_anchor_reg2loc.items():
      # check if this conflict location has been blocked.
      # note that the vivado command reference has an error. Should check the "IS_USED" property instead of the "IS_OCCUPIED" property
      script.append(f'if {{ [ get_property IS_USED [get_bels {loc} ] ] == 0 }} {{')
      script.append(f'  create_cell -reference FDRE placeholder_{reg} ;# placeholder for current conflict anchors')
      script.append(f'  place_cell placeholder_{reg} {loc} ;# unplace conflict anchors')
      script.append(f'}}')

    script.append(f'if {{ [llength [get_cells -filter {{STATUS != FIXED && PRIMITIVE_TYPE =~ REGISTER.*.*}} ] ] != {len(local_conflict_anchor_reg2loc)} }} {{puts "mismatch in unplaced anchors!"; exit(1)}}')
    script.append('place_design -directive Quick')

    # remove the placeholder cells
    script.append('remove_cell [get_cells -regexp placeholder.*]')

    script.append(f'source {pair_wrapper_proj_dir}/{wrapper_name}_print_anchor_placement.tcl')
    script.append(f'write_checkpoint -force {wrapper_name}_placed.dcp')

  return script

def getAllAnchorRegToLoc(stitch_run_dir):
  json_list = glob.glob(f'{stitch_run_dir}/*/*.json')
  reg2loc_list = [json.loads(open(f, 'r').read()) for f in json_list]
  all_anchor_reg2loc = {}
  for reg2loc in reg2loc_list:
    all_anchor_reg2loc.update(reg2loc)
  return all_anchor_reg2loc

def collisionDetection(stitch_run_dir):
  """
  collect the anchor placement from each slot pair
  filter valid ones and conflict ones
  """
  all_anchor_reg2loc = getAllAnchorRegToLoc(stitch_run_dir)

  occupied_locs = set()
  all_placed_anchor_reg2loc = {}
  all_idle_anchor_reg2loc = {}

  for reg, loc in all_anchor_reg2loc.items():
    if loc in occupied_locs:
      all_idle_anchor_reg2loc[reg] = loc
    else:
      occupied_locs.add(loc)
      all_placed_anchor_reg2loc[reg] = loc

  logging.info(json.dumps(all_idle_anchor_reg2loc, indent=2))

  # do it in another way to check
  num_unique_locs = len(set(all_anchor_reg2loc.values()))
  assert num_unique_locs == len(occupied_locs)
  num_total_anchors = len(all_anchor_reg2loc)

  logging.info(f'There are {num_total_anchors} anchors in total, {num_total_anchors-num_unique_locs} anchors are not placed, \
    {(num_total_anchors-num_unique_locs)/num_total_anchors}')

  return all_placed_anchor_reg2loc, all_idle_anchor_reg2loc

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  hub_path = '/home/einsx7/auto-parallel/src/e2e_test/cnn_13x16_LUT_style/front_end_result.json'
  base_dir = '/expr/cnn_13x16_test_non_distribute_placement'
  stitch_run_dir = base_dir + '/parallel_stitch'
  all_placed_anchor_reg2loc, all_idle_anchor_reg2loc = collisionDetection(stitch_run_dir)
  
  hub = json.loads(open(hub_path, 'r').read())

  pair_list = hub["AllSlotPairs"]

  task_queue = []
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    slot1_name = pair[0]
    slot2_name = pair[1]
    wrapper_name = f'{slot1_name}_AND_{slot2_name}'
    pair_wrapper_proj_dir = stitch_run_dir + '/' + wrapper_name

    script = createAnchorAdjustmentScript(
      hub,
      slot1_name, 
      slot2_name,
      wrapper_name,
      all_placed_anchor_reg2loc, 
      all_idle_anchor_reg2loc,
      pair_wrapper_proj_dir)

    if script:
      task_queue.append(f'cd {pair_wrapper_proj_dir} && VIV_VER=2020.1 vivado -mode batch -source anchor_adjustment.tcl')
      open(f'{pair_wrapper_proj_dir}/anchor_adjustment.tcl', 'w').write('\n'.join(script))

  open(f'{stitch_run_dir}/parallel-legalize.txt', 'w').write('\n'.join(task_queue))

  # visualize the distribution of conflicts
  show_conflict = open(f'{stitch_run_dir}/show_all_conflicts.tcl', 'w')
  for reg, loc in all_idle_anchor_reg2loc.items():
    show_conflict.write(f'create_cell -reference FDRE {reg}_test; catch {{ place_cell {reg}_test {loc} }} \n')

  if len(all_idle_anchor_reg2loc) == 0: 
    open(f'{stitch_run_dir}/finalized_anchor_placement.json', 'w').write(json.dumps(all_placed_anchor_reg2loc, indent=2))