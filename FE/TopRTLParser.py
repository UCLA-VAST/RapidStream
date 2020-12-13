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
    self.initFIFOListOfModuleInst()

    self.fifo_to_src_mod = {}
    self.fifo_to_dst_mod = {}
    self.initSrcAndDstOfFIFO()

  # 1. no start_for FIFOs
  # 2.
  def checker(self):
    for node in self.DFS(self.top_module_ast, lambda x : True):
      assert 'start_for' not in node.name, 'Found start FIFOs. Must use disable_start_propagation' 

  def DFS(self, node, filter_func):
    if filter_func(node):
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
          fifo_name = re.search(TopRTLParser.fifo_dout_format, actual_raw).group(1)
          self.mod_to_fifo_in[v_node.name].append(fifo_name) 

        elif '_din' in formal_raw:
          assert '_din' in actual_raw
          fifo_name = re.search(TopRTLParser.fifo_din_format, actual_raw).group(1)
          self.mod_to_fifo_out[v_node.name].append(fifo_name) 
          
        else:
          continue

  def initSrcAndDstOfFIFO(self):
    for e_node in self.traverseEdgeInAST():
      # extract wire name
      # augment vertices with edge info
      for portarg in e_node.portlist:
        # filter constant ports
        if(not isinstance(portarg.argname, ast.Identifier)):
          continue

        formal_raw = portarg.portname
        actual_raw = portarg.argname.name

        formal_raw = portarg.portname
        actual_raw = portarg.argname.name
        
        # each fifo xxx -> xxx_din & xxx_dout, each maps to a vertex
        # note that 'dout' is the output side of FIFO, thus the input side for the vertex
        if '_dout' in formal_raw:
          assert '_dout' in actual_raw
          fifo_name = re.search(TopRTLParser.fifo_dout_format, actual_raw).group(1)
          self.fifo_to_dst_mod[e_node.name] = fifo_name

        elif '_din' in formal_raw:
          assert '_din' in actual_raw
          fifo_name = re.search(TopRTLParser.fifo_din_format, actual_raw).group(1)
          self.fifo_to_src_mod[e_node.name] = fifo_name


  def getInFIFOsOfModuleInst(self, mod_name):
    return self.mod_to_fifo_in[mod_name]

  def getOutFIFOsOfModuleInst(self, mod_name):
    return self.mod_to_fifo_out[mod_name]
        

  # xxx_dout -> xxx
  def getFIFONameFromDataPort(self, data_port:str):


    if ('_dout' in data_port):
      return re.search(TopRTLParser.fifo_dout_format, data_port).group(1)
    elif ('_din' in data_port):
      return re.search(TopRTLParser.fifo_din_format,  data_port).group(1)
    else:
      assert False, f'{data_port} is not a FIFO data port'   

  # fifo_w32_d2_A xxx -> 32
  def getFIFOWidthFromHLSNaming(self, fifo_inst_name):
    match = re.search(r'_w(\d+)_d(\d+)_', fifo_inst_name)
    assert match, f'wrong FIFO instance name: {fifo_inst_name}'
    return int(match.group(1)) # group 111111

  # fifo_w32_d2_A xxx -> 2
  def getFIFODepthFromHLSNaming(self, fifo_inst_name):
    match = re.search(r'_w(\d+)_d(\d+)_', fifo_inst_name)
    assert match, f'wrong FIFO instance name: {fifo_inst_name}'
    return int(match.group(2)) # group 222222
    
  def isVertexNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' not in node.top_module_ast

  def isEdgeNode(self, node):
    return isinstance(node, ast.Instance) and 'fifo' not in node.top_module_ast

  
  # FIXME: what is InstanceList?
  def isFIFOInstanceList(self, node):
    return isinstance(node, ast.InstanceList) and 'fifo' in node.module
  
  def getFIFONameFromInstanceList(self, node):
    assert(len(node.instances) == 1)
    return node.instances[0].name

  def isInstanceList(self, node):
    return isinstance(node, ast.InstanceList)