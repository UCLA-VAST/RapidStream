#! /usr/bin/python3.6

import logging
import re
from os.path import isfile, isdir
from collections import defaultdict

class HLSProjectManager:
  def __init__(
      self, 
      top_func_name,
      hls_prj_path, 
      hls_solution_name='solution'):
    self.top_func_name = top_func_name
    self.hls_prj_path = hls_prj_path
    self.hls_solution_name = hls_solution_name
    self.area_map = {} # name -> area
    self.__checker()

    self.getAreaOfAllInst()

  def __checker(self):
    # rtl name should contain not the file extension
    assert self.top_func_name[-2:] != '.v'

  def getCsynthReportDir(self):
    ans = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/report/'
    assert isdir(ans), ans
    return ans

  def getScheReportDir(self):
    ans =  f'{self.hls_prj_path}/{self.hls_solution_name}/.autopilot/db/'
    assert isdir(ans), ans
    return ans

  def getRTLDir(self):
    ans = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/verilog/'
    assert isdir(ans), ans
    return ans

  def getTopRTLPath(self):
    opt1 = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/verilog/{self.top_func_name}.v'
    opt2 = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/verilog/{self.top_func_name}_{self.top_func_name}.v'
    if isfile(opt1):
      return opt1
    elif isfile(opt2):
      return opt2
    else:
      assert False, f'cannot find the RTL file for {self.top_func_name}'  

  # kernel0 or kernel0_kernel0
  def getTopModuleName(self):
    opt1 = rf'{self.top_func_name}'
    opt2 = rf'{self.top_func_name}_{self.top_func_name}'
    path = self.getTopRTLPath()
    if re.search(opt2, path):
      return opt2
    elif re.search(opt1, path):
      return opt1
    else:
      assert False, f'cannot find the top RTL module name'   

  def getScheReportFromModuleType(self, mod_type):
    opt1 = self.getScheReportDir() + f'/{mod_type}' + '.verbose.sched.rpt'
    opt2 = self.getScheReportDir() + f'/{mod_type[len(self.top_func_name)+1:]}' + '.verbose.sched.rpt'
    
    if isfile(opt1):
      return opt1
    elif isfile(opt2):
      return opt2
    else:
      assert False, f'cannot find the schedule report for {mod_type}'

  def getHLSReportFromModuleType(self, mod_type):
    opt1 = self.getCsynthReportDir() + f'/{mod_type}' + '_csynth.rpt'
    opt2 = self.getCsynthReportDir() + f'/{mod_type[len(self.top_func_name)+1:]}' + '_csynth.rpt'
    
    if isfile(opt1):
      return opt1
    elif isfile(opt2):
      return opt2
    else:
      assert False, f'cannot find the HLS report for {mod_type}'    

  def getAreaOfAllInst(self):
    top_rpt_addr = self.getHLSReportFromModuleType(self.top_func_name)
    rpt = open(top_rpt_addr, 'r')
    line = ''

    while r'Utilization Estimates' not in line:
      line = rpt.readline()

    # ......
    # + Detail: 
    # * Instance: 
    # +-------------------------------------+------------------------------------+---------+-------+------+------+-----+
    # |               Instance              |               Module               | BRAM_18K| DSP48E|  FF  |  LUT | URAM|
    # +-------------------------------------+------------------------------------+---------+-------+------+------+-----+
    # |A_IO_L1_in_0_0_U0                    |A_IO_L1_in_0_0_s                    |        0|      0|   429|   334|    0|
    # |A_IO_L1_in_0_10_U0                   |A_IO_L1_in_0_10_s                   |        0|      0|   425|   334|    0|
    # ......

    while r'+ Detail:' not in line:
      line = rpt.readline()

    line = rpt.readline()   # * Instance: 
    assert r'* Instance:' in line, line
    line = rpt.readline()   # +-------------
    assert r'+-------' in line, line
    line = rpt.readline()   # |               Instance  
    assert re.search(r'[| ]*Instance[ ]*[| ]*Module[ ]*[| ]*BRAM_18K[ |]+DSP[48E |]+FF[ |]+LUT[ |]+URAM', line), line
    line = rpt.readline()   # +----------
    assert r'+-------' in line, line

    line = rpt.readline()   # +----------
    while r'+-------' not in line:
      #                   |   (inst )     |    (mod )     |    (bram)   |    (dsp)    |    (ff )    |   (lut)     |    (uram)
      match = re.search(r'[| ]*([^ ]+)[ ]*[| ]*([^ ]+)[ ]*[| ]*(\d+)[ ]*[| ]*(\d+)[ ]*[| ]*(\d+)[ ]*[| ]*(\d+)[ ]*[| ]*(\d+)', line)
      assert match, line

      inst_name = match.group(1)
      mod_type = match.group(2)
      bram = int(match.group(3))
      dsp  = int(match.group(4))
      ff   = int(match.group(5))
      lut  = int(match.group(6))
      uram = int(match.group(7))
      self.area_map[mod_type] = {'BRAM':bram, 'DSP':dsp, 'FF':ff, 'LUT':lut, 'URAM':uram}

      line = rpt.readline() 
    rpt.close()
    
  def getAreaFromModuleType(self, mod_type):
    # if '_axi' in mod_type:
    #   if mod_type not in self.area_map:
    #     assert re.search(f'{self.top_func_name}_{self.top_func_name}', mod_type), mod_type
    #     mod_type = mod_type[len(self.top_func_name)+1:]
    
    opt1 = mod_type
    opt2 = mod_type[len(self.top_func_name)+1:]
    if opt1 in self.area_map: 
      return self.area_map[opt1]
    elif opt2 in self.area_map:
      return self.area_map[opt2]
    else:
      return self.getAreaBasedOnIndividualReport(mod_type)

  def getAreaBasedOnIndividualReport(self, mod_type):
    logging.debug(f'Area information of instance {mod_type} not found in report for the top func, but has its own report.')

    rpt_addr = self.getHLSReportFromModuleType(mod_type)
    rpt = open(rpt_addr, 'r')

    for line in rpt:
      if ('Utilization Estimates' in line):
        for line in rpt:
          if ('Name' in line):
            assert re.search(r'BRAM[_]18K[ |]*DSP[48E |]*FF[ |]*LUT[ |]*URAM', line), f'HLS has changed the item order in reports! {rpt_addr} : {line}'

          if ('Total' in line):
            x = re.findall(r'\d+', line)
            return {'BRAM':int(x[0]), 'DSP':int(x[1]), 'FF':int(x[2]), 'LUT':int(x[3]), 'URAM':int(x[4])}

    assert False, 'Error in parsing the HLS report'

  def getTotalArea(self):
    return self.getAreaBasedOnIndividualReport(self.top_func_name)