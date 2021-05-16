#! /usr/bin/python3.6
import logging
import json
import os
import sys
from autoparallel.BE.CreateAnchorWrapper import *
from autoparallel.BE.GenAnchorConstraints import *
from autoparallel.BE.CreateVivadoRun import *
from autoparallel.BE.AnchorPlacement import *
from autoparallel.BE.CreatePairwiseWrapper import *
from autoparallel.BE.CreateTopRun import createTopRun

def parallelAnchorPlacement(
    hub, 
    parallel_run_dir,
    pairwise_placement_dir):
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
    guard = 'until ' + ' & '.join(f'[ -f {dcp_flag} ]' for dcp_flag in all_dcp_flags) + '; do sleep 10; done'
    command = 'VIV_VER=2020.1 vivado -mode batch -source place.tcl'
    parallel_task.append(f'{guard} && cd {dir} && {command}')

  # create GNU parallel script
  open(f'{pairwise_placement_dir}/run_parallel.txt', 'w').write('\n'.join(parallel_task))

def parallelSlotRun(hub, parallel_run_dir):
  """
  generate scripts to place & route each slot independently
  """
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
    createAnchorWrapper(hub, slot_name, output_path=target_rtl_path)  

    # create pblock constraints for each anchored wrapper
    createPBlockScript(hub, slot_name, output_path=dir)

    createClockFromBUFGXDC(slot_name, output_path=dir)

    # create Vivado script for each slot
    createVivadoRunScript(fpga_part_name, 
                          orig_rtl_path, 
                          slot_name,
                          output_path=dir, 
                          placement_strategy='Default')
    
    # extract anchor placement. Note that anchor registers are appended the suffix "_anchor"
    io_list = hub['SlotIO'][slot_name]
    anchor_list = [ io[:-1] + [f'{io[-1]}_anchor'] for io in io_list]
    createAnchorPlacementExtractScript(slot_name, anchor_list, dir)

  createGNUParallelScript(hub, parallel_run_dir)

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  hub = json.loads(open(fe_result_path, 'r').read())

  # the back end directory
  if os.path.isdir(backend_run_dir):
    raise f'target directory already exists: {backend_run_dir}'
  os.mkdir(backend_run_dir)

  # p&r each slot
  parallel_run_dir = f'{backend_run_dir}/parallel_run'
  os.mkdir(parallel_run_dir)
  parallelSlotRun(hub, parallel_run_dir)

  # pairwise anchor placement
  pairwise_placement_dir = f'{backend_run_dir}/parallel_stitch'
  os.mkdir(pairwise_placement_dir)
  parallelAnchorPlacement(hub, parallel_run_dir, pairwise_placement_dir)

  # final stitch
  final_slot_run_dir = f'{backend_run_dir}/opt_iter1_ctrl_only'
  interconnect_placement_path = f'{pairwise_placement_dir}/place_interconnect.tcl'
  createTopRun(hub, backend_run_dir, final_slot_run_dir, interconnect_placement_path)