import logging
import json
import sys
import math
import os

from autoparallel.BE.Utilities import getAnchorTimingReportScript
from autoparallel.BE.GenAnchorConstraints import getSlotInitPlacementPblock
from autoparallel.BE.Utilities import loggingSetup

loggingSetup()


def getPlacementScript(slot_name):
  script = []
  script.append(f'set_param general.maxThreads 8')

  dcp_path = get_synth_dcp(slot_name)
  script.append(f'open_checkpoint {dcp_path}')
  
  # add floorplanning constraints
  script += getSlotInitPlacementPblock(hub, slot_name)
  
  script.append(f'opt_design')

  # placement
  script.append(f'place_design')
  script.append(f'phys_opt_design')

  # write out the ctrl wrapper only for anchor placement
  script.append(f'write_checkpoint -cell {slot_name}_ctrl_U0 {init_place_dir}/{slot_name}/{slot_name}_placed_no_anchor.dcp')
  script.append(f'write_checkpoint {init_place_dir}/{slot_name}/{slot_name}_placed.dcp')

  # get the timing report of anchors. At this point the timing report is meaningless
  # however, we use the report to extract the number of LUTs on the timing paths
  script += getAnchorTimingReportScript(report_prefix='init_placement')

  script.append(f'exec touch {init_place_dir}/{slot_name}/{slot_name}_placed.dcp.done.flag') # signal that the DCP generation is finished

  return script


def setupSlotInitPlacement():
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{init_place_dir}/{slot_name}')
    script = getPlacementScript(slot_name)
    open(f'{init_place_dir}/{slot_name}/place_slot.tcl', 'w').write('\n'.join(script))


def generateParallelScript(hub, user_name, server_list):
  """
  spread the tasks to multiple servers
  broadcast the results to all servers
  """
  place = []
  
  vivado = f'VIV_VER={VIV_VER} vivado -mode batch -source place_slot.tcl'
  parse_timing_report = 'python3.6 -m autoparallel.BE.TimingReportParser init_placement'

  for slot_name in hub['SlotIO'].keys():
    cd = f'cd {init_place_dir}/{slot_name}/'

    guard = get_guard(slot_name)
    
    # broadcast the results to all servers
    transfer = []
    for server in server_list:
      transfer.append(f'rsync -azh --delete -r {init_place_dir}/{slot_name}/ {user_name}@{server}:{init_place_dir}/{slot_name}/')
    transfer_str = "&&".join(transfer)

    command = f'{guard} && {cd} && {vivado} && {parse_timing_report} && {transfer_str}'

    place.append(command)

  num_job_server = math.ceil(len(place) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = place[i * num_job_server: (i+1) * num_job_server]
    open(f'{init_place_dir}/parallel_init_slot_placement_{server}.txt', 'w').write('\n'.join(local_tasks))


if __name__ == '__main__':
  assert len(sys.argv) == 5, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  VIV_VER=sys.argv[3]
  UNIQUE_SYNTH_DCP_DIR=sys.argv[4]

  # depends on whether we use the uniquified synth checkpoints
  if UNIQUE_SYNTH_DCP_DIR:
    get_synth_dcp = lambda slot_name : f'{UNIQUE_SYNTH_DCP_DIR}/{slot_name}/{slot_name}_synth_unique_2021.1.dcp'
    get_guard = lambda slot_name : 'sleep 1' # use a harmless placeholder command
  else:
    get_synth_dcp = lambda slot_name : f'{synth_dir}/{slot_name}/{slot_name}_synth.dcp'
    get_guard = lambda slot_name : f'until [[ -f {synth_dir}/{slot_name}/{slot_name}_synth.dcp.done.flag ]] ; do sleep 10; done'

  hub = json.loads(open(hub_path, 'r').read())

  synth_dir = f'{base_dir}/slot_synth'
  init_place_dir = f'{base_dir}/init_slot_placement'
  os.mkdir(init_place_dir)

  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']

  setupSlotInitPlacement()

  generateParallelScript(hub, user_name, server_list)