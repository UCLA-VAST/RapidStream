#! /usr/bin/python3.6
from collections import defaultdict
from autoparallel.FE.tapa.DataflowGraphTapa import DataflowGraphTapa
from autoparallel.FE.tapa.ProgramJsonManager import ProgramJsonManager
from autoparallel.FE.DeviceManager import DeviceManager
from autoparallel.FE.Floorplan import Floorplanner
from autoparallel.FE.Slot import Topology
from autoparallel.FE.AXIConnectionParser import AXIConnectionParser
from autoparallel.FE.SlotManager import SlotManager

import logging
import json
import re
import os

class TapaManager:
  def __init__(self, config):
    self.__setupLogging(logging.DEBUG)
    self.config = config
    assert self.config['CompiledBy'] == 'TAPA'

    self.board = DeviceManager(config['Board']).getBoard()

    self.program_json_manager = ProgramJsonManager(
      config['ProjectPath'],
      config['Edges'],
      config['Vertices'],
    )
    self.graph = DataflowGraphTapa(self.program_json_manager)

    slot_manager = SlotManager(self.board)
    user_constraint_s2v = self.parseUserConstraints(slot_manager)
    
    self.fp = Floorplanner(self.graph, user_constraint_s2v, slot_manager=slot_manager, total_usage=self.program_json_manager.getVertexTotalArea(), board=self.board)
    self.fp.coarseGrainedFloorplan()

  def generateTAPAConstraints(self):
    s2v = self.fp.getSlotToVertices()
    topology = Topology(s2v)
    output = {
        slot.pblock_name:
        [v.name for v in v_group] + [topology.getTopologyOf(slot)]
        for slot, v_group in s2v.items()
    }
    return output

  def parseUserConstraints(self, slot_manager):
    user_constraint_s2v = defaultdict(list)
    # for optional module constraints
    module_fp = self.config['OptionalFloorplan']
    for region, module_group in module_fp.items():
      slot = slot_manager.getSlot(region)
      for mod_name in module_group:
        user_constraint_s2v[slot].append(self.graph.getVertex(mod_name))

    return user_constraint_s2v

  def __setupLogging(self, level):
    logging.basicConfig(filename='auto-parallel.log', filemode='w', level=level, format="[%(levelname)s: %(funcName)25s() ] %(message)s")

if __name__ == "__main__":
  with open('SampleUserConfig.json', 'r') as fp:
    constraints = TapaManager(json.load(fp)).generateTAPAConstraints()
  with open('tapa_constraint.json', 'w') as fp:
    json.dump(constraints, fp, indent=2)
