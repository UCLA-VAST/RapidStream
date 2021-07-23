import sys
import json
import os
import math
from typing import List
from autoparallel.BE.Device import U250
from autoparallel.BE.GenAnchorConstraints import __getBufferRegionSize
from autoparallel.BE.Utilities import getAnchorTimingReportScript


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


def addAllAnchors(slot_name_list: List[str]):
  """
  when route a slot, instantiate and place all anchors, so that the tap of row buffers are closer to the real case.
  """
  pair_name_list = ['_AND_'.join(pair) for pair in hub["AllSlotPairs"]]
  get_create_anchor_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'

  script = ['set_property DONT_TOUCH 0 [get_nets ap_clk]']
  script += [f'catch {{ source -notrace {get_create_anchor_script(pair_name)} }}' \
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
  script.append('set non_laguna_anchor_nets [ get_nets -of_objects $non_laguna_anchors -filter {NAME != "ap_clk" && NAME != "<const0>" && NAME != "<const1>"} ]')
  script.append('route_design -unroute -nets $non_laguna_anchor_nets')

  return script


def routeWithGivenClock(hub, opt_dir, routing_dir):
  """
  Run the final routing of each slot with the given clock network
  """
  os.mkdir(routing_dir)

  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{routing_dir}/{slot_name}')

    script = []
    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')

    # report timing to check the quality of the final anchor placement
    script += getAnchorTimingReportScript(report_prefix='ILP_anchor_placement_iter1')

    # relax placement pblocks
    # do this before updating the clock to prevent vivado crash
    script.append(f'delete_pblock [get_pblocks *]')
    script.append(f'create_pblock {slot_name}')
    pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
    script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_ctrl_U0]')
    script.append(f'resize_pblock [get_pblocks {slot_name}] -add {pblock_def}')

    # previously we set the pblock as the entire clock regions. 
    # However, the intra-slot nets may use the anchor regions. 
    # This will interfere with the RW router, which preserves all intra-slot nets.
    # To get a clean anchor region, we set the routing pblock to strictly disjoint from the anchor regions
    # The prerequisite is that the placement pblock is even smaller than the routing pblock.
    # we need at least 1 row/col of empty space at the boundary to make the boundary nets routable.
    buffer_col_num, buffer_row_num = __getBufferRegionSize(hub, slot_name)
    slice_buffer_at_boundary = U250.getAllBoundaryBufferRegions(buffer_col_num, buffer_row_num)
    script.append(f'resize_pblock [get_pblocks {slot_name}] -remove {{ {slice_buffer_at_boundary} }}')
    script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')

    # *** prevent gap in clock routing
    script.append(f'set_property ROUTE "" [get_nets ap_clk]')
    script.append(f'source -notrace {anchor_clock_routing_dir}/{slot_name}/set_anchor_clock_route.tcl')
    script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

    # add hold uncertainty
    # since we find a trick to keep a consistent tap for row buffers, we don't need this
    script.append(f'set_clock_uncertainty -hold 0.05 [get_clocks ap_clk]')

    # include all anchors to ensure the tap of row buffers are properly set
    script += addAllAnchors([slot_name])

    script.append(f'route_design')
    script.append(f'puts [get_property ROUTE [get_nets ap_clk]]') # to check the row buffer tap

    # remove the placeholder anchors
    script += removePlaceholderAnchors()

    # restore the hold uncertainty
    script.append(f'set_clock_uncertainty -hold 0 [get_clocks ap_clk]')

    # sometimes phys_opt_design make things worse, probably because of the fixed clock
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/routed_with_ooc_clock.dcp')
    script.append(f'phys_opt_design')
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/phys_opt_routed_with_ooc_clock.dcp')

    script += getAnchorTimingReportScript(report_prefix='slot_routing_iter0')

    # record the route of laguna nets
    script += extractLagunaAnchorRoutes(slot_name)

    # unroute non-laguna anchor D pin /Q pin nets
    script += unrouteNonLagunaAnchorDPinQPinNets()

    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted.dcp')
    script.append(f'write_edif -force {routing_dir}/{slot_name}/non_laguna_anchor_nets_unrouted.edf')

    open(f'{routing_dir}/{slot_name}/route_with_ooc_clock.tcl', "w").write('\n'.join(script))


def getParallelTasks(hub, routing_dir, user_name, server_list, main_server_name):
  # generate the gnu parallel tasks
  all_tasks = []

  parse_timing_report_1 = 'python3.6 -m autoparallel.BE.TimingReportParser ILP_anchor_placement_iter1'
  parse_timing_report_2 = 'python3.6 -m autoparallel.BE.TimingReportParser slot_routing_iter0'

  for slot_name in hub['SlotIO'].keys():
    vivado = 'VIV_VER=2020.2 vivado -mode batch -source route_with_ooc_clock.tcl'
    dir = f'{routing_dir}/{slot_name}/'
    
    transfer = f'rsync -azh --delete -r {dir} {user_name}@{main_server_name}:{dir}'
    all_tasks.append(f'cd {dir} && {vivado} && {transfer} && {parse_timing_report_1} && {parse_timing_report_2}')
    
  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]
    open(f'{routing_dir}/parallel-route-with-ooc-clock-{server}.txt', 'w').write('\n'.join(local_tasks))


if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  opt_dir = f'{base_dir}/opt_placement_iter0'
  routing_dir = f'{base_dir}/slot_routing'
  anchor_clock_routing_dir = f'{base_dir}/slot_anchor_clock_routing'

  user_name = 'einsx7'
  # server_list=['u5','u17','u18','u15']
  server_list=['u5']
  main_server_name = 'u5'
  print(f'WARNING: the server list is: {server_list}' )

  hub = json.loads(open(hub_path, 'r').read())
  routeWithGivenClock(hub, opt_dir, routing_dir)
  getParallelTasks(hub, routing_dir, user_name, server_list, main_server_name)
