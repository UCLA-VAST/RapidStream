import logging
import sys
import os
import json

from autoparallel.BE.Utilities import loggingSetup

loggingSetup()


def getSlotAnchorRoutingScript(anchor_initialization_scripts):
  """
  for each slot, get all anchors around the slot
  route the clock net towards all anchors
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

  # invert the clock
  if IS_INVERT_CLOCK:
    script.append(f'set_property IS_INVERTED 1 [ get_pins -filter {{ NAME =~ "*C" }} -of_object [get_cells *q0_reg*] ]')

  script += [f'route_design']
  script += [f'set clock_route [get_property ROUTE [get_nets ap_clk]]']

  script += [f'set file [ open "set_anchor_clock_route.tcl" "w" ]']
  script += [ 'puts $file "set_property FIXED_ROUTE ${clock_route} \[ get_nets ap_clk \]" ']
  script += [f'close $file']

  return script


def getAllSlotAnchorRoutingScripts():
  """
  setup the clock routing script for each slot
  """
  parallel = []
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{slot_anchor_clock_routing_dir}/{slot_name}')

    # create and place all anchors
    anchor_initialization_scripts = get_all_anchor_initialization_scripts(slot_name)

    anchor_clock_route_script = getSlotAnchorRoutingScript(anchor_initialization_scripts)

    script_name = f'{slot_anchor_clock_routing_dir}/{slot_name}/{slot_name}_anchor_clock_routing.tcl'
    open(script_name, 'w').write('\n'.join(anchor_clock_route_script))


def getParallelScript():
  """
  setup the clock routing script for each slot
  """
  parallel = []
  for slot_name in hub['SlotIO'].keys():

    cd = f'cd {slot_anchor_clock_routing_dir}/{slot_name}'

    script_name = f'{slot_anchor_clock_routing_dir}/{slot_name}/{slot_name}_anchor_clock_routing.tcl'
    vivado = f'VIV_VER={VIV_VER} vivado -mode batch -source {script_name}'
    
    transfer = []
    for server in server_list:
      transfer.append(f'rsync -azh --delete -r {slot_anchor_clock_routing_dir}/{slot_name}/ {user_name}@{server}:{slot_anchor_clock_routing_dir}/{slot_name}/')
    transfer_str = ' && '.join(transfer)

    parallel.append(f'{cd} && {vivado} && {transfer_str}')

  open(f'{slot_anchor_clock_routing_dir}/parallel-run-slot-clock-routing.txt', 'w').write('\n'.join(parallel))


if __name__ == '__main__':
  assert len(sys.argv) == 5, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  VIV_VER=sys.argv[3]
  IS_INVERT_CLOCK = sys.argv[4]

  hub = json.loads(open(hub_path, 'r').read())
  pair_list = hub["AllSlotPairs"]
  pair_name_list = ['_AND_'.join(pair) for pair in pair_list]

  slot_anchor_clock_routing_dir = base_dir + '/slot_anchor_clock_routing'
  os.mkdir(slot_anchor_clock_routing_dir)

  current_path = os.path.dirname(os.path.realpath(__file__))
  empty_checkpoint_path = f'{current_path}/../../../../checkpoint/empty_U250.dcp'
  set_clock_stem_script = f'{current_path}/set_clock_stem_from_FF_chain_over_all_CR_design.tcl'

  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']
  print(f'WARNING: the server list is: {server_list}' )

  # path of the checkpoint in the last iteration
  get_anchor_initialization_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'
  get_anchor_placement_flag = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/place_anchors.tcl.done.flag'

  # path of the anchor placement in the current iteration
  get_related_pairs = lambda slot_name : [pair_name for pair_name in pair_name_list if slot_name in pair_name]
  get_all_anchor_initialization_scripts = lambda slot_name : [get_anchor_initialization_script(pair_name) for pair_name in get_related_pairs(slot_name)]
  get_all_anchor_initialization_flags = lambda slot_name : [script + '.done.flag' for script in get_all_anchor_initialization_scripts(slot_name)]

  getAllSlotAnchorRoutingScripts()
  getParallelScript()