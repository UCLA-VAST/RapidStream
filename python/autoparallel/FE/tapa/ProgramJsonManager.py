#! /usr/bin/python3.6

from collections import defaultdict
from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import re
import logging
import json
import os.path
import collections, functools, operator

class ProgramJsonManager:
  def __init__(self, project_path, top_name):
    self.project_path = project_path
    self.top_rtl_path = f'{project_path}/hdl/{top_name}_{top_name}.v'
    program_json_path = f'{project_path}/program.json'
    self.program = json.loads(open(program_json_path).read())
    self.top_name = top_name

    # be consistent with the RTL
    self.__updateNaming()

    # update json to include fifo width
    self.e_name_to_width = {}
    self.__extractFIFOWidth()

    self.v_name_to_v_module = {}
    self.v_module_to_area = {}

    self.__initVertexMapping()

  def __DFS(self, node, filter_func):
    if filter_func(node):
      try:
        logging.debug(f'visit node {node.name}')
      except:
        pass
        # logging.debug(f'node in line {node.lineno} has no name')
      yield node
    for c in node.children():
      yield from self.__DFS(c, filter_func)

  def __traverseEdgeInAST(self):
    top_module_ast, directives = rtl_parse([self.top_rtl_path]) 
    is_edge_node = lambda node : isinstance(node, ast.Instance) and 'fifo' in node.module
    yield from self.__DFS(top_module_ast, is_edge_node)

  def __extractFIFOWidth(self):
    for e_node in self.__traverseEdgeInAST():
      name = e_node.name
      for param in e_node.parameterlist:
        if 'WIDTH' in param.paramname:
          self.e_name_to_width[name] = int(param.argname.value)
          break
      assert name in self.e_name_to_width, f'{name}'

    # update json
    fifos_dict = self.getFIFOSection()

    for e_name, info in fifos_dict.items():
      info['width'] = self.e_name_to_width[e_name]

  def __initVertexMapping(self):
    fifos_dict = self.getFIFOSection()

    for e_name, info in fifos_dict.items():
      src = info['produced_by']
      dst = info['consumed_by']
      src_name = f'{src[0]}_{src[1]}'
      src_module = src[0]
      dst_name = f'{dst[0]}_{dst[1]}'
      dst_module = dst[0]

      self.v_name_to_v_module[src_name] = src_module
      self.v_name_to_v_module[dst_name] = dst_module     

  def __updateNaming(self):
    fifos_dict = self.getFIFOSection()
    fifos_dict_new = {}

    # change from fifo_name[0] to fifo_name_0
    for e_name_orig, info in fifos_dict.items():
      if re.search(r'\[\d+\]', e_name_orig):
        e_name = re.sub(r'\[(\d+)\]', r'_\1', e_name_orig)
        fifos_dict_new[e_name] = info
    
    # change from [kernel_name, 0] to kernel_name_0
    for e_name, info in fifos_dict_new.items():
      info['produced_by_module_name'] = info['consumed_by'][0] + '_' + str(info['consumed_by'][1])
      info['consumed_by_module_name'] = info['consumed_by'][0] + '_' + str(info['consumed_by'][1])

    self.__updateFIFOSection(fifos_dict_new)    

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
  
  def __updateFIFOSection(self, fifo_sec_new):
    self.program['tasks'][self.top_name]['fifos'] = fifo_sec_new

  def getFIFOSection(self):
    return self.program['tasks'][self.top_name]['fifos']

  def getVNameToModule(self):
    return self.v_name_to_v_module
  
  def getAreaOfModule(self, v_module):
    return self.__getAreaBasedOnIndividualReport(v_module)

  def getVertexTotalArea(self):
    v_name_to_v_area = {v_name: self.getAreaOfModule(v_module)
      for v_name, v_module in self.v_name_to_v_module.items()}

    return dict(functools.reduce(operator.add, \
      map(collections.Counter, v_name_to_v_area.values())))