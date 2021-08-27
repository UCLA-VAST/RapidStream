import argparse
import logging
import math
import os
import json
from typing import List

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
  if args.is_invert_clock == 1:
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
    anchor_initialization_scripts = getAnchorInitScripts(slot_name)

    anchor_clock_route_script = getSlotAnchorRoutingScript(anchor_initialization_scripts)

    script_name = f'{slot_anchor_clock_routing_dir}/{slot_name}/{slot_name}_anchor_clock_routing.tcl'
    open(script_name, 'w').write('\n'.join(anchor_clock_route_script))


def getAnchorInitScripts(slot_name) -> List[str]:
  """
  get the dependency files for the job
  """
  related_pairs = [pair_name for pair_name in pair_name_list if slot_name in pair_name]

  get_anchor_initialization_script_path = lambda pair_name : f'{anchor_source_dir}/{pair_name}/create_and_place_anchors_for_clock_routing.tcl'
  
  anchor_init_script_list = [get_anchor_initialization_script_path(pair_name) for pair_name in related_pairs]

  return anchor_init_script_list


def getGuards(slot_name) -> List[str]:
  anchor_init_script_list = getAnchorInitScripts(slot_name)
  guard_list = [script + '.done.flag' for script in anchor_init_script_list]
  return guard_list


def getParallelScript():
  """
  setup the clock routing script for each slot
  """
  all_tasks = []
  for slot_name in hub['SlotIO'].keys():

    cd = f'cd {slot_anchor_clock_routing_dir}/{slot_name}'

    flags = getGuards(slot_name)
    get_guard = lambda flag : f'until [[ -f {flag} ]] ; do sleep 5; done'
    guards =  ' && '.join([get_guard(flag) for flag in flags])

    script_name = f'{slot_anchor_clock_routing_dir}/{slot_name}/{slot_name}_anchor_clock_routing.tcl'
    vivado = f'VIV_VER={args.vivado_version} vivado -mode batch -source {script_name}'
    
    touch_flag = f'touch {slot_anchor_clock_routing_dir}/{slot_name}/set_anchor_clock_route.tcl.done.flag'

    transfer = []
    for server in server_list:
      transfer.append(f'rsync -azh --delete -r {slot_anchor_clock_routing_dir}/{slot_name}/ {user_name}@{server}:{slot_anchor_clock_routing_dir}/{slot_name}/')
    transfer_str = ' && '.join(transfer)

    all_tasks.append(f'{cd} && {guards} && {vivado} && {touch_flag} && {transfer_str}')

  open(f'{slot_anchor_clock_routing_dir}/parallel_{folder_name}_all.txt', 'w').write('\n'.join(all_tasks))

  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]
    open(f'{slot_anchor_clock_routing_dir}/parallel_{folder_name}_{server}.txt', 'w').write('\n'.join(local_tasks))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--hub_path", type=str, required=True)
  parser.add_argument("--base_dir", type=str, required=True)
  parser.add_argument("--vivado_version", type=str, required=True)
  parser.add_argument("--is_invert_clock", type=int, required=True)
  parser.add_argument("--server_list_in_str", type=str, required=True, help="e.g., \"u5 u15 u17 u18\"")
  parser.add_argument("--user_name", type=str, required=True)
  args = parser.parse_args()

  hub_path = args.hub_path
  base_dir = args.base_dir
  user_name = args.user_name
  server_list = args.server_list_in_str.split()

  hub = json.loads(open(hub_path, 'r').read())
  pair_list = hub["AllSlotPairs"]
  pair_name_list = ['_AND_'.join(pair) for pair in pair_list]

  folder_name = 'slot_anchor_clock_routing'
  slot_anchor_clock_routing_dir = base_dir + '/' + folder_name
  os.mkdir(slot_anchor_clock_routing_dir)

  current_path = os.path.dirname(os.path.realpath(__file__))
  empty_checkpoint_path = f'{current_path}/../../../../checkpoint/empty_U250.dcp'
  set_clock_stem_script = f'{current_path}/set_clock_stem_from_FF_chain_over_all_CR_design.tcl'

  print(f'WARNING: the server list is: {server_list}' )

  anchor_source_dir = f'{base_dir}/ILP_anchor_placement_iter0'

  getAllSlotAnchorRoutingScripts()
  getParallelScript()