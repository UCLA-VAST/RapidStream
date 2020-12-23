#! /usr/bin/python3.6
from collections import defaultdict
from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import re
import logging


class TopRTLParser:

  fifo_dout_format = '([^ ]*[^_])_+dout'
  fifo_din_format = '([^ ]*[^_])_+din'

  def __init__(self, top_rtl_path):
    self.top_rtl_path = top_rtl_path
    self.top_module_ast, directives = rtl_parse([top_rtl_path]) 
    self.checker()

    self.mod_to_fifo_in = defaultdict(list)
    self.mod_to_fifo_out = defaultdict(list)

    self.wire_to_fifo_name = {} # str -> str
    self.fifo_name_to_wires = defaultdict(list) # fifo -> interface wires
    self.inst_name_to_rtl = {}
    self.reg_wire_decl_list = [] # all wire and reg declaration 
    self.io_decl_list_with_comma = []
    self.codegen = ASTCodeGenerator()

    self.initWireToFIFOMapping()
    self.initFIFOListOfModuleInst()
    self.initRTLOfAllInsts()
    self.initDeclList()
    
  # 1. no start_for FIFOs
  # 2. each inst has different name
  def checker(self):
    for node in self.DFS(self.top_module_ast, lambda node : isinstance(node, ast.Instance)):
      assert 'start_for' not in node.name, f'Found start FIFOs: {self.top_rtl_path} : {node.name}' 

    names = set()
    for node in self.DFS(self.top_module_ast, lambda node : isinstance(node, ast.Instance)):
      if node.name not in names:
        names.add(node.name)
      else:
        assert False, f'Found duplicated name for instance {node.name}'

  def DFS(self, node, filter_func):
    if filter_func(node):
      try:
        logging.debug(f'visit node {node.name}')
      except:
        logging.debug(f'node in line {node.lineno} has no name')
      yield node
    for c in node.children():
      yield from self.DFS(c, filter_func)

  def traverseVertexInAST(self):
    yield from self.DFS(self.top_module_ast, self.isVertexNode)
  
  def traverseEdgeInAST(self):
    yield from self.DFS(self.top_module_ast, self.isEdgeNode)
  
  def initRTLOfAllInsts(self):
    for v_inst_list in self.DFS(self.top_module_ast, self.isVertexInstanceList):
      assert len(v_inst_list.instances) == 1, f'unsupported RTL coding style at line {v_inst_list.lineno}'
      v_node = v_inst_list.instances[0]
      self.inst_name_to_rtl[v_node.name] = self.codegen.visit(v_inst_list)

    for e_inst_list in self.DFS(self.top_module_ast, self.isEdgeInstanceList):
      assert len(e_inst_list.instances) == 1, f'unsupported RTL coding style at line {e_inst_list.lineno}'
      e_node = e_inst_list.instances[0]
      self.inst_name_to_rtl[e_node.name] = self.codegen.visit(e_inst_list)

  def initDeclList(self):

    for decl in self.DFS(self.top_module_ast, lambda node : isinstance(node, ast.Decl)):
      decl = self.codegen.visit(decl)
      if re.search(r'^input', decl) or re.search(r'^output', decl):
        self.io_decl_list_with_comma.append(decl)
      else:
        self.reg_wire_decl_list.append(decl.replace(';', ','))

  def initFIFOListOfModuleInst(self):
    for v_node in self.traverseVertexInAST():
      for portarg in v_node.portlist:
        # filter out constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        port_name = portarg.portname
        wire_name = portarg.argname.name
        
        # each fifo xxx -> xxx_din & xxx_dout, each maps to a vertex
        # note that 'dout' is the output side of FIFO, thus the input side for the vertex
        if '_dout' in port_name:
          assert '_dout' in wire_name
          fifo_name = self.wire_to_fifo_name[wire_name]
          self.mod_to_fifo_in[v_node.name].append(fifo_name) 

        elif '_din' in port_name:
          assert '_din' in wire_name
          fifo_name = self.wire_to_fifo_name[wire_name]
          self.mod_to_fifo_out[v_node.name].append(fifo_name) 
          
        else:
          continue

  def initWireToFIFOMapping(self):
    for e_node in self.traverseEdgeInAST():
      for portarg in e_node.portlist:
        # filter constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        wire_name = portarg.argname.name
        self.wire_to_fifo_name[wire_name] = e_node.name
        self.fifo_name_to_wires[e_node.name].append(wire_name)

  def getRegAndWireDeclList(self):
    return self.reg_wire_decl_list

  def getRTLOfInst(self, inst_name):
    return self.inst_name_to_rtl[inst_name]

  def getIODeclListWithComma(self):
    return self.io_decl_list_with_comma

  def getInFIFOsOfModuleInst(self, inst_name):
    return self.mod_to_fifo_in[inst_name]

  def getOutFIFOsOfModuleInst(self, inst_name):
    return self.mod_to_fifo_out[inst_name]

  # fifo_w32_d2_A xxx -> 32
  def getFIFOWidthFromFIFOType(self, fifo_type):
    match = re.search(r'_w(\d+)_d(\d+)_', fifo_type)
    assert match, f'wrong FIFO instance name: {fifo_type}'
    return int(match.group(1)) # group 111111

  # fifo_w32_d2_A xxx -> 2
  def getFIFODepthFromFIFOType(self, fifo_type):
    match = re.search(r'_w(\d+)_d(\d+)_', fifo_type)
    assert match, f'wrong FIFO instance name: {fifo_type}'
    return int(match.group(2)) # group 222222
    
  def isVertexNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' not in node.module

  def isEdgeNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' in node.module

  def isVertexInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' not in node.module
  
  def isEdgeInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' in node.module
  
  def getFIFONameFromInstanceList(self, node):
    assert(len(node.instances) == 1)
    return node.instances[0].name

  def isInstanceList(self, node):
    return isinstance(node, ast.InstanceList)