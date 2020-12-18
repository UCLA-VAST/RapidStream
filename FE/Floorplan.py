#! /usr/bin/python3.6
import logging
from collections import defaultdict
from typing import Dict
from DeviceManager import *
from DataflowGraph import DataflowGraph
from mip import *

class Slot:
  def __init__(self, board, down_left_x, down_left_y, up_right_x, up_right_y):
    self.board = board

    # enlarge the values to avoid fraction in later operations
    ratio = 4
    self.down_left_x = int(down_left_x * ratio)
    self.down_left_y = int(down_left_y * ratio)
    self.up_right_x = int(up_right_x * ratio)
    self.up_right_y = int(up_right_y * ratio)
    
    self.area = {}
    self.initArea()

  def __hash__(self):
    logging.warning('Using customized hash function for Slot')
    assert self.down_left_x < 100
    assert self.down_left_y < 100
    assert self.up_right_x < 100
    assert self.up_right_y < 100

    return hash(str(self.down_left_x).zfill(3) + \
                str(self.down_left_y).zfill(3) + \
                str(self.up_right_x).zfill(3) + \
                str(self.up_right_y).zfill(3) )

  # calculate the available resources of this slot
  def initArea(self):
    for item in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      self.area[item] = 0
      for i in range(self.down_left_x, self.up_right_x+1):
        self.area[item] += self.board.CR_AREA[i][item]
      
      # vertically the CRs are the same
      self.area[item] *= (self.up_right_y - self.down_left_y + 1)
    
    self.area['LAGUNA'] = 0
    for i in self.board.getLagunaPositionY():
      if self.down_left_y <= i <= self.up_right_y:
        self.area['LAGUNA'] += self.board.LAGUNA_PER_CR

  def getArea(self):
    return self.area
  
  # use the middle point as the position of the slot. Check the results have no fractional part
  def getPositionX(self):
    ans = (self.down_left_x + self.up_right_x) / 2
    assert ans == int(ans)
    return ans

  def getPositionY(self):
    ans = (self.down_left_y + self.up_right_y) / 2
    assert ans == int(ans)
    return ans
  
  def getQuarterPositionX(self):
    ans = self.down_left_x + (self.up_right_x - self.down_left_x) / 4
    assert ans == int(ans)
    return ans

  def getQuarterPositionY(self):
    ans = self.down_left_y + (self.up_right_y - self.down_left_y) / 4
    assert ans == int(ans)
    return ans

  def getHalfLenX(self):
    ans = (self.up_right_x - self.down_left_x) / 2
    assert ans == int(ans)
    return ans

  def getHalfLenY(self):
    ans = (self.up_right_y - self.down_left_y) / 2
    assert ans == int(ans)
    return ans

  # split by the middle row
  def getBottomAndUpSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'

    #                  |-------| u_r_x, u_r_y
    #                  |  up   |
    #   d_l_x, mid_y   |-------| u_r_x, mid_y   
    #                  |  bot  |
    #   d_l_x, d_l_y   |-------|
    mid_y = self.getPositionY()
    up     = Slot(self.board, self.down_left_x, mid_y,            self.up_right_x, self.up_right_y)
    bottom = Slot(self.board, self.down_left_x, self.down_left_y, self.up_right_x, mid_y)

    logging.debug(f'Horizontal Partition: from ({self.down_left_x}, {self.down_left_y}, {self.up_right_x}, {self.up_right_y}) to \
      ({up.down_left_x}, {up.down_left_y}, {up.up_right_x}, {up.up_right_y}) and \
      ({bottom.down_left_x}, {bottom.down_left_y}, {bottom.up_right_x}, {bottom.up_right_y})  ')
    return bottom, up 

  # split by the middle column
  def getLeftAndRightSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'
    
    #                mid_x, u_r_y
    #               |-----|-----| u_r_x, u_r_y
    #               |     |     |
    #               |  L  |  R  |
    #               |     |     |
    #  d_l_x, d_l_y |-----|-----|
    #                mid_x, d_l_y
    #
    mid_x = int(self.down_left_x + self.up_right_x) / 2
    left =  Slot(self.board, self.down_left_x, self.down_left_y, mid_x,           self.up_right_y)
    right = Slot(self.board, mid_x,            self.down_left_y, self.up_right_x, self.up_right_y)

    logging.debug(f'Vertical Partition: from ({self.down_left_x}, {self.down_left_y}, {self.up_right_x}, {self.up_right_y}) to \
      ({left.down_left_x}, {left.down_left_y}, {left.up_right_x}, {left.up_right_y}) and \
      ({right.down_left_x}, {right.down_left_y}, {right.up_right_x}, {right.up_right_y})  ')

    return left, right

  def partitionByHalf(self, dir : str):
    if dir == 'HORIZONTAL':
      return self.getBottomAndUpSplit()
    elif dir == 'VERTICAL':
      return self.getLeftAndRightSplit()
    else:
      assert False, f'unrecognized partition direction: {dir}'

  def containsChildSlot(self, target : Slot) -> bool:
    return target.down_left_x >= self.down_left_x \
      and  target.down_left_y >= self.down_left_y \
      and  target.up_right_x  <= self.up_right_x  \
      and  target.up_right_y  <= self.up_right_y  

