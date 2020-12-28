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
    self.__checker()

    self.mod_to_fifo_in = defaultdict(list)
    self.mod_to_fifo_out = defaultdict(list)

    self.wire_to_fifo_name = {} # str -> str
    self.fifo_name_to_wires = defaultdict(list) # fifo -> interface wires
    self.wire_to_v_name = {} # str -> str
    self.v_name_to_wires = defaultdict(list) # vertex -> interface wires
    self.inst_name_to_rtl = {}
    self.reg_wire_name_to_width = {} # from name to full declaration (with width, etc) 
    self.io_name_to_width = {}
    self.io_name_to_dir = {}
    self.all_decl_except_io = []
    self.codegen = ASTCodeGenerator()

    self.__initWireToFIFOMapping()
    self.__initWireToVertexMapping()
    self.__initFIFOListOfModuleInst()
    self.__initRTLOfAllInsts()
    self.__initDeclList()
    
  # 1. no start_for FIFOs
  # 2. each inst has different name
  def __checker(self):
    for node in self.__DFS(self.top_module_ast, lambda node : isinstance(node, ast.Instance)):
      assert 'start_for' not in node.name, f'Found start FIFOs: {self.top_rtl_path} : {node.name}' 

    names = set()
    for node in self.__DFS(self.top_module_ast, lambda node : isinstance(node, ast.Instance)):
      if node.name not in names:
        names.add(node.name)
      else:
        assert False, f'Found duplicated name for instance {node.name}'

  def __DFS(self, node, filter_func):
    if filter_func(node):
      try:
        logging.debug(f'visit node {node.name}')
      except:
        logging.debug(f'node in line {node.lineno} has no name')
      yield node
    for c in node.children():
      yield from self.__DFS(c, filter_func)

  def __initRTLOfAllInsts(self):
    for v_inst_list in self.__DFS(self.top_module_ast, self.__isVertexInstanceList):
      assert len(v_inst_list.instances) == 1, f'unsupported RTL coding style at line {v_inst_list.lineno}'
      v_node = v_inst_list.instances[0]
      self.inst_name_to_rtl[v_node.name] = self.codegen.visit(v_inst_list)

    for e_inst_list in self.__DFS(self.top_module_ast, self.__isEdgeInstanceList):
      assert len(e_inst_list.instances) == 1, f'unsupported RTL coding style at line {e_inst_list.lineno}'
      e_node = e_inst_list.instances[0]
      self.inst_name_to_rtl[e_node.name] = self.codegen.visit(e_inst_list)

  # get mapping from reg/wire/io name to width/direction
  def __initDeclList(self):

    # get a copy of all delcaration
    for decl_node in self.__DFS(self.top_module_ast, lambda node : isinstance(node, ast.Decl)):
      assert len(decl_node.children()) == 1
      content = decl_node.children()[0]
      name = content.name

      if not isinstance(content, ast.Input) and not isinstance(content, ast.Output):
        self.all_decl_except_io.append(self.codegen.visit(decl_node))

    # initialize various mappings
    for decl_node in self.__DFS(self.top_module_ast, lambda node : isinstance(node, ast.Decl)):
      assert len(decl_node.children()) == 1
      content = decl_node.children()[0]
      name = content.name

      # filter out ast.Parameter
      if isinstance(content, ast.Parameter):
        continue
      
      width_node = content.width
      if width_node:
        width = self.codegen.visit(width_node)
      else:
        width = ''

      if isinstance(content, ast.Input):
        self.io_name_to_dir[name] = 'input'
        self.io_name_to_width[name] = width

      elif isinstance(content, ast.Output):
        self.io_name_to_dir[name] = 'output'
        self.io_name_to_width[name] = width

      elif isinstance(content, ast.Wire) or isinstance(content, ast.Reg):
        self.reg_wire_name_to_width[name] = width

      else:
        logging.debug(f'unrecorded Decl statement: {name} @ line {decl_node.lineno}')

  def __initFIFOListOfModuleInst(self):
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

  def __initWireToFIFOMapping(self):
    for e_node in self.traverseEdgeInAST():
      for portarg in e_node.portlist:
        # filter constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        wire_name = portarg.argname.name
        self.wire_to_fifo_name[wire_name] = e_node.name
        self.fifo_name_to_wires[e_node.name].append(wire_name)

  def __initWireToVertexMapping(self):
    for v_node in self.traverseVertexInAST():
      for portarg in v_node.portlist:
        # filter constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        wire_name = portarg.argname.name
        self.wire_to_v_name[wire_name] = v_node.name
        self.v_name_to_wires[v_node.name].append(wire_name)
  
  def __isVertexNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' not in node.module

  def __isEdgeNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' in node.module

  def __isVertexInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' not in node.module
  
  def __isEdgeInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' in node.module
  
  #                                                 #
  # ---------------- Public Methods --------------- #
  #                                                 #

  def traverseVertexInAST(self):
    yield from self.__DFS(self.top_module_ast, self.__isVertexNode)
  
  def traverseEdgeInAST(self):
    yield from self.__DFS(self.top_module_ast, self.__isEdgeNode)
  
  # get the interface wires of vertex or edges
  def getWiresOfFIFOName(self, inst_name) -> list:
    return self.fifo_name_to_wires[inst_name]

  def getWiresOfVertexName(self, v_name) -> list:
    return self.v_name_to_wires[v_name]

  def getWidthOfRegOrWire(self, name):
    return self.reg_wire_name_to_width[name]

  def getRTLOfInst(self, inst_name : str):
    return self.inst_name_to_rtl[inst_name]

  def getWidthOfIO(self, io_name):
    return self.io_name_to_width[io_name]

  def getAllDeclExceptIO(self):
    return self.all_decl_except_io

  def isIO(self, io_name):
    return io_name in self.io_name_to_width

  def getDirOfIO(self, io_name):
    return self.io_name_to_dir[io_name]

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

  def getFIFONameFromInstanceList(self, node):
    assert(len(node.instances) == 1)
    return node.instances[0].name
