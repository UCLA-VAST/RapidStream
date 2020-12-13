#! /usr/bin/python3.6

from collections import defaultdict
from HLSProjectManager import HLSProjectManager
from DeviceManager import DeviceManager
import logging

class Manager:

  def __init__(
      self,
      hls_prj_path,
      top_rtl_name,
      user_floorplan,
      ddr_enable_bitmap,
      board_name,
      hls_solution_name='solution',
      max_search_time = 600,
      mod_level_rebalance = True):
    self.hls_prj_path = hls_prj_path
    self.top_rtl_name = top_rtl_name
    self.user_floorplan = user_floorplan
    self.ddr_enable_bitmap = ddr_enable_bitmap
    self.max_search_time = max_search_time
    self.mod_level_rebalance = mod_level_rebalance     # only utilize the dataflow-process-level topology. Do not analyze the internal FSM

    self.device_manager = DeviceManager(board_name)
    self.hls_prj_manager = HLSProjectManager(self.top_rtl_name, self.hls_prj_path, hls_solution_name)

    logging.basicConfig(level=logging.INFO, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
     

    


