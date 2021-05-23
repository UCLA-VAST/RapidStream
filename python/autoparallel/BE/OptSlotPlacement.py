import logging
import json
import sys
import os
import math

def getSlotPlacementOptScript(hub, slot_name, dcp_path):
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
  script.append(f'source place_anchors_of_slot.tcl')

  # get rid of the place holder LUTs
  if hub['InSlotPipelineStyle'] == 'LUT':
    script += removeLUTPlaceholders()

  # optimize the slot based on the given anchor placement
  # do placement only so that we could track the change from the log
  script.append(f'phys_opt_design -verbose')
  script.append(f'write_checkpoint -force {slot_name}_post_placed_opt.dcp')
  script.append(f'write_checkpoint -cell {slot_name}_U0 -force {slot_name}_ctrl_post_placed_opt.dcp')

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

def generateParallelScript(hub, opt_dir, user_name, server_list):
  """
  summarize all tasks for gnu parallel
  fire as soon as the neighbor anchors are ready
  """
  all_tasks = []
  slot_names = hub['SlotIO'].keys()
  for slot_name in slot_names:
    # wait until local anchors are ready
    # check flags to prevent race conditions
    guard = f'until [[ -f {opt_dir}/{slot_name}/place_anchors_of_slot.done.flag ]] ; do sleep 10; done'
    vivado = f'VIV_VER=2020.1 vivado -mode batch -source {slot_name}_phys_opt_placement.tcl'
    
    # broadcast the results
    for server in server_list:
      vivado += f' && rsync -azh --delete -r {opt_dir}/{slot_name}/ {user_name}@{server}:{opt_dir}/{slot_name}/'

    command = f' {guard} && cd {opt_dir}/{slot_name} && {vivado}'
    all_tasks.append(command)

  num_job_server = math.ceil(len(all_tasks) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = all_tasks[i * num_job_server: (i+1) * num_job_server]
    open(f'{opt_dir}/parallel-opt-placement-{server}.txt', 'w').write('\n'.join(local_tasks))

def generateOptScript(hub, parallel_run_dir):
  """
  setup the opt script for each slot
  """
  for slot_name in hub['SlotIO'].keys():
    slot_dir = f'{parallel_run_dir}/{slot_name}'
    slot_placement_dir = f'{slot_dir}/{slot_name}_placed_free_run'
    dcp_path = f'{slot_placement_dir}/{slot_name}_placed_free_run.dcp'

    opt_script = getSlotPlacementOptScript(hub, slot_name, dcp_path)
    open(f'{opt_dir}/{slot_name}/{slot_name}_phys_opt_placement.tcl', 'w').write('\n'.join(opt_script))
  
if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  
  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']
  print(f'WARNING: the server list is: {server_list}' )

  parallel_run_dir = base_dir + '/parallel_run'

  hub = json.loads(open(hub_path, 'r').read())

  opt_dir = base_dir + '/opt_test'
  os.mkdir(opt_dir)
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{opt_dir}/{slot_name}')

  generateOptScript(hub, parallel_run_dir)
  generateParallelScript(hub, opt_dir, user_name, server_list)