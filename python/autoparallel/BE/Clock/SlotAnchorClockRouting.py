import logging
import sys
import os
import json


def getSlotAnchorRoutingScript(slot_name, anchor_initialization_scripts):
  """
  for each slot, get all anchors around the slot
  route the clock net towards all anchors
  TODO: try not using FIXED_ROUTE, but using route_design -preserve
  if the clock stem is not modified, we should go this way
  """
  script = []

  script += [f'open_checkpoint {empty_checkpoint_path}']

  # add bufg and ap_clk
  script += ['create_cell -reference BUFGCE test_bufg']
  script += ['place_cell test_bufg BUFGCE_X0Y194']
  script += ['create_net ap_clk']
  script += ['connect_net -net ap_clk -objects {test_bufg/O}']
  script += ['create_clock -name ap_clk -period 2.50 [get_pins test_bufg/O]']

  # init all anchors around the slot, place them, connect to ap_clk
  script += [f'source -notrace {init_anchor}' for init_anchor in anchor_initialization_scripts]

  # add the clock stem
  script += [f'source {set_clock_stem_script}']

  script += [f'route_design']
  script += [f'set clock_route [get_property ROUTE [get_nets ap_clk]]']

  script += [f'set file [ open "{slot_name}_anchor_clock_route.txt" "w" ]']
  script += [f'puts $file $clock_route']
  script += [f'close $file']

  return script


def getAllSlotAnchorRoutingScripts():
  """
  setup the opt script for each slot
  """
  parallel = []
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{slot_anchor_clock_routing_dir}/{slot_name}')

    # create and place all anchors
    anchor_initialization_scripts = get_all_anchor_initialization_scripts(slot_name)

    anchor_clock_route_script = getSlotAnchorRoutingScript(slot_name, anchor_initialization_scripts)

    script_name = f'{slot_anchor_clock_routing_dir}/{slot_name}/{slot_name}_anchor_clock_routing.tcl'
    open(script_name, 'w').write('\n'.join(anchor_clock_route_script))
    
    parallel.append(f'cd {slot_anchor_clock_routing_dir}/{slot_name} && VIV_VER=2020.1 vivado -mode batch -source {script_name}')

  open(f'{slot_anchor_clock_routing_dir}/parallel-run-slot-clock-routing.txt', 'w').write('\n'.join(parallel))


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())
  pair_list = hub["AllSlotPairs"]
  pair_name_list = ['_AND_'.join(pair) for pair in pair_list]

  slot_anchor_clock_routing_dir = base_dir + '/slot_anchor_clock_routing'
  os.mkdir(slot_anchor_clock_routing_dir)

  current_path = os.path.dirname(os.path.realpath(__file__))
  empty_checkpoint_path = f'{current_path}/../../../../checkpoint/empty_U250.dcp'
  set_clock_stem_script = f'{current_path}/set_clock_stem_from_FF_chain_over_all_CR_design.tcl'

  user_name = 'einsx7'
  # server_list=['u5','u17','u18','u15']
  server_list=['u5']
  print(f'WARNING: the server list is: {server_list}' )

  # path of the checkpoint in the last iteration
  get_anchor_initialization_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'
  get_anchor_placement_flag = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/place_anchors.tcl.done.flag'

  # path of the anchor placement in the current iteration
  get_related_pairs = lambda slot_name : [pair_name for pair_name in pair_name_list if slot_name in pair_name]
  get_all_anchor_initialization_scripts = lambda slot_name : [get_anchor_initialization_script(pair_name) for pair_name in get_related_pairs(slot_name)]
  get_all_anchor_initialization_flags = lambda slot_name : [script + '.done.flag' for script in get_all_anchor_initialization_scripts(slot_name)]

  getAllSlotAnchorRoutingScripts()