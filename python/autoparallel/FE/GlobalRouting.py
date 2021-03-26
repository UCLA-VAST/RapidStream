#! /usr/bin/python3.6
import logging
import json
from collections import defaultdict 
from autobridge.Opt.DataflowGraph import Vertex, Edge

class GlobalRouting:
  def __init__(self, floorplan, top_rtl_parser, slot_manager):
    self.floorplan = floorplan
    self.top_rtl_parser = top_rtl_parser
    self.slot_manager = slot_manager
    self.v2s = floorplan.getVertexToSlot()
    self.s2v = floorplan.getSlotToVertices()
    self.s2e = floorplan.getSlotToEdges()
    self.e_name2lat = {}
    self.e_name2path = {} # from edge to all slots passed, exclude src and dst
    self.slot2e_names = {} # from slot to all edges passed through
    self.slot_to_dir_to_edges = defaultdict(lambda: defaultdict(list))

    self.naiveGlobalRouting()

  def naiveGlobalRouting(self):
    """
    each edge first go in the Y direction then in the X direction
    assume all slots are of the same size and are aligned
    the slot_path exclude the src slot and the dst slot
    """
    def __initEdgeLatency():
      for e_list in self.s2e.values():
        for e in e_list:
          self.e_name2lat[e.name] = self.__getPipelineLevelOfEdge(e)

    for e_list in self.s2e.values():
      for e in e_list:
        slot_path = []
        src_slot = self.v2s[e.src]
        dst_slot = self.v2s[e.dst]
        slot_path.append(src_slot)

        curr = src_slot
        len_x = src_slot.getLenX()
        len_y = src_slot.getLenY()

        # first go in X direction
        x_diff = curr.getPositionX() - dst_slot.getPositionX()
        if x_diff:
          dir = 'LEFT' if x_diff > 0 else 'RIGHT'
          for i in range(int(abs(x_diff/len_x))):
            curr = self.slot_manager.createSlotForRouting(curr.getNeighborSlotName(dir))
            slot_path.append(curr)

        y_diff = curr.getPositionY() - dst_slot.getPositionY()
        if y_diff:
          dir = 'DOWN' if y_diff > 0 else 'UP'
          for i in range(int(abs(y_diff/len_y))):
            curr = self.slot_manager.createSlotForRouting(curr.getNeighborSlotName(dir))
            slot_path.append(curr)
        
        assert curr == dst_slot
        
        slot_path = slot_path[1:-1] # exclude the src and the dst
        logging.info(f'{e.name}: {self.v2s[e.src].getName()} -> {self.v2s[e.dst].getName()} : ' + ' '.join(s.getName() for s in slot_path))
        self.e_name2path[e.name] = slot_path

    for e_name, slots in self.e_name2path.items():
      for s in slots:
        if s not in self.slot2e_names:
          self.slot2e_names[s] = []
        self.slot2e_names[s].append(e_name)

    for slot, e_names in self.slot2e_names.items():
        logging.info(f'{slot.getName()} will be passed by: \n\t' + '\n\t'.join(e_names))

    __initEdgeLatency()

  def getDirectionOfPassingEdges(self):
    """
    In which directions (UP, DOWN, LEFT, RIGHT) do the edges come and go
    slot -> dir & in or out -> edges
    """
    for e_list in self.s2e.values():
      for e in e_list:
        src_slot = self.v2s[e.src]
        dst_slot = self.v2s[e.dst]
        
        # ignore intra slot edges
        if src_slot == dst_slot:
          continue

        logging.debug(f'from {src_slot.getRTLModuleName()} to {dst_slot.getRTLModuleName()}')
        slot_path = self.e_name2path[e.name]

        prev = src_slot
        for slot in slot_path + [dst_slot]:
          curr_name = slot.getRTLModuleName()
          prev_name = prev.getRTLModuleName()
          if slot.isAbove(prev):
            logging.debug('Go up')
            self.slot_to_dir_to_edges[curr_name]['DOWN_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev_name]['UP_OUT'].append(e.name)
          elif slot.isBelow(prev):
            logging.debug('Go down')
            self.slot_to_dir_to_edges[curr_name]['UP_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev_name]['DOWN_OUT'].append(e.name)
          elif slot.isToTheLeftOf(prev):
            logging.debug('Go left')
            self.slot_to_dir_to_edges[curr_name]['RIGHT_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev_name]['LEFT_OUT'].append(e.name)
          elif slot.isToTheRightOf(prev):
            logging.debug('Go right')
            self.slot_to_dir_to_edges[curr_name]['LEFT_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev_name]['RIGHT_OUT'].append(e.name)
          else:
            assert False

          prev = slot

    # remove the defualt dict property to prevent unexpected contamination
    self.slot_to_dir_to_edges = json.loads(json.dumps(self.slot_to_dir_to_edges))

    return self.slot_to_dir_to_edges

  def getDirectionOfPassingEdgeWires(self):
    """
    get the map: slot -> each direction -> all wires of all the edges that leave through this direction
    Note that the routing inclusive wrapper will rename the wires.
    Thus the routing wrapper creater should take care of the renaming
    """
    slot_to_dir_to_wires = {}
    for slot, dir_to_fifos in self.slot_to_dir_to_edges.items():
      dir_to_wires = {}
      for dir, fifos in dir_to_fifos.items():
        dir_to_wires[dir] = []
        for e_name in fifos:
          # the interface wires are the inbound wires for both sides 
          dir_to_wires[dir].extend(self.top_rtl_parser.getInboundSideWiresOfFIFOName(e_name))

      slot_to_dir_to_wires[slot] = dir_to_wires
    return slot_to_dir_to_wires

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

  def getPipelineLevelOfEdge(self, e : Edge) -> int:
    return self.e_name2lat[e.name]
  
  def getPipelineLevelOfEdgeName(self, e_name : str) -> int:
    return self.e_name2lat[e_name]

  def getLatencyOfEdge(self, e: Edge) -> int:
    """consider the latency of the FIFO itself"""
    return self.getPipelineLevelOfEdge(e) + 1

  def getPassingEdgeNamesOfSlot(self, slot):
    if slot in self.slot2e_names:
      return self.slot2e_names[slot]
    else:
      return []

  def getIndexOfSlotInPath(self, e_name, slot):
    assert slot in self.e_name2path[e_name]
    return self.e_name2path[e_name].index(slot)

  def getPathLength(self, e_name):
    return len(self.e_name2path[e_name])

  def getPureRoutingSlots(self):
    return self.slot_manager.getPureRoutingSlots()

  def isPureRoutingSlot(self, slot):
    return self.slot_manager.isPureRoutingSlot(slot)

if __name__ == '__main__':
  json_path = './BE_pass1_anchored.json'
  json_hub = json.loads(open(json_path, 'r').read())


