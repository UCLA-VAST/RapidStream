#! /usr/bin/python3.6
import logging
import json
import os
import sys
from autoparallel.BE.CreateAnchorWrapper import *
from autoparallel.BE.GenAnchorConstraints import *

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  target_dir = sys.argv[2]
  fe_result_path = sys.argv[1]

  if os.path.isdir(target_dir):
    raise f'target directory already exists: {target_dir}'
  os.mkdir(target_dir)

  hub = json.loads(open(fe_result_path, 'r').read())
  fpga_part_name = hub['FPGA_PART_NAME']
  orig_rtl_path = hub['ORIG_RTL_PATH']

  assert os.path.isdir(orig_rtl_path)
  
  for slot_name in hub['SlotIO'].keys():
    dir = f'{target_dir}/{slot_name}'
    os.mkdir(dir)
    
    createAnchorWrapper(hub, slot_name, output_path=dir)  

    # create pblock constraints for each anchored wrapper
    createPBlockScript(hub, slot_name, output_path=dir)

    createClockXDC(slot_name, output_path=dir)

    # create Vivado script for each slot
    anchored_wrapper_path = f'{dir}/{slot_name}_anchored.v'
    createVivadoRunScript(fpga_part_name, 
                          orig_rtl_path, 
                          anchored_wrapper_path, 
                          slot_name,
                          output_path=dir)
    
    createAnchorPlacementExtractScript(hub, slot_name, dir)
    
  createGNUParallelScript(hub, target_dir)

  
