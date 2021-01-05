#! /usr/bin/python3.6
import sys
sys.path.append('../FE')

from DataflowGraph import Vertex, Edge
from ProgramJsonManager import ProgramJsonManager
from AXIConnectionParser import AXIConnectionParser
import logging
import re
import math
import json

class DataflowGraphTapa ():

  def __init__(self, program_json_manager : ProgramJsonManager, axi_parser : AXIConnectionParser):
    self.program_json_manager = program_json_manager
    self.axi_parser = axi_parser

    self.vertices = {} # name -> Vertex
    self.edges = {} # name -> Edge

    self.__initEdges()

    self.__initVertices()
    self.__initAXIVertices()

    self.__linkEdgeAndVertex()
    
  def __initEdges(self):
    fifo_section = self.program_json_manager.getFIFOSection()

    # init Edge objects
    for e_name, info in fifo_section.items():
      e = Edge(e_name)
      e.depth = info['depth']
      e.width = info['width']
      e.addr_width = int(math.log2(e.depth)+1)
      self.edges[e_name] = e

  def __initVertices(self):
    v_name_to_module = self.program_json_manager.getVNameToModule()

    for v_name, v_module in v_name_to_module.items():
      v = Vertex(v_module, v_name)

      # get area
      v.area = self.program_json_manager.getAreaOfModule(v_module)
      
      fifo_section = self.program_json_manager.getFIFOSection()
      for e_name, info in fifo_section.items():
        if info['produced_by_module_name'] == v_name:
          v.out_edge_names.append(e_name)
        if info['consumed_by_module_name'] == v_name:
          v.in_edge_names.append(e_name)
          
      self.vertices[v_name] = v

  def __initAXIVertices(self):
    axi_modules = self.axi_parser.getAllAXIModules()

    for v_module, v_name in axi_modules:
      v = Vertex(v_module, v_name)
      v.area = self.program_json_manager.getAreaOfModule(v_module)
      self.vertices[v_name] = v

  def __linkEdgeAndVertex(self):
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