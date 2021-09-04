import argparse
import sys
import json
import os
import re
import math
from typing import List

import autoparallel.BE.Constants as Constants
from autoparallel.BE.Device import U250
from autoparallel.BE.GenAnchorConstraints import __getBufferRegionSize
from autoparallel.BE.Utilities import (
  getAnchorTimingReportScript,
  loggingSetup,
  getSlotIndicesFromSlotName,
  getSLRCrossingNeighbor,
)

loggingSetup()


def extractLagunaAnchorRoutes(slot_name):
  """
  record the ROUTE property of the nets to/from laguna anchors.
  Will reuse them later in the final stitch
  """
  script = []
  script.append(f'set target {slot_name}_ctrl_U0')
  script.append(
r'''
set laguna_anchors [get_cells -hierarchical -regexp -filter { LOC =~  ".*LAGUNA.*" } ]
set laguna_anchor_nets [get_nets  -regexp -top_net_of_hierarchical_group -filter { TYPE != "GROUND" && TYPE != "POWER" && NAME !~  ".*ap_clk.*" && ROUTE_STATUS != "HIERPORT" }  -of_objects ${laguna_anchors} ]
set file [open "add_${target}_laguna_route.tcl" "w"]
foreach net ${laguna_anchor_nets} {
  # check if the net connects to a laguna anchor
  set laguna_anchor [get_cells -of_objects [get_nets -segment $net] -filter {LOC =~ LAGUNA*}]
  if {$laguna_anchor != [] } {
    set net_route [get_property ROUTE $net]
    puts $file "set_property ROUTE ${net_route} \[get_nets ${net} \]"
  }
}
close $file
''')

  return script


def addSomeAnchors(hub, base_dir, slot_name_list: List[str]):
  """
  when route a slot, instantiate and place a subset of anchors, so that the tap of row buffers are closer to the real case.
  """
  pair_name_list = ['_AND_'.join(pair) for pair in hub["AllSlotPairs"]]
  get_create_anchor_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'
  script = ['set_property DONT_TOUCH 0 [get_nets ap_clk]']

  for pair_name in pair_name_list:
    if all(slot_name not in pair_name for slot_name in slot_name_list):
      if re.search(r'CR_X2Y\d+_To_CR_X3Y\d+_AND_CR_X4Y\d+_To_CR_X5Y\d+', pair_name):
        script.append(f'source -notrace {get_create_anchor_script(pair_name)}')

  return script


def addAllAnchors(hub, base_dir, slot_name_list: List[str]):
  """
  when route a slot, instantiate and place all anchors, so that the tap of row buffers are closer to the real case.
  """
  pair_name_list = ['_AND_'.join(pair) for pair in hub["AllSlotPairs"]]
  get_create_anchor_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'

  script = ['set_property DONT_TOUCH 0 [get_nets ap_clk]']
  script += [f'source -notrace {get_create_anchor_script(pair_name)}' \
    for pair_name in pair_name_list \
      if all(slot_name not in pair_name for slot_name in slot_name_list)]

  return script


def removePlaceholderAnchors():
  script = []
  script.append('set placeholder_FF [get_cells  -filter { DONT_TOUCH == "FALSE" && NAME =~ "*q0_reg*" } ]')
  script.append('set placeholder_FF_clock_pin [get_pins -filter { NAME =~ "*C" } -of_objects $placeholder_FF ]')
  script.append('disconnect_net -net [get_nets ap_clk] -objects $placeholder_FF_clock_pin')
  script.append('remove_cell $placeholder_FF')
  return script


def unrouteNonLagunaAnchorDPinQPinNets() -> List[str]:
  """
  unroute the D net and Q net of non-laguna anchors
  """
  script = []

  script.append('set non_laguna_anchors [get_cells  -filter { NAME =~  "*q0_reg*" && LOC !~  "*LAGUNA*" } ]')
  script.append('set non_laguna_anchor_nets [ get_nets -of_objects $non_laguna_anchors -filter { TYPE == "SIGNAL" && ROUTE_STATUS != "HIERPORT"} ]')
  script.append('set_property ROUTE "" $non_laguna_anchor_nets')

  return script


