from collections import defaultdict
from typing import Dict
from autoparallel.FE.Slot import Slot
import re

class SlotManager:
  def __init__(self, board):
    self.board = board
    self.pblock_to_slot = {}

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
      return f'CLOCKREGION_X{left_bottom_x}Y{left_bottom_y} : CLOCKREGION_X{right_up_x}Y{right_up_y}'

    if 'COARSE' in pblock:
      return __convertCoarseRegionToClockRegion(pblock)
    else:
      match = re.search(r'^CLOCKREGION_X(\d+)Y(\d+)[ ]*:[ ]*CLOCKREGION_X(\d+)Y(\d+)$', pblock)
      assert match, f'incorrect pblock {pblock}'
      return pblock

  def getSlot(self, pblock : str):
    pblock = self.__preprocessPblock(pblock)
    if pblock not in self.pblock_to_slot:
      self.pblock_to_slot[pblock] = Slot(self.board, pblock)
    return self.pblock_to_slot[pblock]

  # split by the middle row
  def getBottomAndUpSplit(self, slot):
    up     = self.getSlot(slot.getUpChildSlotName())
    bottom = self.getSlot(slot.getBottomChildSlotName())

    return bottom, up 

  # split by the middle column
  def getLeftAndRightSplit(self, slot):
    left =  self.getSlot(slot.getLeftChildSlotName())
    right = self.getSlot(slot.getRightChildSlotname())

    return left, right

  def partitionSlotByHalf(self, slot : Slot, dir : str):
    if dir == 'HORIZONTAL':
      return self.getBottomAndUpSplit(slot)
    elif dir == 'VERTICAL':
      return self.getLeftAndRightSplit(slot)
    else:
      assert False, f'unrecognized partition direction: {dir}'

  def getInitialSlot(self):
    return self.getSlot(f'CLOCKREGION_X0Y0:CLOCKREGION_X{self.board.CR_NUM_HORIZONTAL-1}Y{self.board.CR_NUM_VERTICAL-1}')
