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

class Vertex():
  def __init__(self, type:str, name : str):
    self.in_edges = [] # stores Edge objects
    self.out_edges = []
    self.in_edge_names = [] # stores Edge objects
    self.out_edge_names = []
    self.type = type
    self.name = name
    self.area = {} # str_name -> count
    self.sub_vertices = {} # pp id -> sub vertex
    self.actual_to_sub = {} # map actual edge name -> sub vertex
    self.vertical_cut = []
    self.horizontal_cut = []

    logging.info(f'[Init vertex] create vertix {self.name} of type {self.type}')

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

  def initVertices(self, v_node):

    v = Vertex(v_node.module, v_node.name)

    # get area
    v.area = self.hls_prj_manager.getArea(v.type)
    
    v.in_edge_names = self.top_rtl_parser.getInFIFOsOfModuleInst(v.name)
    v.out_edge_names = self.top_rtl_parser.getOutFIFOsOfModuleInst(v.name)

    self.vertices[v_node.name] = v

  def initEdges(self, e_node):

    e = Edge(e_node.name)

    # extract width
    e.width = self.top_rtl_parser.getFIFOWidthFromHLSNaming(e_node)
    e.depth = self.top_rtl_parser.getFIFODepthFromHLSNaming(e_node)
    e.addr_width = int(math.log2(e.depth)+1)

    self.edges[e_node.name] = e

  def linkEdgeAndVertex(self):
    for e in self.edges.values():
      src_name = self.top_rtl_parser.getSrcModuleOfFIFO(e.name)
      dst_name = self.top_rtl_parser.getDstModuleOfFIFO(e.name)
      e.src = self.vertices[src_name]
      e.dst = self.vertices[dst_name]
      e.src.out_edges.append(e)
      e.dst.in_edges.append(e)

    # safe check
    for v in self.vertices.values():
      assert len(v.in_edges) == len(v.in_edge_names)
      assert len(v.out_edges) == len(v.out_edge_name)

  def printVertices(self):
    for v in self.vertices.values():
      print(f'{v.name}: {v.area}')
      for e in v.in_edges:
        print(f'  <- {e.name}')
      for e in v.out_edges:
        print(f'  -> {e.name}')

  def printEdges(self):
    for e in self.edges.values():
      print(f'{e.name}: {e.src.name} -> {e.dst.name}')

   