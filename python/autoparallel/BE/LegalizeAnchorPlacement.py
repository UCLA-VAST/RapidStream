import logging
import json
import glob
from autoparallel.BE.CreatePairwiseWrapper import getTopIOAndInnerConnectionOfPair, getConnection

def createAnchorAdjustmentScript(
    hub,
    slot1_name, 
    slot2_name,
    wrapper_name,
    global_anchor_reg2loc, 
    global_conflict_anchor_reg2loc,
    output_dir):
  """
  for the given pair, determine which anchors are in valid position
  and which ones are in conflict with others
  In the wrapper we only include anchors between the two slots
  Here we also include anchors between each of the slot with other slots outside
  We create a placeholder cell for each of those anchors to prevent further conflict
  At this point, only the conflict anchors between the two slots are unplaced
  Run placement again to determine their new location, which should resolve the confliction
  """
  assert len(global_anchor_reg2loc.values()) == len(set(global_anchor_reg2loc.values()))

  # get the anchors between the two slots
  wrapper_io, inner_connection = getTopIOAndInnerConnectionOfPair(hub, slot1_name, slot2_name)
  _, local_anchors = getConnection(inner_connection, pipeline_level=1)
  local_anchor_names = [anchor[-1] for anchor in local_anchors]

  # get the anchors beween either slot with other slots outside the wrapper
  top_ports = hub['TopIO']
  extern_anchor_names = [f'{io_name}_q0' for io_name in wrapper_io if io_name not in top_ports]

  # get the valid anchor placement
  # note that each anchor corresponds to multiple 1-bit registers
  # with suffix "_reg[...]"
  # note that we must not use '_reg[' to split, because 1-bit variables does not have '[...]' at the end
  def extract_anchor_name(netlist_name):
    if netlist_name.endswith('_reg'):
      return netlist_name[:-4]
    else:
      assert '_reg[' in netlist_name
      return netlist_name.split('_reg[')[0]

  local_anchor_reg2loc = {reg : loc for reg, loc in global_anchor_reg2loc.items() \
                          if extract_anchor_name(reg) in local_anchor_names}

  # get the placement of external anchors, i.e. between on slot and outside
  extern_anchor_reg2loc = {reg : loc for reg, loc in global_anchor_reg2loc.items() \
                          if extract_anchor_name(reg) in extern_anchor_names}

  # get which anchors are in conflict and their locations
  local_conflict_anchor_reg2loc = {reg : loc for reg, loc in global_conflict_anchor_reg2loc.items() \
                          if extract_anchor_name(reg) in local_anchor_names}

  if local_conflict_anchor_reg2loc:
    script = []

    logging.info(f'{wrapper_name} needs anchor adjustments')

    # unplace the anchors with conflict. Should be very small
    for reg, loc in local_conflict_anchor_reg2loc.items():
      script.append(f'unplace_cell {reg} ;# unplace conflict anchors')
      script.append(f'create_cell -reference FDRE placeholder_{reg}')
      # we want a placeholder to block this position
      # but this may cause conflict if we later want to block positions held by external anchors
      # so we push it to the end and wrap it with catch {}
      # script.append(f'place_cell placeholder_{reg} {loc}') 

    # dictate the placement of valid anchors
    for reg, loc in local_anchor_reg2loc.items():
      script.append(f'place_cell {reg} {loc} ;# place valid anchors')

    # create placeholders for external anchors. Split the loop for locality concern
    for reg, loc in extern_anchor_reg2loc.items():
      script.append(f'create_cell -reference FDRE placeholder_{reg} ;# placeholder for extern anchors')
    for reg, loc in extern_anchor_reg2loc.items():
      script.append(f'place_cell placeholder_{reg} {loc} ;# placeholder for extern anchors')

    # block the previous conflict position if it has not been so.
    for reg, loc in local_conflict_anchor_reg2loc.items():
      script.append(f'catch {{ place_cell placeholder_{reg} {loc} }}') 

    script.append('place_design')

    # remove the placeholder cells
    script.append('remove_cell [get_cells -regexp placeholder.*]')

    script.append(f'source {wrapper_name}_print_anchor_placement.tcl')
    script.append(f'write_checkpoint {wrapper_name}_placed_adjusted.dcp')

    open(f'{output_dir}/anchor_adjustment.tcl', 'w').write('\n'.join(script))

def collisionDetection(stitch_run_dir):
  """
  collect the anchor placement from each slot pair
  filter valid ones and conflict ones
  """
  json_list = glob.glob(f'{stitch_run_dir}/*/*.json')

  # a list of dict, each is the pipeline reg -> location mapping of a slot pair
  reg2loc_list = [json.loads(open(f, 'r').read()) for f in json_list]

  # inversed mapping
  loc2reg_list = [{loc : reg for reg, loc in reg2loc.items()} for reg2loc in reg2loc_list]

  # check if the same location occurs more than once
  global_anchor_loc2reg = {}
  global_conflict_anchor_loc2regs = {}
  for loc2reg in loc2reg_list:
    for loc, reg in loc2reg.items():
      # found a collision
      if loc in global_anchor_loc2reg:
        conflict_reg = global_anchor_loc2reg[loc]
        if loc not in global_conflict_anchor_loc2regs:
          global_conflict_anchor_loc2regs[loc] = [conflict_reg]
        global_conflict_anchor_loc2regs[loc].append(reg)
      else:
        global_anchor_loc2reg[loc] = reg

  # convert data format
  global_anchor_reg2loc = {reg : loc for loc, reg in global_anchor_loc2reg.items()}
  global_conflict_anchor_reg2loc = {}
  for loc, regs in  global_conflict_anchor_loc2regs.items():
    global_conflict_anchor_reg2loc.update({reg : loc for reg in regs})

  logging.info(json.dumps(global_conflict_anchor_reg2loc, indent=2))
  logging.info(f'conflict rate: {len(global_conflict_anchor_loc2regs)} / {len(global_anchor_loc2reg) + len(global_conflict_anchor_loc2regs)} = {len(global_conflict_anchor_loc2regs) / (len(global_anchor_loc2reg)+len(global_conflict_anchor_loc2regs))} ')

  return global_anchor_reg2loc, global_conflict_anchor_reg2loc
  
