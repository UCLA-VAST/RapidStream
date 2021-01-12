#! /usr/bin/python3.6
import logging
import json

class CreateResultJson:
  def __init__(self, floorplan, wrapper_creater, path_planner):
    self.floorplan = floorplan
    self.s2v = floorplan.getSlotToVertices()
    self.s2e = floorplan.getSlotToEdges()
    self.wrapper_creater = wrapper_creater
    self.path_planner = path_planner

  def createResultJson(self, file = 'FE_result.json'):
    result = {}
    result['FloorplanVertex'] = self.floorplan.getSlotNameToVertexNames()
    result['FloorplanEdge'] = self.floorplan.getSlotNameToEdgeNames()
    result['SlotIO'] = self.wrapper_creater.getSlotToIO()
    
    slot_to_rtl = {}
    for slot in self.s2v.keys():
      slot_to_rtl[slot.getRTLModuleName()] = self.wrapper_creater.createSlotWrapper(slot)
    result['SlotWrapperRTL'] = slot_to_rtl

    result['PathPlanningFIFO'] = self.path_planner.naivePathPlanningFIFO()
    result['PathPlanningWire'] = self.path_planner.naivePathPlanningWire()

    f = open(file, 'w')
    f.write(json.dumps(result, indent=2))