import logging
import json
import sys
import os
import math
from autoparallel.BE.Utilities import getAnchorTimingReportScript


def getSlotPlacementOptScript(hub, slot_name, dcp_path, anchor_placement_scripts):
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
  # script.append(f'source place_anchors_of_slot.tcl')
  for anchor_placement in anchor_placement_scripts:
    script.append(f'source {anchor_placement}')

  # get rid of the place holder LUTs
  # currently keep the LUTs to alleviate hold violations
  if hub['InSlotPipelineStyle'] == 'LUT':
    script += removeLUTPlaceholders()

  # to help analysis of the anchor placement quality
  script.append(f'write_checkpoint -force {slot_name}_before_placed_opt.dcp')

  # report timing to check the quality of anchor placement
  script += getAnchorTimingReportScript(report_prefix='ILP_anchor_placement_iter0')

  # optimize the slot based on the given anchor placement
  # do placement only so that we could track the change from the log
  script.append(f'phys_opt_design -verbose')
  script.append(f'write_checkpoint -force {slot_name}_post_placed_opt.dcp')

  # report timing to check the timing improvement of slot phys_opt_design
  script += getAnchorTimingReportScript(report_prefix='phys_opt_design_iter0')

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

def generateParallelScript(hub, user_name, server_list):
  """
  summarize all tasks for gnu parallel
  fire as soon as the neighbor anchors are ready
  """
  all_tasks = []
  slot_names = hub['SlotIO'].keys()
  parse_timing_report_1 = 'python3.6 -m autoparallel.BE.TimingReportParser ILP_anchor_placement_iter0'
  parse_timing_report_2 = 'python3.6 -m autoparallel.BE.TimingReportParser phys_opt_design_iter0'

  for slot_name in slot_names:
    # wait until local anchors are ready
    # check flags to prevent race conditions
    flags = get_all_anchor_placement_flags(slot_name)
    get_guard = lambda flag : f'until [[ -f {flag} ]] ; do sleep 5; done'
    guards =  ' && '.join([get_guard(flag) for flag in flags])

    vivado = f'VIV_VER={VIV_VER} vivado -mode batch -source {slot_name}_phys_opt_placement.tcl'
    
    # broadcast the results
    for server in server_list:
      vivado += f' && rsync -azh --delete -r {opt_dir}/{slot_name}/ {user_name}@{server}:{opt_dir}/{slot_name}/'

    command = f' {guards} && cd {opt_dir}/{slot_name} && {vivado} && {parse_timing_report_1} && {parse_timing_report_2}'
    all_tasks.append(command)

  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]
    open(f'{opt_dir}/parallel-opt-placement-{server}.txt', 'w').write('\n'.join(local_tasks))

def generateOptScript(hub):
  """
  setup the opt script for each slot
  """
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{opt_dir}/{slot_name}')
    dcp_path = get_dcp_path(slot_name)

    # get the placement of the anchors
    anchor_placement_scripts = get_all_anchor_placement_scripts(slot_name)

    opt_script = getSlotPlacementOptScript(hub, slot_name, dcp_path, anchor_placement_scripts)
    open(f'{opt_dir}/{slot_name}/{slot_name}_phys_opt_placement.tcl', 'w').write('\n'.join(opt_script))
  
if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 4, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  VIV_VER=sys.argv[3]

  hub = json.loads(open(hub_path, 'r').read())
  pair_list = hub["AllSlotPairs"]
  pair_name_list = ['_AND_'.join(pair) for pair in pair_list]

  opt_dir = base_dir + '/opt_placement_iter0'
  os.mkdir(opt_dir)  

  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']
  print(f'WARNING: the server list is: {server_list}' )

  # path of the checkpoint in the last iteration
  get_dcp_path = lambda slot_name: f'{base_dir}/init_slot_placement/{slot_name}/{slot_name}_placed.dcp'
  get_anchor_placement_script = lambda pair_name : f'{base_dir}/ILP_anchor_placement_iter0/{pair_name}/place_anchors.tcl'
  get_anchor_placement_flag = lambda pair_name : get_anchor_placement_script(pair_name) + '.done.flag'

  # path of the anchor placement in the current iteration
  get_related_pairs = lambda slot_name : [pair_name for pair_name in pair_name_list if slot_name in pair_name]
  get_all_anchor_placement_scripts = lambda slot_name : [get_anchor_placement_script(pair_name) for pair_name in get_related_pairs(slot_name)]
  get_all_anchor_placement_flags = lambda slot_name : [script + '.done.flag' for script in get_all_anchor_placement_scripts(slot_name)]

  generateOptScript(hub)
  generateParallelScript(hub, user_name, server_list)