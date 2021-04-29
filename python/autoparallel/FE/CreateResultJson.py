#! /usr/bin/python3.6
import logging
import json
from collections import defaultdict

class CreateResultJson:
  def __init__(
      self, 
      floorplan, 
      wrapper_creater, 
      global_router, 
      board, 
      hls_prj_manager, 
      slot_manager, 
      top_rtl_parser, 
      new_top_rtl):
    self.floorplan = floorplan
    self.wrapper_creater = wrapper_creater
    self.global_router = global_router
    self.board = board
    self.hls_prj_manager = hls_prj_manager
    self.slot_manager = slot_manager
    self.top_rtl_parser = top_rtl_parser
    self.new_top_rtl = new_top_rtl

  def __getNeighborSection(self):
    neighbors = defaultdict(dict)
    for slot in self.slot_manager.getActiveSlotsIncludeRouting():
      for dir in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        neighbor_slots = self.slot_manager.getNeighborSlotsIncludeRouting(slot, dir)
        neighbors[slot.getRTLModuleName()][dir] = [s.getRTLModuleName() for s in neighbor_slots]
    return neighbors

  def __getOppositeDirection(self, dir):
    if dir == 'UP':
      return 'DOWN'
    elif dir == 'DOWN':
      return 'UP'
    elif dir == 'LEFT':
      return 'RIGHT'
    elif dir == 'RIGHT':
      return 'LEFT'
    else:
      assert False, f'inccorect direction {dir}'

  def __getSharedAnchorSection(self, neighbors, path_planning_wire):
    """ 
    [obsolete] collect the shared anchors with immediate neighbors in each direction
    If we do not include passing edges to the wrapper, not all IOs are to immediate neighbors
    Right now each slot will only connect with direct neighbors
    """
    shared_anchors = defaultdict(dict)
    for slot_name in neighbors.keys():
      for dir in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        neighbor_slots = neighbors[slot_name][dir]
        reverse_dir = self.__getOppositeDirection(dir)
        
        if f'{dir}_OUT' in path_planning_wire[slot_name]:
          wires_out_from_this_slot = path_planning_wire[slot_name][f'{dir}_OUT']
          wires_into_neighbor_slot = []
          for neighbor_slot in neighbor_slots:
            if f'{reverse_dir}_IN' in path_planning_wire[neighbor_slot]:
              wires_into_neighbor_slot.extend( \
                path_planning_wire[neighbor_slot][f'{reverse_dir}_IN'])

          shared_anchors_outbound = [anchor for anchor in wires_out_from_this_slot if anchor in wires_into_neighbor_slot]        
          shared_anchors[slot_name][f'{dir}_OUT'] = \
            {anchor : self.top_rtl_parser.getIntegerWidthOfRegOrWire(anchor) for anchor in shared_anchors_outbound}

        if f'{dir}_IN' in path_planning_wire[slot_name]:
          wires_into_this_slot = path_planning_wire[slot_name][f'{dir}_IN']
          wires_out_from_neighbor_slot = []
          for neighbor_slot in neighbor_slots:
            if f'{reverse_dir}_OUT' in path_planning_wire[neighbor_slot]:
              wires_out_from_neighbor_slot.extend( \
                path_planning_wire[neighbor_slot][f'{reverse_dir}_OUT'])
        
          shared_anchors_inbound = [anchor for anchor in wires_into_this_slot if anchor in wires_out_from_neighbor_slot]
          shared_anchors[slot_name][f'{dir}_IN'] = \
            {anchor : self.top_rtl_parser.getIntegerWidthOfRegOrWire(anchor) for anchor in shared_anchors_inbound}
    
    return shared_anchors

  def __getSlotWrapperRTLSection(self):
    slot_to_rtl = {}
    for slot in self.slot_manager.getActiveSlotsIncludeRouting():
      slot_to_rtl[slot.getRTLModuleName()] = self.wrapper_creater.getCtrlInclusiveWrapper(slot)
    return slot_to_rtl

  def createResultJson(self, file = 'front_end_result.json'):
    result = {}
    result['CR_NUM_Y'] = self.board.CR_NUM_VERTICAL
    result['CR_NUM_X'] = self.board.CR_NUM_HORIZONTAL
    result['FPGA_PART_NAME'] = self.board.FPGA_PART_NAME
    result['ORIG_RTL_PATH'] = self.hls_prj_manager.getRTLDir()

    result['FloorplanVertex'] = self.floorplan.getSlotNameToVertexNames()
    # result['FloorplanEdge'] = self.floorplan.getSlotNameToEdgeNames()
    
    result['SlotIO'] = self.wrapper_creater.getSlotNameToIOList()
    result['SlotWrapperRTL'] = self.__getSlotWrapperRTLSection()
    result['TopIO'] = self.top_rtl_parser.getDirWidthNameOfAllIO()
    
    result['NewTopRTL'] = self.new_top_rtl
    
    result['PathPlanningWire'] = self.wrapper_creater.getSlotNameToDirToWires()
    
    # result['Utilization'] = self.floorplan.getUtilization()
    # result['Neighbors'] = self.__getNeighborSection()

    result['ComputeSlots'] = [ s.getRTLModuleName() for s in self.slot_manager.getComputeSlots() ]
    result['PureRoutingSlots'] = [ s.getRTLModuleName() for s in self.slot_manager.getPureRoutingSlots() ]
    result['AllSlotPairs'] = [[p[0].getRTLModuleName(), p[1].getRTLModuleName()] for p in self.slot_manager.getAllSlotPairs()]

    result['InSlotPipelineStyle'] = self.wrapper_creater.in_slot_pipeline_style

    f = open(file, 'w')
    f.write(json.dumps(result, indent=2))