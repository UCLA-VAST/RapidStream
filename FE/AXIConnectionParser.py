#! /usr/bin/python3.6
from collections import defaultdict
from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import re
import logging
import json

class AXIConnectionParser:
  def __init__(self, top_rtl_path):
    self.top_rtl_path = top_rtl_path
    self.top_module_ast, directives = rtl_parse([top_rtl_path]) 
    self.top_m_axi_port_to_io_module = self.__getPortToModule()
    self.s_axi_module = self.__initSAXIModule()
    # print(json.dumps(self.top_m_axi_port_to_io_module, indent=2))

  def __getTopMAXIs(self):
    top = open(self.top_rtl_path, 'r').read()
    top_axi_list = re.findall(r'input[ ]+m_axi_(.*)_ARREADY', top)
    return top_axi_list

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

  def __isVertexNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' not in node.module

  def traverseVertexInAST(self):
    yield from self.__DFS(self.top_module_ast, self.__isVertexNode)

  # extract the modules directly connected to the top M_AXI interfaces
  def __getPortToModule(self):
    m_axi_list = self.__getTopMAXIs()

    top_m_axi_port_to_io_module = {}

    for v_node in self.traverseVertexInAST():
      interface_wire_set = set()
      for portarg in v_node.portlist:
        if not isinstance(portarg.argname, ast.Identifier): continue
        interface_wire_set.add(portarg.argname.name)
      # interface_wire_set = set([portarg.argname.name  for portarg in v_node.portlist if not isinstance(portarg.argname, ast.Identifier)] )
      for axi_name in m_axi_list:
        if f'm_axi_{axi_name}_ARREADY' in interface_wire_set:
          top_m_axi_port_to_io_module[axi_name] = (v_node.module, v_node.name)
    
    assert len(top_m_axi_port_to_io_module) == len(m_axi_list)
    return top_m_axi_port_to_io_module

  def getIOModuleNameOfAXI(self, axi_name):
    return self.top_m_axi_port_to_io_module[axi_name][1] # get name 

  def getAllAXIModules(self) -> list:
    axi_modules = list(self.top_m_axi_port_to_io_module.values())
    axi_modules.append(self.s_axi_module)

    return axi_modules
  
  def __initSAXIModule(self) -> list:
    for v_node in self.traverseVertexInAST():
      for portarg in v_node.portlist:
        if not isinstance(portarg.argname, ast.Identifier): continue
        if 's_axi_control' in portarg.argname.name:
          return (v_node.module, v_node.name)

  def getSAXIName(self):
    return self.s_axi_module[1]

if __name__ == '__main__':
  top_rtl_path = '/home/einsx7/auto-parallel/src/benchmark/SSSP-tapa/hdl/SSSP_SSSP.v'
  AXIConnectionParser(top_rtl_path)
