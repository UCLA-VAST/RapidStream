#! /usr/bin/python3.6
import logging
import json
import os
import sys
from autoparallel.BE.CreateAnchorWrapper import *
from autoparallel.BE.GenAnchorConstraints import *
from autoparallel.BE.CreateVivadoRun import *
from autoparallel.BE.AnchorPlacement import *
from autoparallel.BE.DuplicateRTL import *
from autoparallel.BE.CreatePairwiseWrapper import *
from autoparallel.BE.CreateTopRun import createTopRunScript, setupTopRunRTL

def parallelAnchorPlacement(
    hub, 
    parallel_run_dir,
    stitch_dir):
  """
  for each pair of neighbor slots, group them and place & router the anchors in between
  """

  parallel_task = []

  pair_list = hub["ComputeSlotPairs"]
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    dir = f'{stitch_dir}/' + wrapper_name
    os.mkdir(dir)
    
    # generate wrapper rtl
    wrapper_path = f'{dir}/{wrapper_name}.v'
    pair_wrapper = CreateWrapperForSlotPair(hub, pair[0], pair[1], 1, dir, wrapper_name)

    # generate clock constraint
    createClockXDC(wrapper_name, dir)
    clock_xdc_path = f'{dir}/{wrapper_name}_clk.xdc' # TODO: redundancy

    # generate vivado script. Used post-placement DCP to place anchors
    dcp_path = lambda name : f'{parallel_run_dir}/{name}/{name}_placed_free_run/{name}_ctrl_placed_free_run.dcp'
    dcp_name2path = {name : dcp_path(name) for name in pair}
    createVivadoScriptForSlotPair(hub, wrapper_name, wrapper_path, dcp_name2path, clock_xdc_path, dir)

    # add to task queue
    parallel_task.append(f'cd {dir} && VIV_VER=2020.1 vivado -mode batch -source place.tcl')

  # create GNU parallel script
  open(f'{stitch_dir}/run_parallel.txt', 'w').write('\n'.join(parallel_task))

def parallelSlotRun(hub, parallel_run_dir):
  """
  generate scripts to place & route each slot independently
  """
  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']
  FloorplanVertex = hub['FloorplanVertex']

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
    # duplicateSourceRTL(orig_rtl_path, target_rtl_path, slot_name, FloorplanVertex)

    # create pblock constraints for each anchored wrapper
    createPBlockScript(hub, slot_name, output_path=dir)

    createClockXDC(slot_name, output_path=dir)

    # create Vivado script for each slot
    anchored_wrapper_path = f'{dir}/{slot_name}_anchored.v'
    createVivadoRunScript(fpga_part_name, 
                          orig_rtl_path, 
                          slot_name,
                          output_path=dir, 
                          placement_strategy='AltSpreadLogic_high')
    
    # extract anchor placement. Note that anchor registers are appended the suffix "_anchor"
    io_list = hub['SlotIO'][slot_name]
    anchor_list = [ io[:-1] + [f'{io[-1]}_anchor'] for io in io_list]
    createAnchorPlacementExtractScript(slot_name, anchor_list, dir)

    # TODO: monitor when the placement of the free run is finished
    # createAnchorPlacementScript(hub, slot_name, backend_run_dir)

  createGNUParallelScript(hub, parallel_run_dir)

def topRun(hub, top_run_dir, parallel_run_dir):
  """
  Assemble the post-place DCPs and post-route DCPs
  """
  setupTopRunRTL(hub, top_run_dir)

  # clock xdc
  createClockXDC('final_top', top_run_dir)

  # two set of top run
  # overlap the placement of interconnects with the routing of compute slots
  for target in ['placed', 'routed']:
    top_run_script = createTopRunScript(hub, f'{top_run_dir}/rtl', f'{top_run_dir}/final_top_clk.xdc', parallel_run_dir, target)
    open(f'{top_run_dir}/final_top_{target}.tcl', 'w').write('\n'.join(top_run_script))

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  if os.path.isdir(backend_run_dir):
    raise f'target directory already exists: {backend_run_dir}'
  os.mkdir(backend_run_dir)

  parallel_run_dir = f'{backend_run_dir}/parallel_run'
  stitch_dir = f'{backend_run_dir}/parallel_stitch'
  top_run_dir = f'{backend_run_dir}/top_run'
  os.mkdir(parallel_run_dir)
  os.mkdir(stitch_dir)
  os.mkdir(top_run_dir)

  hub = json.loads(open(fe_result_path, 'r').read())

  parallelSlotRun(hub, parallel_run_dir)
  parallelAnchorPlacement(hub, parallel_run_dir, stitch_dir)
  topRun(hub, top_run_dir, parallel_run_dir)