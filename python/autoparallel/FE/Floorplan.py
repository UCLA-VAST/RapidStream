#! /usr/bin/python3.6
import logging
from collections import defaultdict
from typing import Dict
from autoparallel.FE.DeviceManager import *
from autoparallel.FE.DataflowGraph import *
from autoparallel.FE.HLSProjectManager import HLSProjectManager
from autoparallel.FE.Slot import Slot
from autoparallel.FE.SlotManager import SlotManager
from mip import *

_logger = logging.getLogger().getChild(__name__)

class Floorplanner:

  def __init__(
      self, 
      graph : DataflowGraph, 
      user_constraint_s2v : Dict, 
      slot_manager : SlotManager,
      total_usage : dict, 
      board=DeviceU250, 
      user_max_usage_ratio = 0.7,
      max_search_time=600, 
      grouping_constrants=[]):
    self.board = board
    self.graph = graph
    self.user_constraint_s2v = user_constraint_s2v
    self.slot_manager = slot_manager
    self.total_usage = total_usage
    self.max_search_time = max_search_time
    self.grouping_constrants = grouping_constrants # dict of dict
    self.s2v = {}
    self.v2s = {}
    self.s2e = {}

    self.max_usage_ratio = self.__getResourceUsageLimit(user_max_usage_ratio)

    self.__checker()

  def __checker(self):
    for v_group in self.user_constraint_s2v.values():
      for v in v_group:
        assert v in self.graph.getAllVertices(), f'{v.name} is not a valid RTL module'

  def __getResourceUsageLimit(self, user_max_usage_ratio):
    total_avail = self.board.TOTAL_AREA

    for item in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      usage = self.total_usage[item] / total_avail[item] + 0.05
      ratio = max(usage, user_max_usage_ratio)

    logging.info(f'Maximum resource usage ratio set as: {ratio}')
    return ratio

  def __initSlotToEdges(self):
    self.s2e = {}
    for s, v_group in self.s2v.items():
      assert v_group, f'incorrect empty slot: {s.getName()}'

      # add the edge if the src and dst are both in this slot
      intra_edges, inter_edges = self.getIntraAndInterEdges(v_group)
      self.s2e[s] = intra_edges

      # for the FIFO connecting two different slots, it should be assigned to the destination side
      v_set = set(v_group)
      for e in inter_edges:
        if e.dst in v_set:
          self.s2e[s].append(e)
          logging.debug(f'{e.name} is assigned with {e.dst.name}')

  # map all vertices to the initial slot (the whole device)
  def __getInitialSlotToVerticesMapping(self):
    init_slot = self.slot_manager.getInitialSlot()
    init_s2v = {init_slot : self.graph.getAllVertices()}
    init_v2s = {v : init_slot for v in self.graph.getAllVertices()}
    return init_s2v, init_v2s

  def __addAreaConstraints(self, m, curr_s2v, v2var, dir, delta=0):
    for s, v_group in curr_s2v.items():
      bottom_or_left, up_or_right = self.slot_manager.partitionSlotByHalf(s, dir)
      assert up_or_right.up_right_x >= bottom_or_left.down_left_x
  
      for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
        v_var_list = [v2var[v] for v in v_group]
        area_list = [v.area[r] for v in v_group]
        I = range(len(v_group))

        # for the up/right child slot (if mod_x is assigned 1)
        m += xsum( v_var_list[i] * area_list[i] for i in I ) <= up_or_right.getArea()[r] * (self.max_usage_ratio + delta)
        
        # for the down/left child slot (if mod_x is assigned 0)        
        m += xsum( (1-v_var_list[i]) * area_list[i] for i in I ) <= bottom_or_left.getArea()[r] * (self.max_usage_ratio + delta)

  def __addUserConstraints(self, m, curr_v2s, v2var, dir):
    for expect_slot, v_group in self.user_constraint_s2v.items():
      for v in v_group:
        assert v in curr_v2s, f'ERROR: user has forced the location of a non-existing module {v.name}'
        
        curr_slot = curr_v2s[v]
        bottom_or_left, up_or_right = self.slot_manager.partitionSlotByHalf(curr_slot, dir)
        if bottom_or_left.containsChildSlot(expect_slot):
          logging.debug(f'[user constraint] {v.name} assigned to bottom/left')
          m += v2var[v] == 0
        elif up_or_right.containsChildSlot(expect_slot):
          logging.debug(f'[user constraint] {v.name} assigned to up/right')
          m += v2var[v] == 1
        else:
          logging.warning(f'Potential wrong constraints from user: {v.name} -> {expect_slot.getName()}')

  # specify which modules must be assigned to the same slot
  # note that the key of curr_v2s is Vertex instead of name string
  def __addGroupingConstraints(self, m, curr_v2s, v2var):
    v_name_to_v = {v.name : v for v in curr_v2s.keys()}
    for grouping in self.grouping_constrants:
      assert grouping[0] in v_name_to_v, f'unknown vertex: {grouping[0]}'

      for i in range(1, len(grouping)):
        assert grouping[i] in v_name_to_v, f'unknown vertex: {grouping[i]}'

        logging.info(f'[grouping] {grouping[0]} is grouped with {grouping[i]}')
        m += v2var[v_name_to_v[grouping[0]]] == v2var[v_name_to_v[grouping[i]]]

  def __addOptGoal(self, m, curr_v2s, external_v2s, v2var, dir):
    def getVertexPosInChildSlot(v : Vertex):
      def getChildSlotPositionX(v):
        if v in external_v2s:
          return external_v2s[v].getPostionX() # const
        else:
          return curr_v2s[v].getQuarterPositionX() + v2var[v] * curr_v2s[v].getHalfLenX() # expr

      def getChildSlotPositionY(v):
        if v in external_v2s:
          return external_v2s[v].getPostionY() # const
        else:        
          return curr_v2s[v].getQuarterPositionY() + v2var[v] * curr_v2s[v].getHalfLenY() # expr

      if dir == 'VERTICAL':
        return getChildSlotPositionX(v)
      elif dir == 'HORIZONTAL':
        return getChildSlotPositionY(v)
      else:
        assert False

    # get all involved edges. Differentiate internal edges and boundary edges
    intra_edges, interface_edges = self.getIntraAndInterEdges(curr_v2s.keys())

    # cost function.
    edge_costs = [m.add_var(var_type=INTEGER, name=f'intra_{e.name}') for e in intra_edges] \
        + [m.add_var(var_type=INTEGER, name=f'inte_{e.name}') for e in interface_edges]

    all_edges = intra_edges + interface_edges
    for e_cost, e in zip(edge_costs, all_edges):
      m += e_cost >= getVertexPosInChildSlot(e.src) - getVertexPosInChildSlot(e.dst)
      m += e_cost >= getVertexPosInChildSlot(e.dst) - getVertexPosInChildSlot(e.src)

    m.objective = minimize(xsum(edge_costs[i] * edge.width for i, edge in enumerate(all_edges) ) )

  def __getPartitionResult(self, curr_s2v, v2var, dir):
    # create new mapping
    next_s2v = {}
    next_v2s = {}

    for s, v_group in curr_s2v.items():
      bottom_or_left, up_or_right = self.slot_manager.partitionSlotByHalf(s, dir)
      next_s2v[bottom_or_left] = []
      next_s2v[up_or_right] = []
      for v in v_group:
        # if v is assigned to 0-half
        if v2var[v].x == 0:
          next_s2v[bottom_or_left].append(v)
          next_v2s[v] = bottom_or_left
        
        # if v is assigned to 1-half
        elif v2var[v].x == 1:
          next_s2v[up_or_right].append(v)
          next_v2s[v] = up_or_right
        else:
          assert False

      # if no Vertex is assigned to a Slot, remove that Slot
      if not next_s2v[bottom_or_left]:
        next_s2v.pop(bottom_or_left)
        self.slot_manager.removeSlotNonBlocking(bottom_or_left.getName())
      if not next_s2v[up_or_right]:
        next_s2v.pop(up_or_right)
        self.slot_manager.removeSlotNonBlocking(up_or_right.getName())

    return next_s2v, next_v2s

  def __createILPVariables(self, m, curr_v2s):
    v2var = {} # str -> [mip_var]
    for v in curr_v2s.keys():
      v2var[v] = m.add_var(var_type=BINARY, name=f'{v.name}_x') 
    
    return v2var

  # could only be invoked at the beginning when there is only one slot
  def eightWayPartition(self):
    logging.info('Start 8-way partitioning routine')

    curr_s2v, curr_v2s = self.__getInitialSlotToVerticesMapping()

    m = Model()
    if not _logger.isEnabledFor(logging.DEBUG):
      m.verbose = 0    

    # three variables could determine the location of a module
    # y = y1 *2 + y2  (four slots)
    # x = x           (each SLR is divided by half) 
    v2var_x = {} 
    v2var_y1 = {}
    v2var_y2 = {}
    for v in curr_v2s.keys():
      v2var_x[v] = m.add_var(var_type=BINARY, name=f'{v.name}_x') 
      v2var_y1[v] = m.add_var(var_type=BINARY, name=f'{v.name}_y1') 
      v2var_y2[v] = m.add_var(var_type=BINARY, name=f'{v.name}_y2') 

    # get the target slots
    # for U280, slot_11x will have empty area
    init_slot = self.slot_manager.getInitialSlot()
    slot_0, slot_1 = self.slot_manager.getBottomAndUpSplit(init_slot)

    slot_00, slot_01 = self.slot_manager.getBottomAndUpSplit(slot_0)
    slot_10, slot_11 = self.slot_manager.getBottomAndUpSplit(slot_1)

    slot_000, slot_001 = self.slot_manager.getLeftAndRightSplit(slot_00)
    slot_010, slot_011 = self.slot_manager.getLeftAndRightSplit(slot_01)
    slot_100, slot_101 = self.slot_manager.getLeftAndRightSplit(slot_10)
    slot_110, slot_111 = self.slot_manager.getLeftAndRightSplit(slot_11)
    
    # must not change order!
    slot_group = [slot_000, slot_001, \
                  slot_010, slot_011, \
                  slot_100, slot_101, \
                  slot_110, slot_111 ]
    # note that slot_idx is different from slot position
    slot_idx = lambda y1, y2, x : y1 * 4 + y2 * 2 + x

    # area constraint
    for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      choose = lambda x, num: x if num == 1 else (1-x)     

      for y1 in range(2):
        for y2 in range(2):
          for x in range(2):
            # convert logic AND to linear constraints
            # prods[v] = choose_y1 AND choose_y2 AND choose_x
            prods = { v : m.add_var(var_type=BINARY, name=f'{v.name}_choose{y1}{y2}{x}') for v in curr_v2s.keys() }
            for v in curr_v2s.keys():
              m +=  choose(v2var_y1[v], y1) + choose(v2var_y2[v], y2) + \
                    choose(v2var_x[v], x) - 3 * prods[v] >= 0
              m +=  choose(v2var_y1[v], y1) + choose(v2var_y2[v], y2) + \
                    choose(v2var_x[v], x) - 3 * prods[v] <= 2

            m += xsum(  prods[v] * v.area[r] for v in curr_v2s.keys() ) \
                        <= slot_group[slot_idx(y1, y2, x)].getArea()[r] * self.max_usage_ratio

    # user constraint
    for expect_slot, v_group in self.user_constraint_s2v.items():
      for v in v_group:
        assert v in curr_v2s, f'ERROR: user has forced the location of a non-existing module {v.name}'

        for y1 in range(2):
          for y2 in range(2):
            for x in range(2):
              if slot_group[slot_idx(y1, y2, x)].containsChildSlot(expect_slot):
                m += v2var_y1[v] == y1
                m += v2var_y2[v] == y2
                m += v2var_x[v] == x    

    # grouping constraints
    for v2var in [v2var_x, v2var_y1, v2var_y2]:
      self.__addGroupingConstraints(m, curr_v2s=curr_v2s, v2var=v2var)                      

    # add optimization goal
    intra_edges, interface_edges = self.getIntraAndInterEdges(curr_v2s.keys())
    edge_costs = [m.add_var(var_type=INTEGER, name=f'intra_{e.name}') for e in intra_edges] \
        + [m.add_var(var_type=INTEGER, name=f'inter_{e.name}') for e in interface_edges]
    all_edges = intra_edges + interface_edges
    
    # note pos is different from slot_idx, becasue the x dimension is different from the y dimention
    # we will use |(y1 * 2 + y1) - (y2 * 2 + y2)| + |x1 - x2| to express the hamming distance
    pos_y = lambda v : v2var_y1[v] * 2 + v2var_y2[v] 
    pos_x = lambda v : v2var_x[v]
    cost_y = lambda e : pos_y(e.src) - pos_y(e.dst)
    cost_x = lambda e : pos_x(e.src) - pos_x(e.dst)

    for e_cost_var, e in zip(edge_costs, all_edges):
      m += e_cost_var >= cost_y(e) + cost_x(e)
      m += e_cost_var >= -cost_y(e) + cost_x(e)
      m += e_cost_var >= cost_y(e) - cost_x(e)
      m += e_cost_var >= -cost_y(e) - cost_x(e)

    m.objective = minimize(xsum(edge_costs[i] * edge.width for i, edge in enumerate(all_edges) ) )

    logging.info('Start ILP solver')
    # m.write('Coarse-Grained-Floorplan.lp')
    status = m.optimize(max_seconds=self.max_search_time)
    assert status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE, '8-way partioning failed!'

    # extract results
    next_s2v = defaultdict(list)
    next_v2s = {}
    
    for v in curr_v2s.keys():
      idx = int(slot_idx(v2var_y1[v].x,  v2var_y2[v].x, v2var_x[v].x))
      next_s2v[slot_group[idx]].append(v)
      next_v2s[v] = slot_group[idx]

    self.printFloorplan()

    self.s2v, self.v2s = next_s2v, next_v2s
    self.__initSlotToEdges()

    return
  
  # use iterative 2-way partitioning when there are lots of small functions
  def __twoWayPartition(self, curr_s2v : Dict, curr_v2s : Dict, dir : str, external_v2s : Dict = {}, delta=0.0):
    assert set(map(type, curr_s2v.keys())) == {Slot}
    assert set(map(type, curr_v2s.keys())) == {Vertex}
    logging.info('Start 2-way partitioning routine')

    m = Model()
    if not _logger.isEnabledFor(logging.DEBUG):
      m.verbose = 0

    v2var = self.__createILPVariables(m, curr_v2s=curr_v2s)

    self.__addOptGoal(m, curr_v2s=curr_v2s, external_v2s=external_v2s, v2var=v2var, dir=dir)
    
    # area constraints for each child slot
    self.__addAreaConstraints(m, curr_s2v=curr_s2v, v2var=v2var, dir=dir, delta=delta)

    self.__addUserConstraints(m, curr_v2s=curr_v2s, v2var=v2var, dir=dir)

    self.__addGroupingConstraints(m, curr_v2s=curr_v2s, v2var=v2var)
    
    logging.info('Start ILP solver')
    # m.write('Coarse-Grained-Floorplan.lp')
    status = m.optimize(max_seconds=self.max_search_time)
    assert status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE, '2-way partioning failed!'

    next_s2v, next_v2s = self.__getPartitionResult(curr_s2v=curr_s2v, v2var=v2var, dir=dir)

    return next_s2v, next_v2s

  def printFloorplan(self, target_s2v = {}):
    logging.info('Show current floorplan result:')
    if not target_s2v:
      target_s2v = self.s2v

    for s, v_group in target_s2v.items():
      logging.info(f'{s.getName()}:')
      for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
        used = sum([v.area[r] for v in v_group])
        avail = s.getArea()[r]
        if avail:
          logging.info(f'[{r}]: {used} / {avail} = {used/avail}')
        else:
          logging.info(f'[{r}]: {used} used, 0 exists')
      for v in v_group:
        logging.info(f'  Kernel: {v.name}')
      for e in self.s2e[s]:
        logging.info(f'  FIFO: {e.name}')

  def getUtilization(self):
    util = defaultdict(dict)
    for s, v_group in self.s2v.items():
      assert v_group, f'empty slot should not exist: {s.getName()}'
      for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
        used = sum([v.area[r] for v in v_group])
        avail = s.getArea()[r]
        util[s.getRTLModuleName()][r] = f'{used} / {avail} = {used/avail}'
    return util

  # obtain the edges that are inside the given slots and the edges between the given slots and the other slots
  def getIntraAndInterEdges(self, v_group):
    second_visited_edges = set()
    first_visited_edges = set()

    # if an edge is visited twice, then it is entirely within the target slots
    # if an edge is visited only once, then it is between the target slots and the remaining slots
    for v in v_group:
      for e in v.getEdges():
        if e in first_visited_edges:
          second_visited_edges.add(e)
          first_visited_edges.remove(e)
        else:
          first_visited_edges.add(e)
          
          # double check that an edge will not be visited a 3rd time
          assert e not in second_visited_edges

    interface_edges = list(first_visited_edges)
    intra_edges = list(second_visited_edges)

    return intra_edges, interface_edges

  def coarseGrainedFloorplan(self):
    init_s2v, init_v2s = self.__getInitialSlotToVerticesMapping()
    iter1_s2v, iter1_v2s = self.__twoWayPartition(init_s2v, init_v2s, 'HORIZONTAL', delta=-0.05) # based on die boundary

    iter2_s2v, iter2_v2s = self.__twoWayPartition(iter1_s2v, iter1_v2s, 'HORIZONTAL', delta=-0.05) # based on die boundary

    self.s2v, self.v2s = self.__twoWayPartition(iter2_s2v, iter2_v2s, 'VERTICAL', delta=0.05) # based on ddr ctrl in the middle

    self.__initSlotToEdges()
    self.printFloorplan()


  def naiveFineGrainedFloorplan(self):
    init_s2v, init_v2s = self.__getInitialSlotToVerticesMapping()
    iter1_s2v, iter1_v2s = self.__twoWayPartition(init_s2v, init_v2s, 'HORIZONTAL', delta=-0.1) # based on die boundary

    iter2_s2v, iter2_v2s = self.__twoWayPartition(iter1_s2v, iter1_v2s, 'HORIZONTAL',  delta=-0.05) # based on die boundary

    iter3_s2v, iter3_v2s = self.__twoWayPartition(iter2_s2v, iter2_v2s, 'VERTICAL',  delta=-0.05) # based on die boundary

    iter4_s2v, iter4_v2s = self.__twoWayPartition(iter3_s2v, iter3_v2s, 'HORIZONTAL',  delta=0.0) # based on die boundary

    self.s2v, self.v2s = self.__twoWayPartition(iter4_s2v, iter4_v2s, 'VERTICAL',  delta=0.15) # based on ddr ctrl in the middle

    self.__initSlotToEdges()
    self.printFloorplan()

  def naiveTwoCRGranularityFloorplan(self):
    init_s2v, init_v2s = self.__getInitialSlotToVerticesMapping()
    iter1_s2v, iter1_v2s = self.__twoWayPartition(init_s2v, init_v2s, 'HORIZONTAL') # based on die boundary

    iter2_s2v, iter2_v2s = self.__twoWayPartition(iter1_s2v, iter1_v2s, 'HORIZONTAL') # based on die boundary

    iter3_s2v, iter3_v2s = self.__twoWayPartition(iter2_s2v, iter2_v2s, 'HORIZONTAL') # based on die boundary

    iter4_s2v, iter4_v2s = self.__twoWayPartition(iter3_s2v, iter3_v2s, 'VERTICAL') # based on die boundary

    iter5_s2v, iter5_v2s = self.__twoWayPartition(iter4_s2v, iter4_v2s, 'VERTICAL') # based on die boundary

    self.s2v, self.v2s = self.__twoWayPartition(iter5_s2v, iter5_v2s, 'VERTICAL') # based on ddr ctrl in the middle

    self.__initSlotToEdges()    
    self.printFloorplan()

  def getSlotToVertices(self):
    return self.s2v

  def getSlotToEdges(self):
    return self.s2e

  def getVertexToSlot(self):
    return self.v2s

  def getSlotNameToVertexNames(self):
    s_name_2_v_names = {}
    for slot, v_group in self.s2v.items():
      s_name_2_v_names[slot.getName()] = {v.type : v.name for v in v_group}
    return s_name_2_v_names
  
  def getSlotNameToEdgeNames(self):
    s_name_2_e_names = {}
    for slot, e_group in self.s2e.items():
      s_name_2_e_names[slot.getName()] = [e.name for e in e_group]
    return s_name_2_e_names