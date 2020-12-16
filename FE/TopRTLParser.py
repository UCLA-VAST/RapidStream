#! /usr/bin/python3.6
from collections import defaultdict
from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
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

    self.fifo_to_src_mod = {}
    self.fifo_to_dst_mod = {}
    self.wire_to_fifo_map = {} # str -> str

    self.initWireToFIFOMapping()
    self.initFIFOListOfModuleInst()

  # 1. no start_for FIFOs
  # 2.
  def checker(self):
    for node in self.DFS(self.top_module_ast, lambda node : isinstance(node, ast.Instance)):
      assert 'start_for' not in node.name, f'Found start FIFOs: {self.top_rtl_path} : {node.name}' 

  def DFS(self, node, filter_func):
    if filter_func(node):
      logging.debug(f'visit node {node.name}')
      yield node
    for c in node.children():
      yield from self.DFS(c, filter_func)

  def traverseVertexInAST(self):
    yield from self.DFS(self.top_module_ast, self.isVertexNode)
  
  def traverseEdgeInAST(self):
    yield from self.DFS(self.top_module_ast, self.isEdgeNode)
  
  def initFIFOListOfModuleInst(self):
    for v_node in self.traverseVertexInAST():
      for portarg in v_node.portlist:
        # filter out constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        formal_raw = portarg.portname
        actual_raw = portarg.argname.name
        
        # each fifo xxx -> xxx_din & xxx_dout, each maps to a vertex
        # note that 'dout' is the output side of FIFO, thus the input side for the vertex
        if '_dout' in formal_raw:
          assert '_dout' in actual_raw
          fifo_name = self.wire_to_fifo_map[actual_raw]
          self.mod_to_fifo_in[v_node.name].append(fifo_name) 

        elif '_din' in formal_raw:
          assert '_din' in actual_raw
          fifo_name = self.wire_to_fifo_map[actual_raw]
          self.mod_to_fifo_out[v_node.name].append(fifo_name) 
          
        else:
          continue

  def initWireToFIFOMapping(self):
    for e_node in self.traverseEdgeInAST():
      for portarg in e_node.portlist:
        # filter constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue
        # formal_raw = portarg.portname
        actual_raw = portarg.argname.name

        self.wire_to_fifo_map[actual_raw] = e_node.name

  def getInFIFOsOfModuleInst(self, inst_name):
    return self.mod_to_fifo_in[inst_name]

  def getOutFIFOsOfModuleInst(self, inst_name):
    return self.mod_to_fifo_out[inst_name]
        

  # xxx_dout -> xxx
  def getFIFONameFromWire(self, fifo_data_wire:str):
    assert '_dout' in fifo_data_wire or '_din' in fifo_data_wire, f'{fifo_data_wire} is not a FIFO data wire'   
    return self.wire_to_fifo_map[fifo_data_wire]

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

  
  # FIXME: what is InstanceList?
  def isFIFOInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' in node.module
  
  def getFIFONameFromInstanceList(self, node):
    assert(len(node.instances) == 1)
    return node.instances[0].name

  def isInstanceList(self, node):
    return isinstance(node, ast.InstanceList)