def addRoutingPblock(slot_name: str, enable_anchor_pblock: bool) -> List[str]:
    script = []

    pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
    
    detailed_pblock_def = U250.getDetailedRangeOfClockRegion(slot_name)
    slr_crossing_neighbor = getSLRCrossingNeighbor(hub, slot_name)
    if slr_crossing_neighbor:
      slr_crossing_neighbor_pblock_def = U250.getDetailedRangeOfClockRegion(slr_crossing_neighbor)

    # relax placement pblocks
    # do this before updating the clock to prevent vivado crash
    script.append(f'delete_pblock [get_pblocks *]')

    # first create outer pblock that includes both the slot and the anchors
    if enable_anchor_pblock:
      script += U250.constrainAnchorNetsAndSlot(slot_name, pblock_def)

    # next create the inner pblock that only includes the slot
    script.append(f'startgroup')
    script.append(f'create_pblock {slot_name}')
    script.append(f'resize_pblock [get_pblocks {slot_name}] -add {detailed_pblock_def}')
    if slr_crossing_neighbor:
      script.append(f'resize_pblock [get_pblocks {slot_name}] -add {slr_crossing_neighbor_pblock_def}')

    # previously we set the pblock as the entire clock regions. 
    # However, the intra-slot nets may use the anchor regions. 
    # This will interfere with the RW router, which preserves all intra-slot nets.
    # To get a clean anchor region, we set the routing pblock to strictly disjoint from the anchor regions
    # The prerequisite is that the placement pblock is even smaller than the routing pblock.
    # we need at least 1 row/col of empty space at the boundary to make the boundary nets routable.
    script.append(f'resize_pblock [get_pblocks {slot_name}] -remove {{ {U250.getNonSlotRegionsForRouting()} }}')

    script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')
    script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_ctrl_U0]')

    # add the laguna anchors within the slot region to the slot pblock
    # because we will not re-route laguna anchor nets
    # thus those must not spill into other slots
    dl_x, dl_y, ur_x, ur_y = getSlotIndicesFromSlotName(slot_name)
    script.append(f'catch {{ add_cells_to_pblock [get_pblocks {slot_name}] [get_cells -filter {{ LOC =~ *LAGUNA* }} ] }}')

    # script.append(f'set_property SNAPPING_MODE ON [get_pblocks {slot_name}]')
    script.append(f'endgroup')

    script.append(f'report_utilization -pblock [get_pblocks {slot_name}]')

    if enable_anchor_pblock:
      script.append(f'set_property PARENT anchor_pblock [get_pblocks {slot_name}]')

    return script


def routeWithGivenClock(hub, opt_dir, routing_dir):
  """
  Run the final routing of each slot with the given clock network
  """
  os.mkdir(routing_dir)

  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{routing_dir}/{slot_name}')

    script = []

    # enable higher hold fixing efforts
    script.append('set_param route.enableGlobalHoldIter 1')

    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')

    # should lock before adding placeholder FFs, otherwise vivado may crash
    script.append(f'lock_design -level placement')

    # report timing to check the quality of the final anchor placement
    script += getAnchorTimingReportScript(report_prefix='ILP_anchor_placement_iter1')

    script += addRoutingPblock(slot_name, enable_anchor_pblock=True)

    if args.do_not_fix_clock == False:
      # *** prevent gap in clock routing
      script.append(f'set_property ROUTE "" [get_nets ap_clk]')
      script.append(f'source -notrace {anchor_clock_routing_dir}/{slot_name}/set_anchor_clock_route.tcl')
      script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

      # add hold uncertainty
      # since we find a trick to keep a consistent tap for row buffers, we don't need this
      script.append(f'set_clock_uncertainty -hold 0.02 [get_clocks ap_clk]')

      # include all anchors to ensure the tap of row buffers are properly set
      script += addSomeAnchors(hub, base_dir, [slot_name])

    script.append(f'route_design')
    script.append(f'write_checkpoint routed.dcp')
    script.append(f'set fp [open "clock_route.txt" "w" ]') # to check the row buffer tap
    script.append(f'puts $fp [get_property ROUTE [get_nets ap_clk]]')
    script.append(f'close $fp')

    # whichever pblock is used for routing,
    # make sure the pblock is non-overlapping with anchor reigons before phys_opt_design
    # post-routing phys_opt_design may change placement as well
    # if inner cells are moved to anchor regions, the stitcher may fail due to its limitation
    script.append(f'resize_pblock [get_pblocks {slot_name}] -remove {{ {U250.getNonSlotRegionsForRouting()} }}')

    script.append(f'phys_opt_design')

    # remove the placeholder anchors
    script += removePlaceholderAnchors()

    # restore the hold uncertainty
    script.append(f'set_clock_uncertainty -hold 0 [get_clocks ap_clk]')

    # the RW stitcher cannot handle the pblocks well
    script.append(f'delete_pblocks *')

    # sometimes phys_opt_design make things worse, probably because of the fixed clock
    script.append(f'exec mkdir {routing_dir}/{slot_name}/phys_opt_routed')
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/phys_opt_routed/phys_opt_routed_with_ooc_clock.dcp')
    script.append(f'write_edif -force {routing_dir}/{slot_name}/phys_opt_routed/phys_opt_routed_with_ooc_clock.edf')

    script += getAnchorTimingReportScript(report_prefix='phys_opt_routed/slot_routing_iter0')

    # record the route of laguna nets
    script += extractLagunaAnchorRoutes(slot_name)

    # unroute non-laguna anchor D pin /Q pin nets
    script += unrouteNonLagunaAnchorDPinQPinNets()

    script.append(f'exec mkdir {routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted')
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted/non_laguna_anchor_nets_unrouted.dcp')
    script.append(f'write_edif -force {routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted/non_laguna_anchor_nets_unrouted.edf')

    open(f'{routing_dir}/{slot_name}/route_with_ooc_clock.tcl', "w").write('\n'.join(script))


