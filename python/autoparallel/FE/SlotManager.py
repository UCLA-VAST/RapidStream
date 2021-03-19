from collections import defaultdict
from typing import Dict
from autoparallel.FE.Slot import Slot
import re

class SlotManager:
  def __init__(self, board):
    self.board = board
    self.pblock_to_slot = {}
    self.pblock_to_routing_slot = {}

  def __preprocessPblock(self, pblock : str) -> str:
    def __convertCoarseRegionToClockRegion(coarse_loc):
      match = re.search(r'COARSE_X(\d+)Y(\d+)', coarse_loc)
      assert match

      x = int(match.group(1))
      y = int(match.group(2))
      CR_NUM_HORIZONTAL_PER_COARSE = int(0.5 * self.board.CR_NUM_HORIZONTAL)
      CR_NUM_VERTICAL_PER_COARSE = int(self.board.CR_NUM_VERTICAL_PER_SLR)

      left_bottom_x = x * CR_NUM_HORIZONTAL_PER_COARSE
      left_bottom_y = y * CR_NUM_VERTICAL_PER_COARSE
      right_up_x = left_bottom_x + CR_NUM_HORIZONTAL_PER_COARSE - 1
      right_up_y = left_bottom_y + CR_NUM_VERTICAL_PER_COARSE - 1
      return f'CLOCKREGION_X{left_bottom_x}Y{left_bottom_y}:CLOCKREGION_X{right_up_x}Y{right_up_y}'

    if 'COARSE' in pblock:
      return __convertCoarseRegionToClockRegion(pblock)
    else:
      match = re.search(r'^CLOCKREGION_X(\d+)Y(\d+)[ ]*:[ ]*CLOCKREGION_X(\d+)Y(\d+)$', pblock)
      assert match, f'incorrect pblock {pblock}'
      return pblock

  def createSlotForRouting(self, pblock : str):
    """create a Slot object for global routing purpose"""
    pblock = self.__preprocessPblock(pblock)
    if pblock not in self.pblock_to_routing_slot:
      self.pblock_to_routing_slot[pblock] = Slot(self.board, pblock)
    return self.pblock_to_routing_slot[pblock]

  def createSlot(self, pblock : str):
    """create a Slot for floorplanning purpose and track the existing Slot objects"""
    pblock = self.__preprocessPblock(pblock)
    if pblock not in self.pblock_to_slot:
      self.pblock_to_slot[pblock] = Slot(self.board, pblock)
    return self.pblock_to_slot[pblock]

  def getPureRoutingSlots(self):
    return [self.pblock_to_routing_slot[pblock] \
        for pblock in self.pblock_to_routing_slot.keys() \
        if pblock not in self.pblock_to_slot]

  def getComputeSlots(self):
    return self.pblock_to_slot.values()

  def removeSlotNonBlocking(self, pblock : str):
    if pblock in self.pblock_to_slot:
      self.pblock_to_slot.pop(pblock)

  # split by the middle row
  def getBottomAndUpSplit(self, slot):
    up     = self.createSlot(slot.getUpChildSlotName())
    bottom = self.createSlot(slot.getBottomChildSlotName())
    self.removeSlotNonBlocking(slot.getName())

    return bottom, up 

  # split by the middle column
  def getLeftAndRightSplit(self, slot):
    left =  self.createSlot(slot.getLeftChildSlotName())
    right = self.createSlot(slot.getRightChildSlotname())
    self.removeSlotNonBlocking(slot.getName())

    return left, right

  def partitionSlotByHalf(self, slot : Slot, dir : str):
    if dir == 'HORIZONTAL':
      return self.getBottomAndUpSplit(slot)
    elif dir == 'VERTICAL':
      return self.getLeftAndRightSplit(slot)
    else:
      assert False, f'unrecognized partition direction: {dir}'

  def getInitialSlot(self):
    return self.createSlot(f'CLOCKREGION_X0Y0:CLOCKREGION_X{self.board.CR_NUM_HORIZONTAL-1}Y{self.board.CR_NUM_VERTICAL-1}')

  def __haveOverlappedYRange(self, a : Slot, b : Slot):
    return min(a.getOrigUpRightY(), b.getOrigUpRightY()) > max(a.getOrigDownLeftY(), b.getOrigDownLeftY())
  
  def __haveOverlappedXRange(self, a : Slot, b : Slot):
    return min(a.getOrigUpRightX(), b.getOrigUpRightX()) > max(a.getOrigDownLeftX(), b.getOrigDownLeftX())
  
  def getLeftNeighborSlots(self, slot, potential_target_slots):
    neighbors = []
    for candidate in potential_target_slots.values():
      if candidate.getOrigUpRightX()+1 == slot.getOrigDownLeftX():
        if self.__haveOverlappedYRange(candidate, slot):
          neighbors.append(candidate)
    return neighbors
  
  def getRightNeighborSlots(self, slot, potential_target_slots):
    neighbors = []
    for candidate in potential_target_slots.values():
      if slot.getOrigUpRightX()+1 == candidate.getOrigDownLeftX():
        if self.__haveOverlappedYRange(candidate, slot):
          neighbors.append(candidate)
    return neighbors
  
  def getUpNeighborSlots(self, slot, potential_target_slots):
    neighbors = []
    for candidate in potential_target_slots.values():
      if slot.getOrigUpRightY()+1 == candidate.getOrigDownLeftY():
        if self.__haveOverlappedXRange(candidate, slot):
          neighbors.append(candidate)
    return neighbors
  
  def getDownNeighborSlots(self, slot, potential_target_slots):
    neighbors = []
    for candidate in potential_target_slots.values():
      if candidate.getOrigUpRightY()+1 == slot.getOrigDownLeftY():
        if self.__haveOverlappedXRange(candidate, slot):
          neighbors.append(candidate)
    return neighbors

  def getNeighborSlotsIncludeRouting(self, slot, dir):
    potential_target_slots = {**self.pblock_to_slot, **self.pblock_to_routing_slot}

    if dir == 'UP':
      return self.getUpNeighborSlots(slot, potential_target_slots)
    elif dir == 'DOWN':
      return self.getDownNeighborSlots(slot, potential_target_slots)
    elif dir == 'LEFT':
      return self.getLeftNeighborSlots(slot, potential_target_slots)
    elif dir == 'RIGHT':
      return self.getRightNeighborSlots(slot, potential_target_slots)
    else:
      assert False, f'wrong direction: {dir}'

  def getActiveSlotsIncludeRouting(self):
    return {**self.pblock_to_slot, **self.pblock_to_routing_slot}.values()

  def isPureRoutingSlot(self, slot):
    slot_name = slot.getName()
    return slot_name in self.pblock_to_routing_slot and slot_name not in self.pblock_to_slot

