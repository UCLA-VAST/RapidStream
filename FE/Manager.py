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

    self.hls_prj_manager = HLSProjectManager(self.top_rtl_name, self.hls_prj_path, self.hls_solution_name)
    self.top_rtl_parser = TopRTLParser(self.hls_prj_manager.getTopRTLPath())
    self.graph = DataflowGraph(self.hls_prj_manager, self.top_rtl_parser)

    user_constraint_s2v = self.parseUserConstraints()

    fp = Floorplanner(self.graph, user_constraint_s2v, total_usage=self.hls_prj_manager.getTotalArea(), board=self.device_manager.getBoard())
    fp.coarseGrainedFloorplan()
    fp.printFloorplan()

    wrapper_creater = CreateSlotWrapper(self.graph, self.top_rtl_parser, fp)
    wrapper_creater.createSlotWrapperForAll()

    json_creater = CreateResultJson(fp, wrapper_creater)
    json_creater.createResultJson()

  def __setupLogging(self):
    logging.basicConfig(filename='auto-parallel.log', filemode='w', level=logging.DEBUG, format="[%(levelname)s: %(funcName)25s() ] %(message)s")

  def parseUserConstraints(self):
    user_constraint_s2v = defaultdict(list)
    user_fp_json = self.config["Floorplan"]
    for region, v_name_group in user_fp_json.items():
      slot = Slot(self.board, region)
      for v_name in v_name_group:
        user_constraint_s2v[slot].append(self.graph.getVertex(v_name))

    return user_constraint_s2v


if __name__ == "__main__":
  m = Manager('SampleUserConfig.json')
    