def getParallelTasks(hub, routing_dir, user_name, server_list, main_server_name):
  # generate the gnu parallel tasks
  all_tasks = []

  parse_timing_report_1 = 'python3.6 -m autoparallel.BE.TimingReportParser ILP_anchor_placement_iter1'
  parse_timing_report_2 = 'python3.6 -m autoparallel.BE.TimingReportParser phys_opt_routed/slot_routing_iter0'

  for slot_name in hub['SlotIO'].keys():
    guard1 = f'until [[ -f {anchor_clock_routing_dir}/{slot_name}/set_anchor_clock_route.tcl.done.flag ]] ; do sleep 5; done'
    guard2 = f'until [[ -f {anchor_source_dir}/done.flag ]] ; do sleep 5; done'
    guard3 = f'until [[ -f {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp ]] ; do sleep 5; done'
    guard = f'{guard1} && {guard2} && {guard3}'

    vivado = f'VIV_VER={args.vivado_version} vivado -mode batch -source route_with_ooc_clock.tcl'
    dir = f'{routing_dir}/{slot_name}/'
    
    transfer = f'rsync -azh --delete -r {dir} {user_name}@{main_server_name}:{dir}'

    setup_rw = f'source {Constants.RWROUTE_SETUP_PATH}'
    target_dcp_path = f'{routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted/'
    target_dcp = f'{target_dcp_path}/non_laguna_anchor_nets_unrouted.dcp'
    output_path = f'{routing_dir}/{slot_name}/test_rw_route'

    if args.run_rwroute_test:
      test_rwroute = f'{setup_rw} && mkdir {output_path} && ' + Constants.RWROUTE.format(dcp=target_dcp, target_dir=output_path)
    else:
      test_rwroute = f'sleep 1'

    all_tasks.append(f'cd {dir} && {guard} && {vivado} && {parse_timing_report_1} && {parse_timing_report_2} && {test_rwroute} && {transfer} ')
    
  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]

    if args.do_not_fix_clock == False:
      folder_name = 'slot_routing'
    else:
      folder_name = 'slot_routing_do_not_fix_clock'

    open(f'{routing_dir}/parallel_{folder_name}_{server}.txt', 'w').write('\n'.join(local_tasks))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--hub_path", type=str, required=True)
  parser.add_argument("--base_dir", type=str, required=True)
  parser.add_argument("--vivado_version", type=str, required=True)
  parser.add_argument("--do_not_fix_clock", action='store_true')
  parser.add_argument("--run_rwroute_test", action='store_true')
  parser.add_argument("--server_list_in_str", type=str, required=True, help="e.g., \"u5 u15 u17 u18\"")
  parser.add_argument("--user_name", type=str, required=True)
  parser.add_argument("--main_server_name", type=str, required=True)
  args = parser.parse_args()

  hub_path = args.hub_path
  base_dir = args.base_dir
  user_name = args.user_name
  server_list = args.server_list_in_str.split()
  main_server_name = args.main_server_name

  opt_dir = f'{base_dir}/opt_placement_iter0'
  anchor_source_dir = f'{base_dir}/ILP_anchor_placement_iter0'

  if args.do_not_fix_clock == False:
    routing_dir = f'{base_dir}/slot_routing'
  else:
    routing_dir = f'{base_dir}/baseline_slot_routing_do_not_fix_clock'

  anchor_clock_routing_dir = f'{base_dir}/slot_anchor_clock_routing'

  print(f'WARNING: the server list is: {server_list}' )

  hub = json.loads(open(hub_path, 'r').read())
  routeWithGivenClock(hub, opt_dir, routing_dir)
  getParallelTasks(hub, routing_dir, user_name, server_list, main_server_name)
