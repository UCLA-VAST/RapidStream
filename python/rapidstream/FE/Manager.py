import json
import logging
import os
import sys
from collections import defaultdict

from autobridge.HLSParser.vivado_hls.HLSProjectManager import HLSProjectManager
from autobridge.Device.DeviceManager import DeviceManager
from autobridge.Opt.DataflowGraph import DataflowGraph
from autobridge.HLSParser.vivado_hls.TopRTLParser import TopRTLParser
from autobridge.Opt.Floorplan import Floorplanner
from autobridge.Opt.SlotManager import SlotManager
from autobridge.Opt.LatencyBalancing import LatencyBalancing

from rapidstream.FE.GlobalRouting import GlobalRouting
from rapidstream.FE.CreateSlotWrapper import CreateSlotWrapper
from rapidstream.FE.CreateRoutingSlotWrapper import CreateRoutingSlotWrapper
from rapidstream.FE.CreateCtrlSlotWrapper import CreateCtrlSlotWrapper
from rapidstream.FE.CreateResultJson import CreateResultJson
from rapidstream.FE.CreateTopRTLForCtrlWrappers import CreateTopRTLForCtrlWrappers
from rapidstream.FE.FIFOCalibration import FIFOCalibration


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
    # unifyModuleTypesInTopRTL(hls_prj_manager.getRTLDir(), hls_prj_manager.getTopRTLPath())

    top_rtl_parser = TopRTLParser(hls_prj_manager.getTopRTLPath())
    graph = DataflowGraph(hls_prj_manager, top_rtl_parser)

    slot_manager = SlotManager(self.board)

    user_constraint_s2v = self.parseUserConstraints(graph, slot_manager)
    grouping_constraints = top_rtl_parser.getStrictGroupingConstraints()

    # extract patterns to facilitate floorplanning
    # pattern_insts = getPatternBasedGrouping(graph, self.peregrine_home)
    pattern_insts = []
    floorplan = self.runFloorplanning(graph, user_constraint_s2v, slot_manager, hls_prj_manager,
                                      max_search_time=180,
                                      grouping_hints=pattern_insts, 
                                      grouping_constraints=grouping_constraints)
    open('floorplan_results.json', 'w').write(json.dumps({"FloorplanVertex":floorplan.getSlotNameToVertexNames()}, indent=2))

    # grid routing of edges 
    logging.info(f'Pipeline style is: {self.pipeline_style}')
    global_router = GlobalRouting(floorplan, top_rtl_parser, slot_manager, self.pipeline_style, self.anchor_plan)

    # latency balancing
    rebalance = LatencyBalancing(graph, floorplan, global_router)

    FIFOCalibration(floorplan)

    logging.info(f'Creating compute wrappers...')
    compute_wrapper_creater = CreateSlotWrapper(graph, top_rtl_parser, floorplan, global_router, rebalance, self.target)
    compute_wrapper_creater.getSlotWrapperForAll(dir='wrapper_rtl')

    logging.info(f'Creating routing inclusive wrappers...')
    routing_wrapper_creater = CreateRoutingSlotWrapper(compute_wrapper_creater, floorplan, global_router, top_rtl_parser, self.pipeline_style, self.anchor_plan)
    routing_wrapper_creater.createRoutingInclusiveWrapperForAll(dir='wrapper_rtl')

    logging.info(f'Creating ctrl inclusive wrappers...')
    ctrl_wrapper_creater = CreateCtrlSlotWrapper(routing_wrapper_creater, floorplan, slot_manager)
    ctrl_wrapper_creater.createCtrlInclusiveWrapperForAll(dir='wrapper_rtl')


    logging.info(f'Creating the new top RTL file...')
    new_top_rtl = CreateTopRTLForCtrlWrappers(top_rtl_parser, ctrl_wrapper_creater, hls_prj_manager.getTopModuleName(), global_router, self.target)
    
    open(f'wrapper_rtl/{hls_prj_manager.getTopModuleName()}.v', 'w').write(new_top_rtl)
      
    logging.info(f'generating front end results...')
    json_creater = CreateResultJson(
                    floorplan, 
                    ctrl_wrapper_creater, 
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

    self.pipeline_style = self.config['PipelineStyle']

    # how many anchor to use between two slots
    # originally the plan is to use 1 FF to pipeline the connection between two adjacent slots
    # in order to make the stitching easier, here we use more FFs.
    # from the outside, we still only use 1 FF between the slots
    # however, inside the slot, the input / output ports are additionally registered
    # in this way, when we do the slot stitching, we only need to route between registers
    self.anchor_plan = int(self.config['AnchorPlan'])

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
    formatter = logging.Formatter("[%(levelname)s: %(funcName)s() %(filename)s:%(lineno)d] %(message)s")
    
    debug_file_handler = logging.FileHandler(filename='rapidstream-debug.log', mode='w')
    debug_file_handler.setLevel(logging.DEBUG)
    info_file_handler = logging.FileHandler(filename='rapidstream-info.log', mode='w')
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

    if "ResultReuse" in self.config:
      old_hub = json.loads(open(self.config["ResultReuse"], 'r').read())
      s2v_type2v_name = old_hub["FloorplanVertex"]
      s2v = {slot : list(v_type2v_name.values()) for slot, v_type2v_name in s2v_type2v_name.items()}
      for region, v_name_group in s2v.items():
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
      if choice == 'NaiveFineGrainedFloorplan':
        floorplan.naiveFineGrainedFloorplan()
      elif choice == 'IterativeDivisionToHalfSLR':
        floorplan.coarseGrainedFloorplan()
      elif choice == 'PatternBasedFineGrainedFloorplan':
        floorplan.patternBasedFineGrainedFloorplan()
      elif choice == 'EightWayDivisionToHalfSLR':
        floorplan.eightWayPartition()
      elif choice == 'hetero4CRFloorplan':
        floorplan.hetero4CRFloorplan()
      elif choice == 'floorplanVHHvh':
        floorplan.floorplanVHHvh()
      else:
        assert False, f'unsupported floorplan method: {choice}'
    else:
      floorplan.coarseGrainedFloorplan() # by default

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
    


