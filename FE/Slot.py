#! /usr/bin/python3.6
import logging
from collections import defaultdict
from typing import Dict
import re

class Slot:
  def __init__(self, board, pblock : str):
    self.board = board

    if 'COARSE_' in pblock:
      pblock = self.__convertCoarseRegionToClockRegion(pblock)

    match = re.search(r'^CLOCKREGION_X(\d+)Y(\d+)[ ]*:[ ]*CLOCKREGION_X(\d+)Y(\d+)$', pblock)
    assert match, f'incorrect pblock {pblock}'

    # convert CR coordinate to boundary intersect coordinates
    self.down_left_x = int(match.group(1))
    self.down_left_y = int(match.group(2))
    self.up_right_x = int(int(match.group(3))+1)
    self.up_right_y = int(int(match.group(4))+1)

    self.area = {}
    self.__initArea()

  def __convertCoarseRegionToClockRegion(self, coarse_loc):
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

  def getName(self):
    # need to convert back to CR coordinates
    return f'CLOCKREGION_X{self.down_left_x}Y{self.down_left_y}:CLOCKREGION_X{self.up_right_x-1}Y{self.up_right_y-1}'

  def getRTLModuleName(self):
    return f'CR_X{self.down_left_x}Y{self.down_left_y}_2_CR_X{self.up_right_x-1}Y{self.up_right_y-1}'

  def __hash__(self):
    assert self.down_left_x < 100
    assert self.down_left_y < 100
    assert self.up_right_x < 100
    assert self.up_right_y < 100

    id =  str(self.down_left_x).zfill(3) + \
          str(self.down_left_y).zfill(3) + \
          str(self.up_right_x).zfill(3) + \
          str(self.up_right_y).zfill(3)
    logging.debug(f'Using customized hash function for Slot ({self.down_left_x}, {self.down_left_y}, {self.up_right_x}, {self.up_right_y}) with id {id}')

    return hash(id)

  # calculate the available resources of this slot
  def __initArea(self):
    for item in ['BRAM', 'DSP', 'FF', 'LUT', 'URAM']:
      self.area[item] = 0
      for i in range(self.down_left_x, self.up_right_x):
        self.area[item] += self.board.CR_AREA[i][item]
      
      # vertically the CRs are the same
      self.area[item] *= (self.up_right_y - self.down_left_y)
    
    self.area['LAGUNA'] = 0
    for i in self.board.getLagunaPositionY():
      if self.down_left_y <= i <= self.up_right_y:
        self.area['LAGUNA'] += self.board.LAGUNA_PER_CR

  def getArea(self):
    return self.area
  
  # use the middle point as the position of the slot. Check the results have no fractional part
  def getPositionX(self):
    return int((self.down_left_x + self.up_right_x) / 2) 

  def getPositionY(self):
    return int((self.down_left_y + self.up_right_y) / 2) 
  
  # 1/4 from the lower end
  def getQuarterPositionX(self):
    return int(self.down_left_x + (self.up_right_x - self.down_left_x) / 4) 

  def getQuarterPositionY(self):
    return int(self.down_left_y + (self.up_right_y - self.down_left_y) / 4) 

  # since we are using the boundary intersect coordinates, we do not need +1
  def getHalfLenX(self):
    return int((self.up_right_x - self.down_left_x) / 2) 

  def getHalfLenY(self):
    return int((self.up_right_y - self.down_left_y) / 2) 

  # split by the middle row
  def getBottomAndUpSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'

    #                  |-------| u_r_x, u_r_y
    #                  |       |
    #                  |  up   |
    #                  |       |
    #                  |-------| u_r_x, mid_y   
    #                  |       |
    #                  |  bot  |
    #                  |       |
    #   d_l_x, d_l_y   |-------|
    def getBottomChildSlotName():
      down_left_cr = f'CLOCKREGION_X{self.down_left_x }Y{self.down_left_y}'
      up_right_cr  = f'CLOCKREGION_X{self.up_right_x-1}Y{mid_y-1}'
      return f'{down_left_cr}:{up_right_cr}'
    
    def getUpChildSlotName():
      down_left_cr = f'CLOCKREGION_X{self.down_left_x }Y{mid_y}'
      up_right_cr  = f'CLOCKREGION_X{self.up_right_x-1}Y{self.up_right_y-1}'
      return f'{down_left_cr}:{up_right_cr}'

    mid_y = self.getPositionY()
    up     = Slot(self.board,  getUpChildSlotName())
    bottom = Slot(self.board,  getBottomChildSlotName())

    logging.debug(f'Horizontal Partition: from {self.getName()} to {up.getName()} and {bottom.getName()}')
    return bottom, up 

  # split by the middle column
  def getLeftAndRightSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'

    #                  mid_x, u_r_y
    #               |---------|---------| u_r_x, u_r_y
    #               |         |         |
    #               |  L      |      R  |
    #               |         |         |
    #  d_l_x, d_l_y |---------|---------|
    #                    mid_x, d_l_y
    #     
    def getLeftChildSlotName():
      down_left_cr = f'CLOCKREGION_X{self.down_left_x}Y{self.down_left_y}'
      up_right_cr  = f'CLOCKREGION_X{mid_x - 1       }Y{self.up_right_y-1}'
      return f'{down_left_cr}:{up_right_cr}'

    def getRightChildSlotname():
      down_left_cr = f'CLOCKREGION_X{mid_x            }Y{self.down_left_y}'
      up_right_cr  = f'CLOCKREGION_X{self.up_right_x-1}Y{self.up_right_y-1}'
      return f'{down_left_cr}:{up_right_cr}'

    mid_x = self.getPositionX()
    left =  Slot(self.board, getLeftChildSlotName())
    right = Slot(self.board, getRightChildSlotname())

    logging.debug(f'Vertical Partition: from {self.getName()} to {left.getName()} and {right.getName()}')

    return left, right

  def partitionByHalf(self, dir : str):
    if dir == 'HORIZONTAL':
      return self.getBottomAndUpSplit()
    elif dir == 'VERTICAL':
      return self.getLeftAndRightSplit()
    else:
      assert False, f'unrecognized partition direction: {dir}'

  def containsChildSlot(self, target) -> bool:
    return target.down_left_x >= self.down_left_x \
      and  target.down_left_y >= self.down_left_y \
      and  target.up_right_x  <= self.up_right_x  \
      and  target.up_right_y  <= self.up_right_y  