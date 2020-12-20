#! /usr/bin/python3.6

from collections import defaultdict
from HLSProjectManager import HLSProjectManager
from DeviceManager import DeviceManager
from DataflowGraph import DataflowGraph
from TopRTLParser import TopRTLParser
from Floorplan import Floorplanner
from Slot import Slot

import logging

class Manager:

  def __init__(
      self,
      hls_prj_path,
      top_rtl_name,
      user_constraint_v2s = {},
      ddr_enable_bitmap=[0, 0, 0, 0],
      board_name='U250',
      hls_solution_name='solution',
      max_search_time = 600,
      enable_loop_level_balance = False):
    self.hls_prj_path = hls_prj_path
    self.top_rtl_name = top_rtl_name
    self.user_constraint_v2s = user_constraint_v2s
    self.ddr_enable_bitmap = ddr_enable_bitmap
    self.max_search_time = max_search_time
    self.enable_loop_level_balance = enable_loop_level_balance     # only utilize the dataflow-process-level topology. Do not analyze the internal FSM
    logging.basicConfig(filename='ap.log', filemode='w', level=logging.INFO, format="[%(funcName)25s() ] %(message)s")

    self.device_manager = DeviceManager(board_name)
    self.hls_prj_manager = HLSProjectManager(self.top_rtl_name, self.hls_prj_path, hls_solution_name)
    self.top_rtl_parser = TopRTLParser(self.hls_prj_manager.getTopRTLPath())

    graph = DataflowGraph(self.hls_prj_manager, self.top_rtl_parser)
    graph.printVertices()

    self.fp = Floorplanner(graph, self.user_constraint_v2s, self.device_manager.getBoard())
    self.fp.coarseGrainedFloorplan()

if __name__ == "__main__":
  m = Manager(
    hls_prj_path='/home/einsx7/pr/application/lu_dcompose/16x16/orig_u250/kernel0',
    top_rtl_name='kernel0')
    


