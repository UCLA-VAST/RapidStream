import logging
import json
import sys
import os
from autoparallel.BE.CreateAnchorWrapper import getAnchoredIOAndWiredIO, getStrictAnchoredIO
from autoparallel.BE.LegalizeAnchorPlacement import getAnchorSourceNameFromFDRE
from autoparallel.BE.getGlobalClockRouting import setGlobalClockRoute

def getSlotAnchorPlacement(hub, slot_name, anchor_placement):
  """ get the locations of anchors of the current slot """

  in_slot_pipeline_style = hub['InSlotPipelineStyle']

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
  """ phys_opt_design the slot based on the dictated anchor locations """
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
  script.append('place_cell { \\')
  for FDRE, loc in local_anchor_placement.items():
    script.append(f'  {FDRE} {loc} \\')
  script.append('}')

  # get rid of the place holder LUTs
  if hub['InSlotPipelineStyle'] == 'LUT':
    script += removeLUTPlaceholders()

  # optimize the slot based on the given anchor placement
  # do placement only so that we could track the change from the log
  script.append(f'phys_opt_design -verbose')
  script.append(f'write_checkpoint -force {slot_name}_post_placed_opt.dcp')
  script.append(f'write_checkpoint -cell {slot_name}_U0 -force {slot_name}_ctrl_post_placed_opt.dcp')

  return script

def routeIncludeAnchorsFromMemory(slot_name, clock_route_path):
  """
  continue the routing task after post-placement phys_opt_design
  The anchor registers will be included in the final checkpoint
  """
  script = []

  # routing. Need to relax the pblocks to facilitate the routing near the boundary
  script.append(f'delete_pblock [get_pblocks *]')
  script.append(f'create_pblock {slot_name}')

  pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
  script.append(f'resize_pblock [get_pblocks {slot_name}] -add {pblock_def}')
  
  script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')
  # script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_U0]')
  script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] -top')

  # set up global clock network
  if clock_route_path:
    script += setGlobalClockRoute(clock_route_path)

  script.append(f'route_design')
  script.append(f'phys_opt_design')

  script.append(f'write_checkpoint -force {slot_name}_ctrl_final.dcp')

  return script

def routeWithoutAnchorsFromDCP(slot_name, clock_route_path):
  """
  start routing from the slot wrapper checkpoint
  the final result will not include the anchor registers
  """
  script = []

  # start with the ctrl wrapper
  script.append(f'open_checkpoint {slot_name}_ctrl_post_placed_opt.dcp')
  script.append(f'create_clock -name ap_clk -period 2.5 [get_ports ap_clk]')
  script.append(f'set_property HD.CLK_SRC BUFGCE_X0Y194 [get_ports ap_clk]')

  script += routeIncludeAnchorsFromMemory(slot_name, clock_route_path)

  return script

def removeLUTPlaceholders():
  """
  remove the placeholder luts
  """
  script = []
  script.append('set all_placeholder_luts [get_cells -hierarchical -filter { PRIMITIVE_TYPE == CLB.LUT.LUT1 && NAME =~  "*_lut*" } ]')
  script.append('foreach lut ${all_placeholder_luts} {set_property DONT_TOUCH 0 $lut}')
  script.append('foreach n [ get_nets -of_objects ${all_placeholder_luts} ] {set_property DONT_TOUCH 0 $n}')
  script.append('opt_design')

  return script

def generateParallelScript(hub, opt_dir):
  """
  summarize all tasks for gnu parallel
  """
  func_route = lambda opt_dir, slot_name : f'cd {opt_dir}/{slot_name} && VIV_VER=2020.1 vivado -mode batch -source {slot_name}_phys_opt_and_route.tcl'
  func_route_no_anchors = lambda opt_dir, slot_name : func_route(opt_dir, slot_name).replace('.tcl', '_without_anchors.tcl')
  
  slot_names = hub['SlotIO'].keys()
  open(f'{opt_dir}/parallel-opt-and-route.txt', 'w').write('\n'.join([func_route(opt_dir, n) for n in slot_names]))
  open(f'{opt_dir}/parallel-opt-and-route-no-anchor.txt', 'w').write('\n'.join([func_route_no_anchors(opt_dir, n) for n in slot_names]))

def generateOptScript(hub, parallel_run_dir, anchor_placement, clock_route_path):
  """
  setup the opt script for each slot
  """
  for slot_name in hub['SlotIO'].keys():
    slot_dir = f'{parallel_run_dir}/{slot_name}'
    slot_placement_dir = f'{slot_dir}/{slot_name}_placed_free_run'
    dcp_path = f'{slot_placement_dir}/{slot_name}_placed_free_run.dcp'

    slot_anchor_placement = getSlotAnchorPlacement(hub, slot_name, anchor_placement)

    # phys_opt_design the slot
    opt_script = getSlotPlacementOptScript(hub, slot_name, slot_anchor_placement, dcp_path)
    
    # continue routing 
    route_script = routeIncludeAnchorsFromMemory(slot_name, clock_route_path)

    # route from checkpoint & without anchors
    route_without_anchor = routeWithoutAnchorsFromDCP(slot_name, clock_route_path)

    open(f'{opt_dir}/{slot_name}/{slot_name}_phys_opt_and_route.tcl', 'w').write('\n'.join(opt_script + route_script))
    open(f'{opt_dir}/{slot_name}/{slot_name}_phys_opt_and_route_without_anchors.tcl', 'w').write('\n'.join(opt_script + route_without_anchor))
  
if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  
  parallel_run_dir = base_dir + '/parallel_run'

  final_stitch_run_dir = base_dir + '/parallel_stitch'
  final_anchor_placement_path = f'{final_stitch_run_dir}/finalized_anchor_placement.json'
  anchor_placement = json.loads(open(final_anchor_placement_path, 'r').read())

  hub = json.loads(open(hub_path, 'r').read())

  opt_dir = base_dir + '/opt_test'
  os.mkdir(opt_dir)
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{opt_dir}/{slot_name}')

  clock_route_path = base_dir + '/clock_routing' + '/clock_route.txt'

  generateOptScript(hub, parallel_run_dir, anchor_placement, clock_route_path)
  generateParallelScript(hub, opt_dir)