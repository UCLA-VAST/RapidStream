#! /usr/bin/python3.6
import logging
import json
from collections import defaultdict 
from autoparallel.FE.DataflowGraph import Vertex, Edge

class GlobalRouting:
  def __init__(self, floorplan, top_rtl_parser):
    self.floorplan = floorplan
    self.top_rtl_parser = top_rtl_parser
    self.v2s = floorplan.getVertexToSlot()
    self.s2v = floorplan.getSlotToVertices()
    self.s2e = floorplan.getSlotToEdges()
    self.e_name2lat = {}

    self.__initEdgeLatency()

  def naivePathPlanningFIFO(self):
    """
    for each slot and for each direction, get all edges that leave through that direction
    """
    slot_to_dir = {}
    for this_slot, v_list in self.s2v.items():
      intra_edges, inter_edges = self.floorplan.getIntraAndInterEdges(v_list)
      dir_to_edge = defaultdict(list)

      for e in inter_edges:
        if self.v2s[e.src] == this_slot:
          that_slot = self.v2s[e.dst]
          e_dir = '_OUT'
        elif self.v2s[e.dst] == this_slot:
          that_slot = self.v2s[e.src]
          e_dir = '_IN'
        else:
          assert False
        assert that_slot != this_slot

        # first quadrant
        if that_slot.getPositionY() > this_slot.getPositionY() and that_slot.getPositionX() > this_slot.getPositionX():
          crossing_loc = 'RIGHT'
        # Y axis positive
        elif that_slot.getPositionY() > this_slot.getPositionY() and that_slot.getPositionX() == this_slot.getPositionX():
          crossing_loc = 'UP'
        # second quadrant
        elif that_slot.getPositionY() > this_slot.getPositionY() and that_slot.getPositionX() < this_slot.getPositionX():
          crossing_loc = 'LEFT'
        # X axis negtive
        elif that_slot.getPositionY() == this_slot.getPositionY() and that_slot.getPositionX() < this_slot.getPositionX():
          crossing_loc = 'LEFT'
        # third quadrant
        elif that_slot.getPositionY() < this_slot.getPositionY() and that_slot.getPositionX() < this_slot.getPositionX():
          crossing_loc = 'LEFT'
        # Y axis negtive
        elif that_slot.getPositionY() < this_slot.getPositionY() and that_slot.getPositionX() == this_slot.getPositionX():
          crossing_loc = 'DOWN'
        # fourth quadrant
        elif that_slot.getPositionY() < this_slot.getPositionY() and that_slot.getPositionX() > this_slot.getPositionX():
          crossing_loc = 'RIGHT'
        # X axis positive
        elif that_slot.getPositionY() == this_slot.getPositionY() and that_slot.getPositionX() > this_slot.getPositionX():
          crossing_loc = 'RIGHT'
        else:
          assert False

        dir_to_edge[crossing_loc + e_dir].append(e.name)
        # --- end of inner loop ---

      slot_to_dir[this_slot.getRTLModuleName()] = dir_to_edge
      # --- end of outer loop ---

    return slot_to_dir

  def getPathPlanningWire(self, slot_to_dir):
    """
    get the map: slot -> each direction -> all wires of all the edges that leave through this direction
    """
    slot_to_dir_to_wires = {}
    for slot, dir_to_fifos in slot_to_dir.items():
      dir_to_wires = {}
      for dir, fifos in dir_to_fifos.items():
        dir_to_wires[dir] = []
        for e_name in fifos:
          # the interface wires are the inbound wires for both sides 
          dir_to_wires[dir].extend(self.top_rtl_parser.getInboundSideWiresOfFIFOName(e_name))

      slot_to_dir_to_wires[slot] = dir_to_wires
    return slot_to_dir_to_wires

  def naivePathPlanningWire(self):
    return self.getPathPlanningWire(self.naivePathPlanningFIFO())

  def __getPipelineLevelOfEdge(self, e : Edge) -> int:
    src_slot = self.v2s[e.src]
    dst_slot = self.v2s[e.dst]

    src_x = src_slot.getPositionX()
    src_y = src_slot.getPositionY()
    dst_x = dst_slot.getPositionX()
    dst_y = dst_slot.getPositionY()
    dist = abs(src_x - dst_x) + abs(src_y - dst_y)

    # add a register every 2 clock regions
    # note that the pipeline level excludes the inherent 1 cycle of latency of the FIFO 
    pipeline_level = int(dist / 2) 
    logging.info(f'edge {e.name}: ({src_x}, {src_y}) -> ({dst_x}, {dst_y}); pipeline level : {pipeline_level}')
    
    return pipeline_level

  def __initEdgeLatency(self):
    for e_list in self.s2e.values():
      for e in e_list:
        self.e_name2lat[e.name] = self.__getPipelineLevelOfEdge(e)

  def getPipelineLevelOfEdge(self, e : Edge) -> int:
    return self.e_name2lat[e.name]
  
  def getPipelineLevelOfEdgeName(self, e_name : str) -> int:
    return self.e_name2lat[e_name]

  def getLatencyOfEdge(self, e: Edge) -> int:
    """consider the latency of the FIFO itself"""
    return self.getPipelineLevelOfEdge(e) + 1

if __name__ == '__main__':
  json_path = './BE_pass1_anchored.json'
  json_hub = json.loads(open(json_path, 'r').read())


