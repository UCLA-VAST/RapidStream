#! /usr/bin/python3.6

from collections import defaultdict
from HLSProjectManager import HLSProjectManager
from DeviceManager import DeviceManager
from DataflowGraph import DataflowGraph
from TopRTLParser import TopRTLParser
from Floorplan import Floorplanner
from Slot import Slot
from CreateSlotWrapper import CreateSlotWrapper
from CreateResultJson import CreateResultJson
from GlobalRouting import GlobalRouting

import logging
import json
import re
import os

class Manager:

  def __init__(
      self,
      config_file_path):
    assert os.path.isfile(config_file_path)
    self.config = json.loads(open(config_file_path, 'r').read())

    self.__setupLogging()

    self.device_manager = DeviceManager(self.config["Board"])
    self.board = self.device_manager.getBoard()

    self.top_rtl_name = self.config["TopName"]
    self.hls_prj_path = self.config["HLSProjectPath"]
    self.hls_solution_name = self.config["HLSSolutionName"]

    hls_prj_manager = HLSProjectManager(self.top_rtl_name, self.hls_prj_path, self.hls_solution_name)
    top_rtl_parser = TopRTLParser(hls_prj_manager.getTopRTLPath())
    graph = DataflowGraph(hls_prj_manager, top_rtl_parser)

    user_constraint_s2v = self.parseUserConstraints(graph)

    floorplan = Floorplanner(graph, user_constraint_s2v, total_usage=hls_prj_manager.getTotalArea(), board=self.device_manager.getBoard())
    floorplan.coarseGrainedFloorplan()
    floorplan.printFloorplan()

    wrapper_creater = CreateSlotWrapper(graph, top_rtl_parser, floorplan)
    wrapper_creater.createSlotWrapperForAll()

    path_planner = GlobalRouting(floorplan, top_rtl_parser)

    json_creater = CreateResultJson(floorplan, wrapper_creater, path_planner)
    json_creater.createResultJson()

  def __setupLogging(self):
    logging.basicConfig(filename='auto-parallel.log', filemode='w', level=logging.DEBUG, format="[%(levelname)s: %(funcName)25s() ] %(message)s")

  def parseUserConstraints(self, graph):
    user_constraint_s2v = defaultdict(list)
    user_fp_json = self.config["Floorplan"]
    for region, v_name_group in user_fp_json.items():
      slot = Slot(self.board, region)
      for v_name in v_name_group:
        user_constraint_s2v[slot].append(graph.getVertex(v_name))

    return user_constraint_s2v


if __name__ == "__main__":
  m = Manager('SampleUserConfig.json')
    


