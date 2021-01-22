from collections import defaultdict
import re
import logging
import os.path
import collections, functools, operator

class ProgramJsonManager:
  def __init__(self, project_path, fifo_section, v_name_to_v_module):
    self.project_path = project_path
    self.fifo_section = fifo_section

    self.v_name_to_v_module = v_name_to_v_module
    self.v_module_to_area = {}

  def __getAreaBasedOnIndividualReport(self, mod_type):
    rpt_addr = f'{self.project_path}/report/{mod_type}_csynth.rpt'
    if not os.path.isfile(rpt_addr):
      logging.warning(f'No area information for module {mod_type}')
      return {'BRAM':0, 'DSP':0, 'FF':0, 'LUT':0, 'URAM':0}

    rpt = open(rpt_addr, 'r')
    for line in rpt:
      if ('Utilization Estimates' in line):
        for line in rpt:
          if ('Name' in line):
            assert re.search(r'BRAM[_]18K[ |]*DSP48E[ |]*FF[ |]*LUT[ |]*URAM', line), f'HLS has changed the item order in reports! {rpt_addr} : {line}'

          if ('Total' in line):
            x = re.findall(r'\d+', line)
            return {'BRAM':int(x[0]), 'DSP':int(x[1]), 'FF':int(x[2]), 'LUT':int(x[3]), 'URAM':int(x[4])}

    assert False, 'Error in parsing the HLS report'
  
  def getFIFOSection(self):
    return self.fifo_section

  def getVNameToModule(self):
    return self.v_name_to_v_module
  
  def getAreaOfModule(self, v_module):
    return self.__getAreaBasedOnIndividualReport(v_module)

  def getVertexTotalArea(self):
    v_name_to_v_area = {v_name: self.getAreaOfModule(v_module)
      for v_name, v_module in self.v_name_to_v_module.items()}

    return dict(functools.reduce(operator.add, \
      map(collections.Counter, v_name_to_v_area.values())))