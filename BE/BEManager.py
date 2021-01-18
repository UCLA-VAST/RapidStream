#! /usr/bin/python3.6
import logging
import json
import os
import shutil
from CreateAnchorWrapper import *
from GenAnchorConstraints import *

if __name__ == '__main__':
  target_dir = '/home/einsx7/auto-parallel/test/parallel_run'
  fe_result_path = '/home/einsx7/auto-parallel/src/FE/FE_result.json'

  if os.path.isdir(target_dir):
    shutil.rmtree(target_dir)
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


  
