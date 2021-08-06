#! /usr/bin/python3.6
import logging
from collections import defaultdict 

from autobridge.Opt.DataflowGraph import Vertex, Edge
from autoparallel.FE.ILPGlobalRouting import ILPRouter


class GlobalRouting:
  def __init__(self, floorplan, top_rtl_parser, slot_manager, pipeline_style, anchor_plan: int):
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
    
    self.in_slot_pipeline_style = pipeline_style
    logging.info(f'Pipeline style: {pipeline_style}')
    self.anchor_plan = anchor_plan

    logging.critical('current latency counting depends on 4-CR slot size')
    self.ILPRouting()
    self.__initDirectionOfPassingEdges()

  def ILPRouting(self):
    all_edges = sum(self.s2e.values(), [])
    ilp_router = ILPRouter(all_edges, self.v2s, self.floorplan.getUtilization())
    self.e_name2path = ilp_router.ILPRouting()

    # register the passed slots as routing slots
    for path in self.e_name2path.values():
      for slot in path:
        self.slot_manager.createSlotForRouting(slot.getName())

    self.postProcessRoutingResults()
    
  def postProcessRoutingResults(self):

    for e_name, slots in self.e_name2path.items():
      for s in slots:
        if s not in self.slot2e_names:
          self.slot2e_names[s] = []
        self.slot2e_names[s].append(e_name)

    for slot, e_names in self.slot2e_names.items():
        logging.info(f'{slot.getName()} will be passed by: \n\t' + '\n\t'.join(e_names))

    for e_list in self.s2e.values():
      for e in e_list:
        # assume each slot is 2x2. The path excludes the src and dst slot
        dist = ( len(self.e_name2path[e.name]) + 1 ) * 2 
        self.e_name2lat[e.name] = self.__getPipelineLevelOfEdge(dist)

  def naiveGlobalRouting(self):
    """
    each edge first go in the Y direction then in the X direction
    assume all slots are of the same size and are aligned
    the slot_path exclude the src slot and the dst slot
    """
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

    self.postProcessRoutingResults()


  def __initDirectionOfPassingEdges(self):
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
          if slot.isAbove(prev):
            logging.debug('Go up')
            self.slot_to_dir_to_edges[slot]['DOWN_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev]['UP_OUT'].append(e.name)
          elif slot.isBelow(prev):
            logging.debug('Go down')
            self.slot_to_dir_to_edges[slot]['UP_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev]['DOWN_OUT'].append(e.name)
          elif slot.isToTheLeftOf(prev):
            logging.debug('Go left')
            self.slot_to_dir_to_edges[slot]['RIGHT_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev]['LEFT_OUT'].append(e.name)
          elif slot.isToTheRightOf(prev):
            logging.debug('Go right')
            self.slot_to_dir_to_edges[slot]['LEFT_IN'].append(e.name)
            self.slot_to_dir_to_edges[prev]['RIGHT_OUT'].append(e.name)
          else:
            assert False

          prev = slot

    # remove the defualt dict property to prevent unexpected contamination
    # self.slot_to_dir_to_edges = json.loads(json.dumps(self.slot_to_dir_to_edges))

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

  def __getPipelineLevelOfEdge(self, dist: int) -> int:
    # add a register every 2 clock regions
    # note that the pipeline level excludes the inherent 1 cycle of latency of the FIFO 
    # the pipeline registers are put into each intermediate slots
    # [ src ] *[reg]* -> [ reg ] -> [ reg ] -> [ dst ]. dist = 3, lat = dist-1 => 2
    # however, immediate neighbors will have one pipeline in between. So skip the -1 here
    # ---------------------------------------------------
    # UPDATE: note that we always add pipelining near the source of the edge.
    # thus the pipeline level is equal to the distance

    if self.in_slot_pipeline_style == 'INVERT_CLOCK':
      assert self.anchor_plan == 3
      pipeline_level = dist
      
    else:
      if self.in_slot_pipeline_style == 'REG':
        pipeline_level = int(dist / 2)
      elif self.in_slot_pipeline_style == 'LUT':
        pipeline_level = int(dist / 2)
      elif self.in_slot_pipeline_style == 'WIRE':
        pipeline_level = int(dist / 2)
      elif self.in_slot_pipeline_style == 'DOUBLE_REG':
        pipeline_level = dist
        
      # anchor_plan will take effect when connecting to the inner slot
      # for a long connection, anchor_plan of 3 will add one additonal register between the source inner-most wrapper 
      # and the first anchor register; and add another register between the last anchor register and the 
      # destination inner-most wrapper
      pipeline_level += (self.anchor_plan - 1)
    
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