class Floorplanner:

  def __init__(self, graph : DataflowGraph, user_constraint_v2s : Dict, board=DeviceU250, max_search_time=600):
    self.board = board
    self.graph = graph
    self.user_constraint_v2s = user_constraint_v2s
    self.max_search_time = max_search_time

    self.checker()

  def checker(self):
    for v in self.user_constraint_v2s.keys():
      assert v in self.graph.getAllVertices(), f'{v.name} is not a valid RTL module'
      
  def coarseGrainedFloorplan(self):
    init_s2v, init_v2s = self.getInitialSlotToVerticesMapping()
    iter1_s2v, iter1_v2s = self.partitionGivenSlotsByHalf(init_s2v, init_v2s, 'HORIZONTAL') # based on die boundary
    iter2_s2v, iter2_v2s = self.partitionGivenSlotsByHalf(iter1_s2v, iter1_v2s, 'HORIZONTAL') # based on die boundary
    iter3_s2v, iter3_v2s = self.partitionGivenSlotsByHalf(iter2_s2v, iter2_v2s, 'VERTICAL') # based on ddr ctrl in the middle
    return iter3_s2v, iter3_v2s

  # map all vertices to the initial slot (the whole device)
  def getInitialSlotToVerticesMapping(self):
    init_slot = self.board.getInitialSlot()
    init_s2v = {init_slot : [v.name for v in self.graph.getAllVertices()]}
    init_v2s = {v.name : init_slot for v in self.graph.getAllVertices()}
    return init_s2v, init_v2s

  def addAreaConstraints(self, m, curr_s2v, v2var):
    for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      for s, v_group in curr_s2v.items():
        bottom_or_left, up_or_right = s.partitionByHalf(dir)
        assert up_or_right.up_right_x >= bottom_or_left.down_left_x

        # for the up/right child slot (if mod_x is assigned 1)
        cmd = 'm += 0'
        for v in v_group:
          cmd += f' + v2var["{v.name}"] * {getattr(v.area, r)}'
        cmd += f'<= {getattr(up_or_right.getArea(), r)}'
        exec(cmd) 

        # for the down/left child slot (if mod_x is assigned 0)
        cmd = 'm += 0'
        for v in v_group:
          cmd += f' + (1 - v2var["{v.name}"]) * {getattr(v.area, r)}'
        cmd += f'<= {getattr(bottom_or_left.getArea(), r)}'
        exec(cmd)     

  def addUserConstraints(self, m, curr_v2s, v2var):
    for v_name, expect_slot in self.user_constraint_v2s.items():
      curr_slot = curr_v2s[v_name]
      bottom_or_left, up_or_right = curr_slot.partitionByHalf(dir)
      if bottom_or_left.containsChildSlot(expect_slot):
        m += v2var[v_name] == 0
      elif up_or_right.containsChildSlot(expect_slot):
        m += v2var[v_name] == 1
      else:
        assert False, f'Wrong constraints from user on {v_name}'

  def addOptGoal(self, m, curr_v2s, external_v2s, v2var):
    def getChildSlotPos(v_name):
      def getChildSlotPositionX(v_name):
        if v_name in external_v2s:
          return external_v2s[v_name].getPostionX() # const
        else:
          return curr_v2s[v_name].getQuarterPositionX() + v2var[v_name] * curr_v2s[v_name].getHalfLenX() # expr

      def getChildSlotPositionY(v_name):
        if v_name in external_v2s:
          return external_v2s[v_name].getPostionY() # const
        else:        
          return curr_v2s[v_name].getQuarterPositionY() + v2var[v_name] * curr_v2s[v_name].getHalfLenY() # expr

      if dir == 'VERTICAL':
        return getChildSlotPositionX(v_name)
      elif dir == 'HORIZONTAL':
        return getChildSlotPositionY(v_name)
      else:
        assert False

    # obtain the edges that are inside the given slots and the edges between the given slots and the other slots
    def classifyEdges():
      second_visited_edges = set()
      first_visited_edges = set()

      # if an edge is visited twice, then it is entirely within the target slots
      # if an edge is visited only once, then it is between the target slots and the remaining slots
      for v in curr_v2s.keys():
        for e_name in v.getEdgeNames():
          if e_name in first_visited_edges:
            second_visited_edges.add(e_name)
            first_visited_edges.remove(e_name)
          else:
            first_visited_edges.add(e_name)
            
            # double check that an edge will not be visited a 3rd time
            assert e_name not in second_visited_edges

      interface_edges = list(first_visited_edges)
      intra_edges = list(second_visited_edges) 

      return intra_edges, interface_edges

    # get all involved edges. Differentiate internal edges and boundary edges
    intra_edges, interface_edges = classifyEdges()

    # cost function.
    edge_costs = [m.add_var(var_type=INTEGER, name=f'intra_edge_cost_{e.name}_{i}') for i, e in enumerate(intra_edges)] \
        + [m.add_var(var_type=INTEGER, name=f'inter_edge_cost_{e.name}_{i}') for i, e in enumerate(interface_edges)]

    all_edges = intra_edges + interface_edges
    for e_cost, e in zip(edge_costs, all_edges):
      m += e_cost >= getChildSlotPos(e.src.name) - getChildSlotPos(e.dst.name)
      m += e_cost >= getChildSlotPos(e.dst.name) - getChildSlotPos(e.src.name)

    m.objective = minimize(xsum(edge_costs[i] * edge.width for i, edge in enumerate(all_edges) ) )

  def getPartitionResult(self, curr_s2v, v2var):
    # create new mapping
    next_s2v = defaultdict(list)
    next_v2s = {}

    # map from slot to sub-slot
    for s, v_group in curr_s2v.items():
      bottom_or_left, up_or_right = s.partitionByHalf(dir)
      for v_name in v_group:
        if v2var[v_name].x == 0:
          next_s2v[bottom_or_left].append(v_name)
          next_v2s[v_name] = bottom_or_left
        elif v2var[v_name].x == 1:
          next_s2v[up_or_right].append(v_name)
          next_v2s[v_name] = up_or_right
        else:
          assert False

    return next_s2v, next_v2s

  def initILPVariables(self, m, curr_s2v):
    v2var = {} # str -> [mip_var]
    for i, v in enumerate(curr_s2v.values()):
      v2var[v.name] = m.add_var(var_type=BINARY, name=f'{v.name}_{i}_x') 
    
    return v2var

  def partitionGivenSlotsByHalf(self, curr_s2v : Dict, curr_v2s : Dict, dir : str, external_v2s : Dict = {}):
    assert set(map(type, curr_s2v.keys())) == {Slot}
    assert set(map(type, curr_v2s.keys())) == {str}

    m = Model()

    v2var = self.initILPVariables(m, curr_s2v=curr_s2v)

    self.addOptGoal(m, curr_v2s=curr_v2s, external_v2s=external_v2s, v2var=v2var)
    
    # area constraints for each child slot
    self.addAreaConstraints(m, curr_s2v=curr_s2v, v2var=v2var)

    self.addUserConstraints(m, curr_v2s=curr_v2s, v2var=v2var)
    
    m.write('Coarse-Grained-Floorplan.lp')
    m.optimize(max_seconds=self.max_search_time)

    return self.getPartitionResult(curr_s2v=curr_s2v, v2var=v2var)


     