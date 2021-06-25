#! /usr/bin/python3.6
import logging
import json
import os
import sys
import math
from autoparallel.BE.UniversalWrapperCreater import addAnchorToNonTopIOs
from autoparallel.BE.GenAnchorConstraints import *
from autoparallel.BE.CreateVivadoRun import *
from autoparallel.BE.AnchorPlacement import *
from autoparallel.BE.CreatePairwiseWrapper import *
from autoparallel.BE.CreateTopRun import createTopRun

def parallelAnchorPlacement(
    hub, 
    parallel_run_dir,
    pairwise_placement_dir,
    user_name,
    server_list):
  """
  for each pair of neighbor slots, group them and place & router the anchors in between
  """
  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  parallel_task = []

  pair_list = hub["AllSlotPairs"]
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    dir = f'{pairwise_placement_dir}/' + wrapper_name
    os.mkdir(dir)
    
    # generate wrapper rtl
    wrapper_path = f'{dir}/{wrapper_name}.v'
    CreateWrapperForSlotPair(hub, pair[0], pair[1], 1, dir, wrapper_name, in_slot_pipeline_style)

    # generate clock constraint
    createClockXDC(wrapper_name, dir)
    clock_xdc_path = f'{dir}/{wrapper_name}_clk.xdc' # TODO: redundancy

    # generate vivado script. Used post-placement DCP to place anchors
    dcp_path = lambda name : f'{parallel_run_dir}/{name}/{name}_placed_free_run/{name}_ctrl_placed_free_run.dcp'
    dcp_flag = lambda name : f'{parallel_run_dir}/{name}/{name}_placed_free_run/{name}.placement.done.flag'
    dcp_name2path = {name : dcp_path(name) for name in pair}
    all_dcp_flags = [dcp_flag(name) for name in pair]
    createVivadoScriptForSlotPair(hub, wrapper_name, wrapper_path, dcp_name2path, clock_xdc_path, dir)

    # add to task queue
    guard = 'until [[ ' + ' && '.join(f' -f {dcp_flag} ' for dcp_flag in all_dcp_flags) + ' ]] ; do sleep 10; done'
    command = 'VIV_VER=2020.1 vivado -mode batch -source place.tcl'
    # broadcast the results
    for server in server_list:
      command += f' && rsync -azh --delete -r {dir}/ {user_name}@{server}:{dir}'

    parallel_task.append(f'{guard} && cd {dir} && {command}')

  # create GNU parallel script
  num_job_server = math.ceil(len(parallel_task) / len(server_list) ) 
  for i, server in enumerate(server_list):
    local_tasks = parallel_task[i * num_job_server: (i+1) * num_job_server]
    open(f'{pairwise_placement_dir}/parallel-anchor-placement-{server}.txt', 'w').write('\n'.join(local_tasks))

def parallelSlotRun(hub, parallel_run_dir, user_name, server_list):
  """
  generate scripts to place & route each slot independently
  """
  def getAnchorWrapperOfSlot(hub, slot_name, output_path='.'):
    """
    Top-level ports will be directly connected
    All other IOs will be registered
    """
    slot_to_io = hub['SlotIO']
    slot_to_rtl = hub['SlotWrapperRTL']
    io_list = slot_to_io[slot_name]

    wrapper = addAnchorToNonTopIOs(hub, f'{slot_name}_ctrl', io_list)
    file = open(f'{output_path}/{slot_name}_anchored.v', 'w')
    file.write('\n'.join(wrapper))

    # add the rtl for the inner module (the slot wrapper)
    # discard the first line (time scale)
    assert 'timescale' in slot_to_rtl[slot_name][0]
    file.write('\n\n')
    file.write('\n'.join(slot_to_rtl[slot_name][1:]))

  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']

  assert os.path.isdir(orig_rtl_path)
  
  # note that pure routing slots are also implemented separately
  for slot_name in hub['SlotIO'].keys():

    logging.info(f'processing slot {slot_name}...')
    dir = f'{parallel_run_dir}/{slot_name}'
    os.mkdir(dir)
    
    # duplicate source RTL and add unique prefix
    target_rtl_path = f'{dir}/rtl'
    os.mkdir(target_rtl_path)
    getAnchorWrapperOfSlot(hub, slot_name, output_path=target_rtl_path)  

    # create pblock constraints for each anchored wrapper
    createPBlockScript(hub, slot_name, output_path=dir)

    createClockFromBUFGXDC(slot_name, output_path=dir)

    # create Vivado script for each slot
    getPlacementScript(fpga_part_name, 
                          orig_rtl_path, 
                          slot_name,
                          output_path=dir, 
                          placement_strategy='Default')

  createMultiServerExecution(hub, parallel_run_dir, user_name=user_name, server_list=server_list)

def loggingSetup():
  root = logging.getLogger()
  root.setLevel(logging.DEBUG)
  formatter = logging.Formatter("[%(levelname)s: %(funcName)25s() ] %(message)s")
  
  info_file_handler = logging.FileHandler(filename='ILP-placement.log', mode='w')
  info_file_handler.setLevel(logging.INFO)
  stdout_handler = logging.StreamHandler(sys.stdout)
  stdout_handler.setLevel(logging.INFO)

  handlers = [info_file_handler, stdout_handler]
  for handler in handlers:
    handler.setFormatter(formatter)
    root.addHandler(handler)

    
if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  hub = json.loads(open(fe_result_path, 'r').read())

  user_name = 'einsx7'
  server_list=['u5','u17','u18','u15']

  # the back end directory
  if os.path.isdir(backend_run_dir):
    raise f'target directory already exists: {backend_run_dir}'
  os.mkdir(backend_run_dir)

  # p&r each slot
  parallel_run_dir = f'{backend_run_dir}/parallel_run'
  os.mkdir(parallel_run_dir)
  parallelSlotRun(hub, parallel_run_dir, user_name=user_name, server_list=server_list)

  # pairwise anchor placement
  pairwise_placement_dir = f'{backend_run_dir}/parallel_stitch'
  os.mkdir(pairwise_placement_dir)
  parallelAnchorPlacement(hub, parallel_run_dir, pairwise_placement_dir,
                          user_name=user_name,server_list=server_list)

  # final stitch
  final_slot_run_dir = f'{backend_run_dir}/pruning_anchors'
  interconnect_placement_path = f'{pairwise_placement_dir}/place_interconnect.tcl'
  createTopRun(hub, backend_run_dir, final_slot_run_dir, interconnect_placement_path)