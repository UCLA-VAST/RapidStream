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

def parallelAnchorPlacement(
    hub, 
    run_dir,
    stitch_dir):
  """
  for each pair of neighbor slots, group them and place & router the anchors in between
  TODO: extract the anchor placement 
  """
  pair_list = hub["ComputeSlotPairs"]
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    dir = f'{stitch_dir}/' + wrapper_name
    os.mkdir(dir)
    
    # generate wrapper rtl
    pair_wrapper = CreateWrapperForSlotPair(hub, pair[0], pair[1])
    wrapper_path = f'{dir}/{wrapper_name}.v'
    open(wrapper_path, 'w').write('\n'.join(pair_wrapper))

    # generate clock constraint
    createClockXDC(wrapper_name, dir)
    clock_xdc_path = f'{dir}/{wrapper_name}_clk.xdc' # TODO: redundancy

    # generate vivado script
    dcp_path = lambda name : f'{run_dir}/{name}/{name}_routed_free_run/{name}_routed_free_run.dcp'
    dcp_name2path = {name : dcp_path(name) for name in pair}
    createVivadoScriptForSlotPair(hub, wrapper_name, wrapper_path, dcp_name2path, clock_xdc_path, dir)

def parallelSlotRun(hub, run_dir):
  """
  generate scripts to place & route each slot independently
  """
  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']
  FloorplanVertex = hub['FloorplanVertex']

  assert os.path.isdir(orig_rtl_path)
  
  # TODO: take care of pure routing slots
  for slot_name in hub['SlotIO'].keys():
    logging.info(f'processing slot {slot_name}...')
    dir = f'{run_dir}/{slot_name}'
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
    
    createAnchorPlacementExtractScript(hub, slot_name, dir)

    # TODO: monitor when the placement of the free run is finished
    # createAnchorPlacementScript(hub, slot_name, backend_run_dir)

  createGNUParallelScript(hub, run_dir)

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  if os.path.isdir(backend_run_dir):
    raise f'target directory already exists: {backend_run_dir}'
  os.mkdir(backend_run_dir)

  run_dir = f'{backend_run_dir}/parallel_run'
  stitch_dir = f'{backend_run_dir}/parallel_stitch'
  os.mkdir(run_dir)
  os.mkdir(stitch_dir)

  hub = json.loads(open(fe_result_path, 'r').read())

  parallelSlotRun(hub, run_dir)
  parallelAnchorPlacement(hub, run_dir, stitch_dir)