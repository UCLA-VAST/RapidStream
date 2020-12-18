#! /usr/bin/python3.6
import logging
from collections import defaultdict
from typing import Dict
from DeviceManager import *
from DataflowGraph import *
from mip import *

class Slot:
  def __init__(self, board, down_left_x, down_left_y, up_right_x, up_right_y):
    self.board = board

    self.down_left_x = down_left_x
    self.down_left_y = down_left_y
    self.up_right_x = up_right_x
    self.up_right_y = up_right_y
    
    self.area = {}
    self.initArea()

  def __hash__(self):
    return hash(str(self.down_left_x) + str(self.down_left_y) + str(self.up_right_x) + str(self.up_right_y))

  # calculate the available resources of this slot
  def initArea(self):
    for item in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      self.area[item] = 0
      for i in range(self.down_left_x, self.up_right_x+1):
        self.area[item] += self.board.CR_AREA[i][item]
      
      self.area[item] *= (self.up_right_y - self.down_left_y + 1)
    
    self.area['LAGUNA'] = 0
    for i in [3, 4, 7, 8, 11, 12]:
      if self.down_left_y <= i <= self.up_right_y:
        self.area['LAGUNA'] += self.board.LAGUNA_PER_CR

  def getArea(self):
    return self.area
  
  # use the middle point as the position of the slot
  def getPositionX(self):
    return (self.down_left_x + self.up_right_x) / 2

  def getPositionY(self):
    return (self.down_left_y + self.up_right_y) / 2

  def getQuarterPositionX(self):
    return self.down_left_x + (self.up_right_x - self.down_left_x) / 4
  
  def getQuarterPositionY(self):
    return self.down_left_y + (self.up_right_y - self.down_left_y) / 4

  def getHalfLenX(self):
    return (self.up_right_x - self.down_left_x) / 2

  def getHalfLenY(self):
    return (self.up_right_y - self.down_left_y) / 2

  # split by the middle row
  def getBottomAndUpSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'
    mid_y = int(self.down_left_y + self.up_right_y) / 2

    bottom = Slot(self.board, self.down_left_x, mid_y,            self.up_right_x, self.up_right_y)
    up     = Slot(self.board, self.down_left_x, self.down_left_y, self.up_right_x, mid_y)

    return bottom, up 

  # split by the middle column
  def getLeftAndRightSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'
    mid_x = int(self.down_left_x + self.up_right_x) / 2

    left =  Slot(self.board, self.down_left_x, self.down_left_y, mid_x,           self.up_right_y)
    right = Slot(self.board, mid_x,            self.down_left_y, self.up_right_x, self.up_right_y)

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
    for v, s in self.user_constraint_v2s.items():
      assert v in self.graph.getAllVertices(), f'{v.name} is not a valid RTL module'
      
  def coarseGrainedFloorplan(self):
    init_s2v, init_v2s = self.getInitialSlotToVerticesMapping()
    iter1_s2v, iter1_v2s = self.partitionGivenSlotsByHalf(init_s2v, init_v2s, 'HORIZONTAL')
    iter2_s2v, iter2_v2s = self.partitionGivenSlotsByHalf(iter1_s2v, iter1_v2s, 'HORIZONTAL')
    iter3_s2v, iter3_v2s = self.partitionGivenSlotsByHalf(iter2_s2v, iter2_v2s, 'VERTICAL')
    return iter3_s2v, iter3_v2s

  # map all vertices to the initial slot (the whole device)
  def getInitialSlotToVerticesMapping(self):
    init_slot = self.board.getInitialSlot()
    init_s2v = {init_slot : [v.name for v in self.graph.getAllVertices()]}
    init_v2s = {v.name : init_slot for v in self.graph.getAllVertices()}
    return init_s2v, init_v2s

  def partitionGivenSlotsByHalf(self, curr_s2v : Dict, curr_v2s : Dict, dir : str, external_v2s : Dict = {}):
    assert set(map(type, curr_s2v.keys())) == {Slot}
    assert set(map(type, curr_v2s.keys())) == {str}

    m = Model()

    mods_x = {} # str -> [mip_var]
    for i, v in enumerate(curr_s2v.values()):
      mods_x[v.name] = m.add_var(var_type=BINARY, name=f'{v.name}_{i}_x') 

    # get all involved edges. Differentiate internal edges and boundary edges
    intra_edges, interface_edges = self.classifyEdges(curr_s2v)

    def getChildSlotPos(v_name):
      def getChildSlotPositionX(v_name):
        if v_name in external_v2s:
          return external_v2s[v_name].getPostionX() # const
        else:
          return curr_v2s[v_name].getQuarterPositionX() + mods_x[v_name] * curr_v2s[v_name].getHalfLenX() # expr

      def getChildSlotPositionY(v_name):
        if v_name in external_v2s:
          return external_v2s[v_name].getPostionY() # const
        else:        
          return curr_v2s[v_name].getQuarterPositionY() + mods_x[v_name] * curr_v2s[v_name].getHalfLenY() # expr

      if dir == 'VERTICAL':
        return getChildSlotPositionX(v_name)
      elif dir == 'HORIZONTAL':
        return getChildSlotPositionY(v_name)
      else:
        assert False
    
    # cost function. Name based on the paper
    d_x = [m.add_var(var_type=INTEGER, name=f'd_x_intra_{e.name}_{i}') for i, e in enumerate(intra_edges)] \
        + [m.add_var(var_type=INTEGER, name=f'd_x_interface_{e.name}_{i}') for i, e in enumerate(interface_edges)]

    all_edges = intra_edges + interface_edges
    for d_x_i, e in zip(d_x, all_edges):
      m += d_x_i >= getChildSlotPos(e.src.name) - getChildSlotPos(e.dst.name)
      m += d_x_i >= getChildSlotPos(e.dst.name) - getChildSlotPos(e.src.name)

    m.objective = minimize(xsum(d_x[i] * edge.width for i, edge in enumerate(all_edges) ) )
    
    # area constraints for each child slot
    for r in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      for s, v_group in curr_s2v.items():
        bottom_or_left, up_or_right = s.partitionByHalf(dir)

        # for the up/right child slot (if mod_x is assigned 1)
        cmd = 'm += 0'
        for v in v_group:
          cmd += f' + mods_x["{v.name}"] * {getattr(v.area, r)}'
        cmd += f'<= {getattr(up_or_right.getArea(), r)}'
        exec(cmd) 

        # for the down/left child slot (if mod_x is assigned 0)
        cmd = 'm += 0'
        for v in v_group:
          cmd += f' + (1 - mods_x["{v.name}"]) * {getattr(v.area, r)}'
        cmd += f'<= {getattr(bottom_or_left.getArea(), r)}'
        exec(cmd)                

    # user constraint
    for v_name, expect_slot in self.user_constraint_v2s.items():
      curr_slot = curr_v2s[v_name]
      bottom_or_left, up_or_right = curr_slot.partitionByHalf(dir)
      if bottom_or_left.containsChildSlot(expect_slot):
        m += mods_x[v_name] == 0
      elif up_or_right.containsChildSlot(expect_slot):
        m += mods_x[v_name] == 1
      else:
        assert False, f'Wrong constraints from user on {v_name}'
    
    m.write('Coarse-Grained-Floorplan.lp')

    m.optimize(max_seconds=self.max_search_time)

    # create new mapping
    next_s2v = defaultdict(list)
    next_v2s = {}

    # map from slot to sub-slot
    for s, v_group in curr_s2v.items():
      bottom_or_left, up_or_right = s.partitionByHalf(dir)
      for v_name in v_group:
        if mods_x[v_name].x == 0:
          next_s2v[bottom_or_left].append(v_name)
          next_v2s[v_name] = bottom_or_left
        elif mods_x[v_name].x == 1:
          next_s2v[up_or_right].append(v_name)
          next_v2s[v_name] = up_or_right
        else:
          assert False

    return next_s2v, next_v2s

  # obtain the edges that are inside the given slots and the edges between the given slots and the other slots
  def classifyEdges(self, curr_s2v):
    intra_edges = []
    interface_edges = []

    first_visited_edges = set()
    for v_group in curr_s2v.values():
      for v in v_group:
        for e_name in v.getEdgeNames():
          if e_name in first_visited_edges:
            intra_edges.append(e_name)
            first_visited_edges.remove(e_name)
          else:
            first_visited_edges.add(e_name)

    interface_edges = list(first_visited_edges)

    return intra_edges, interface_edges
     