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

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  backend_run_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  if os.path.isdir(backend_run_dir):
    raise f'target directory already exists: {backend_run_dir}'
  os.mkdir(backend_run_dir)

  hub = json.loads(open(fe_result_path, 'r').read())
  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']
  FloorplanVertex = hub['FloorplanVertex']

  assert os.path.isdir(orig_rtl_path)
  
  for slot_name in hub['SlotIO'].keys():
    logging.info(f'processing slot {slot_name}...')
    dir = f'{backend_run_dir}/{slot_name}'
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

  createGNUParallelScript(hub, backend_run_dir)

  
