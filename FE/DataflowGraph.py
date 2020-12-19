#! /usr/bin/python3.6

from TopRTLParser import TopRTLParser
from HLSProjectManager import HLSProjectManager
import logging
import math

class Edge:
  def __init__(self, name:str):
    self.src : Vertex = None
    self.dst : Vertex = None
    self.width = -1
    self.depth = -1
    self.addr_width = -1
    self.name = name

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return self.name == other.name

class Vertex():
  def __init__(self, type:str, name : str):
    self.in_edges = [] # stores Edge objects
    self.out_edges = []
    self.in_edge_names = [] # stores Edge objects
    self.out_edge_names = []
    self.type = type
    self.name = name
    self.id = self.type + self.name
    self.area = {} # str_name -> count
    self.sub_vertices = {} # pp id -> sub vertex
    self.actual_to_sub = {} # map actual edge name -> sub vertex
    self.vertical_cut = []
    self.horizontal_cut = []

    logging.info(f'[Init vertex] create vertix {self.name} of type {self.type}')

  def __hash__(self):
    return hash(self.id)

  def __eq__(self, other):
    return self.id == other.id

  def getEdgeNames(self):
    return self.in_edge_names + self.out_edge_names

  def getEdges(self):
    return self.in_edges + self.out_edges

class DataflowGraph:
  def __init__(self, hls_prj_manager : HLSProjectManager, top_rtl_parser : TopRTLParser):
    self.hls_prj_manager = hls_prj_manager
    self.top_rtl_parser = top_rtl_parser

    self.vertices = {} # name -> Vertex
    self.edges = {} # name -> Edge

    for v_node in self.top_rtl_parser.traverseVertexInAST():
      self.initVertices(v_node)

    for e_node in self.top_rtl_parser.traverseEdgeInAST():
      self.initEdges(e_node)

    self.linkEdgeAndVertex()
    
    self.checker()

  def checker(self):
    v_name_list = [v.type + v.name for v in self.getAllVertices()]
    e_name_list = [e.name for e in self.getAllEdges()]
    assert len(v_name_list) == len(set(v_name_list)), 'Find repeated modules'
    assert len(e_name_list) == len(set(e_name_list))

  def initVertices(self, v_node):

    v = Vertex(v_node.module, v_node.name)

    # get area
    v.area = self.hls_prj_manager.getAreaFromModuleType(v.type)
    
    v.in_edge_names = self.top_rtl_parser.getInFIFOsOfModuleInst(v.name)
    v.out_edge_names = self.top_rtl_parser.getOutFIFOsOfModuleInst(v.name)

    self.vertices[v_node.name] = v

  def initEdges(self, e_node):

    e = Edge(e_node.name)

    # extract width
    e.width = self.top_rtl_parser.getFIFOWidthFromFIFOType(e_node.module)
    e.depth = self.top_rtl_parser.getFIFODepthFromFIFOType(e_node.module)
    e.addr_width = int(math.log2(e.depth)+1)

    self.edges[e_node.name] = e

  def linkEdgeAndVertex(self):
    for v in self.vertices.values():
      for fifo_in_name in v.in_edge_names:
        fifo_in = self.edges[fifo_in_name]
        fifo_in.dst = v
        v.in_edges.append(fifo_in)
      for fifo_out_name in v.out_edge_names:
        fifo_out = self.edges[fifo_out_name]
        fifo_out.src = v
        v.out_edges.append(fifo_out)

  def printVertices(self):
    for v in self.vertices.values():
      logging.debug(f'{v.name}: {v.area}')
      for e in v.in_edges:
        logging.debug(f'  <- {e.name}')
      for e in v.out_edges:
        logging.debug(f'  -> {e.name}')

  def printEdges(self):
    for e in self.edges.values():
      logging.debug(f'{e.name}: {e.src.name} -> {e.dst.name}')

  def getAllVertices(self):
    return self.vertices.values()

  def getAllEdges(self):
    return self.edges.values()

  def getNameToVertexMap(self):
    return self.vertices

  def getNameToEdgeMap(self):
    return self.edges

  def getVertex(self, v_name):
    return self.vertices[v_name]