#! /usr/bin/python3.6
import sys
from collections import defaultdict
from autobridge.HLSParser.vivado_hls.HLSProjectManager import HLSProjectManager
from autobridge.Device.DeviceManager import DeviceManager
from autobridge.Opt.DataflowGraph import DataflowGraph
from autobridge.HLSParser.vivado_hls.TopRTLParser import TopRTLParser
from autobridge.Opt.Floorplan import Floorplanner
from autobridge.Opt.SlotManager import SlotManager
from autobridge.Opt.LatencyBalancing import LatencyBalancing

from autoparallel.FE.GlobalRouting import GlobalRouting
from autoparallel.FE.CreateSlotWrapper import CreateSlotWrapper
from autoparallel.FE.CreateRoutingSlotWrapper import CreateRoutingSlotWrapper
from autoparallel.FE.CreateResultJson import CreateResultJson
from autoparallel.FE.CreateTopRTL import CreateTopRTL
from autoparallel.FE.PatternOpt import getPatternBasedGrouping
from autoparallel.FE.UnifyVertexType import unifyModuleTypesInTopRTL

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
    self.basicSetup()
    self.loggingSetup()

    hls_prj_manager = HLSProjectManager(self.top_rtl_name, self.hls_prj_path, self.hls_solution_name)

    # first unify the module types in top RTL
    unifyModuleTypesInTopRTL(hls_prj_manager.getRTLDir(), hls_prj_manager.getTopRTLPath())

    top_rtl_parser = TopRTLParser(hls_prj_manager.getTopRTLPath())
    graph = DataflowGraph(hls_prj_manager, top_rtl_parser)

    slot_manager = SlotManager(self.board)

    user_constraint_s2v = self.parseUserConstraints(graph, slot_manager)
    grouping_constraints = top_rtl_parser.getStrictGroupingConstraints()

    # extract patterns to facilitate floorplanning
    pattern_insts = getPatternBasedGrouping(graph, self.peregrine_home)
    floorplan = self.runFloorplanning(graph, user_constraint_s2v, slot_manager, hls_prj_manager, 
                                      grouping_hints=pattern_insts, 
                                      grouping_constraints=grouping_constraints)

    # grid routing of edges 
    global_router = GlobalRouting(floorplan, top_rtl_parser, slot_manager)

    # latency balancing
    rebalance = LatencyBalancing(graph, floorplan, global_router)

    logging.info(f'Creating compute wrappers...')
    compute_wrapper_creater = CreateSlotWrapper(graph, top_rtl_parser, floorplan, global_router, rebalance, self.target)
    compute_wrapper_creater.getSlotWrapperForAll(dir='wrapper_rtl')

    logging.info(f'Creating routing inclusive wrappers...')
    routing_wrapper_create = CreateRoutingSlotWrapper(compute_wrapper_creater, floorplan, global_router, top_rtl_parser)
    routing_wrapper_create.createRoutingInclusiveWrapperForAll(dir='wrapper_rtl')

    logging.info(f'Creating the new top RTL file...')
    new_top_rtl = CreateTopRTL(top_rtl_parser, routing_wrapper_create, hls_prj_manager.getTopModuleName(), global_router)
    
    open(f'wrapper_rtl/{hls_prj_manager.getTopModuleName()}.v', 'w').write(new_top_rtl)
      
    logging.info(f'generating front end results...')
    json_creater = CreateResultJson(
                    floorplan, 
                    routing_wrapper_create, 
                    global_router, 
                    self.board, 
                    hls_prj_manager, 
                    slot_manager, 
                    top_rtl_parser,
                    new_top_rtl)
    json_creater.createResultJson()

  def basicSetup(self):
    # for designs with lots of modules, pyverilog may go very deep
    sys.setrecursionlimit(3000)

    self.device_manager = DeviceManager(self.config["Board"])
    self.board = self.device_manager.getBoard()

    self.top_rtl_name = self.config["TopName"]
    self.hls_prj_path = os.path.abspath(self.config["HLSProjectPath"])
    self.hls_solution_name = self.config["HLSSolutionName"]
    if "LoggingLevel" in self.config:
      self.logging_level = self.config["LoggingLevel"]
    else:
      self.logging_level = "INFO"

    if "Target" in self.config:
      self.target = self.config["Target"]
    else:
      self.target = "hw"

    self.peregrine_home = os.getenv('PEREGRINE_HOME')

  def loggingSetup(self):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s: %(funcName)25s() ] %(message)s")
    
    debug_file_handler = logging.FileHandler(filename='autoparallel-debug.log', mode='w')
    debug_file_handler.setLevel(logging.DEBUG)
    info_file_handler = logging.FileHandler(filename='autoparallel-info.log', mode='w')
    info_file_handler.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    handlers = [debug_file_handler, info_file_handler, stdout_handler]
    for handler in handlers:
      handler.setFormatter(formatter)
      root.addHandler(handler)

  def parseUserConstraints(self, graph, slot_manager):
    user_constraint_s2v = defaultdict(list)
    if "Floorplan" in self.config:
      user_fp_json = self.config["Floorplan"]
      for region, v_name_group in user_fp_json.items():
        slot = slot_manager.createSlot(region)
        for v_name in v_name_group:
          user_constraint_s2v[slot].append(graph.getVertex(v_name))

    return user_constraint_s2v

  def runFloorplanning(self, graph, user_constraint_s2v, slot_manager, hls_prj_manager, grouping_hints, grouping_constraints):
    floorplan = Floorplanner(
      graph, 
      user_constraint_s2v, 
      slot_manager=slot_manager, 
      total_usage=hls_prj_manager.getTotalArea(), 
      board=self.device_manager.getBoard(),
      user_max_usage_ratio=self.config['AreaUtilizationRatio'],
      grouping_hints=grouping_hints,
      grouping_constraints=grouping_constraints)
    
    if 'FloorplanMethod' in self.config:
      choice = self.config['FloorplanMethod']
      if choice == 'IterativeDivisionToFourCRs':
        floorplan.naiveFineGrainedFloorplan()
      elif choice == 'IterativeDivisionToHalfSLR':
        floorplan.coarseGrainedFloorplan()
      elif choice == 'PatternBasedFineGrainedFloorplan':
        floorplan.patternBasedFineGrainedFloorplan()
      elif choice == 'EightWayDivisionToHalfSLR':
        floorplan.eightWayPartition()
      else:
        assert False, f'unsupported floorplan method: {choice}'
    else:
      floorplan.coarseGrainedFloorplan() # by default

    floorplan.printFloorplan()
    return floorplan

  def help(self):
    manual = {
      "Board" : "Choose between U250 and U280",
      "TopName" : "The name of the top-level function of the HLS design",
      "HLSProjectPath" : "Absolute path to the post-csynth HLS project",
      "HLSSolutionName" : "Name of the solution of the HLS project",
      "FloorplanMethod" : "Choose between IterativeDivisionToFourCRs and IterativeDivisionToHalfSLR",
      "AreaUtilizationRatio" : "Allowed resource usage in each slot",
      "Floorplan (optional)" : {
        "This is a comment" : "User could dictate the final location of given modules",
        "Region" : [
          "RTL module 1",
          "RTL module 2"
        ]
      },
      "LoggingLevel (optional)": "Choose between DEBUG, INFO, WARNING, CRITICAL, ERROR"
    }
    print(json.dumps(manual, indent=2))

if __name__ == "__main__":
  assert len(sys.argv) == 2, 'input the path to the configuration file'
  m = Manager(sys.argv[1])
    


