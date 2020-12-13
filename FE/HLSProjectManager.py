import logging
import re
from os.path import isfile, isdir

class HLSProjectManager:
  def __init__(
      self, 
      top_func_name,
      hls_prj_path, 
      hls_solution_name='solution'):
    self.top_func_name = top_func_name
    self.hls_prj_path = hls_prj_path
    self.hls_solution_name = hls_solution_name

    self.checker()

  def checker(self):
    # rtl name should contain not the file extension
    assert self.top_func_name[-2:] != '.v'

  def getCsynthReportDir(self):
    ans = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/report/'
    assert isdir(ans)
    return ans

  def getScheReportDir(self):
    ans =  f'{self.hls_prj_path}/{self.hls_solution_name}/.autopilot/db/'
    assert isdir(ans)
    return ans

  def getRTLDir(self):
    ans = f'{self.hls_prj_path}/{self.hls_solution_name}/syn/verilog/'
    assert isdir(ans)
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


  def getScheReportFromModuleName(self, mod_name):
    opt1 = self.getScheReportDir() + f'/{mod_name}' + '.verbose.sched.rpt'
    opt2 = self.getScheReportDir() + f'/{mod_name[len(self.top_func_name)+1:]}' + '.verbose.sched.rpt'
    
    if isfile(opt1):
      return opt1
    elif isfile(opt2):
      return opt2
    else:
      assert False, f'cannot find the schedule report for {mod_name}'

  def getHLSReportFromModuleName(self, mod_name):
    opt1 = self.getCsynthReportDir() + f'/{mod_name}' + '_csynth.rpt'
    opt2 = self.getCsynthReportDir() + f'/{mod_name[len(self.top_func_name)+1:]}' + '_csynth.rpt'
    
    if isfile(opt1):
      return opt1
    elif isfile(opt2):
      return opt2
    else:
      assert False, f'cannot find the HLS report for {mod_name}'    

  def getAreaFromModuleName(self, mod_name):

    rpt_addr = self.getHLSReportFromModuleName(mod_name)
    rpt = open(rpt_addr, 'r')

    for line in rpt:
      if ('Utilization Estimates' in line):
        for line in rpt:
          if ('Name' in line):
            assert re.match(r'BRAM_18K[ |]+DSP48E[ |]+FF[ |]+LUT[ |]+URAM', line), 'HLS has changed the item order in reports!'

          if ('Total' in line):
            x = re.findall(r'\d+', line)
            return {'BRAM':int(x[0]), 'DSP':int(x[1]), 'FF':int(x[2]), 'LUT':int(x[3]), 'URAM':int(x[4])}

    assert False, 'Error in parsing the HLS report'