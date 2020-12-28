#! /usr/bin/python3.6
import logging
from Slot import Slot
import re

class CreateSlotWrapper:
  def __init__(self, graph, top_rtl_parser, floorplan):
    self.graph = graph
    self.top_rtl_parser = top_rtl_parser
    self.floorplan = floorplan

    self.s2v = floorplan.getSlotToVertices()
    self.s2e = floorplan.getSlotToEdges()

    for s in self.s2e.keys():
      wrapper = self.createSlotWrapper(s)
      f = open(s.getRTLModuleName()+'.v', 'w')
      f.write('\n'.join(wrapper))

  def getWireDecl(self, slot : Slot) -> str:
    return self.top_rtl_parser.getAllDeclExceptIO()

  def getVertexInstances(self, slot : Slot):
    v_list = self.s2v[slot]
    return [self.top_rtl_parser.getRTLOfInst(v.name) for v in v_list]

  def getEdgeInstances(self, slot : Slot):
    e_list = self.s2e[slot]
    return [self.top_rtl_parser.getRTLOfInst(e.name) for e in e_list]

  def getHeader(self, slot : Slot):
    io_decl = self.getIODecl(slot)
    io_decl_with_comma = [io.replace(';', ',') for io in io_decl]
    io_header = [re.sub(r'input[ ]*|output[ ]*', '', io) for io in io_decl_with_comma]
    io_header = [re.sub(r'[ ]*\[.*\][ ]*', '', io) for io in io_header]
    io_header[-1].replace(';', '') # the last io does not have comma

    # add indentation
    io_header = ['  '+io for io in io_header]

    beg = ['`timescale 1 ns / 1 ps', f'module {slot.getRTLModuleName()} (']
    io_header = beg + io_header
    io_header.append(')')

    return io_header

  def getEnding(self):
    return ['endmodule']

  # 1. inter-slot edges
  # 2. top-level IOs
  def getIODecl(self, slot : Slot):
    IO_section = []

    # inbound wires of inter-slot edges become IOs
    intra_edges, inter_edges = self.floorplan.getIntraAndInterEdges(self.s2v[slot])
          
    for e in inter_edges:
      for wire in self.top_rtl_parser.getWiresOfFIFOName(e.name):
        if '_din' in wire or '_write' in wire:
          IO_section.append(f'input {self.top_rtl_parser.getWidthOfRegOrWire(wire)} {wire};')
        elif '_full_n' in wire:
          IO_section.append(f'output {self.top_rtl_parser.getWidthOfRegOrWire(wire)} {wire};')

    # if any vertex is an AXI module, it will contain top-level IO
    for v in self.s2v[slot]:
      if '_axi' in v.name:
        for wire in self.top_rtl_parser.getWiresOfVertexName(v.name):
          if self.top_rtl_parser.isIO(wire):
            IO_section.append(f'{self.top_rtl_parser.getDirOfIO(wire)} {self.top_rtl_parser.getWidthOfIO(wire)} {wire};')

    if any('s_axi' in v.name for v in self.s2v[slot]):
      IO_section.append('output ap_start;')
      IO_section.append('input  ap_done;')
      IO_section.append('input  ap_idle;')
      IO_section.append('input  ap_ready;')
    else:
      IO_section.append('input  ap_start;')
      IO_section.append('output ap_done;')
      IO_section.append('output ap_idle;')
      IO_section.append('output ap_ready;')      
      IO_section.append('input  ap_continue;')

    IO_section.append('input ap_clk;')
    IO_section.append('input ap_rst;')
    # simultaneous set rst and rst_n in case different modules have different choices
    # the last IO decl does not have ',' at the end
    IO_section.append('input ap_rst_n;') 

    return IO_section

  # TODO fix ap signals
  def createSlotWrapper(self, slot : Slot):
    def addIndent(sec):
      return ['  ' + line for line in sec]

    def filterUnusedDecl(decl, v_insts, e_insts):
      insts = v_insts + e_insts
      decl_filter = []
      ap_signals = ['ap_start', 'ap_done', 'ap_ready', 'ap_idle']
      for d in decl:
        if any(re.search(f' {signal}', d) for signal in ap_signals):
          continue
        
        name = re.search(r' ([^ ]*);', d).group(1)
        # if name == 'L':
        #   import pdb; pdb.set_trace()
        if any([name in line for line in insts]):
          decl_filter.append(d)
      
      return decl_filter

    header = self.getHeader(slot)
    decl = addIndent(self.getWireDecl(slot))
    io_decl = addIndent(self.getIODecl(slot))
    v_insts = addIndent(self.getVertexInstances(slot))
    e_insts = addIndent(self.getEdgeInstances(slot))
    ending = self.getEnding()

    decl = filterUnusedDecl(decl, v_insts, e_insts)

    return header + decl + io_decl + v_insts + e_insts + ending