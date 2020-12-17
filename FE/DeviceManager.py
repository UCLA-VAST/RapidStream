from collections import defaultdict

class DeviceU250:

  # SLR level
  SLR_CNT = 4
  NUM_PER_SLR_HORIZONTAL = 4

  SLR_AREA = defaultdict(lambda: defaultdict(list))
  SLR_AREA['BRAM'][0] = 768
  SLR_AREA['DSP'][0] = 1536
  SLR_AREA['FF'][0] = 433920
  SLR_AREA['LUT'][0] = 216960

  SLR_AREA['BRAM'][1] = 384
  SLR_AREA['DSP'][1] = 1344
  SLR_AREA['FF'][1] = 329280
  SLR_AREA['LUT'][1] = 164640

  SLR_AREA_DDR = defaultdict(lambda: defaultdict(list))
  SLR_AREA_DDR['BRAM'][0] = 768
  SLR_AREA_DDR['DSP'][0] = 1536
  SLR_AREA_DDR['FF'][0] = 433920
  SLR_AREA_DDR['LUT'][0] = 216960

  SLR_AREA_DDR['BRAM'][1] = 288
  SLR_AREA_DDR['DSP'][1] = 1152
  SLR_AREA_DDR['FF'][1] = 245760
  SLR_AREA_DDR['LUT'][1] = 122800

  LAGUNA_PER_CR = 480

  # Clock Region level
  CR_NUM_HORIZONTAL = 8  
  CR_AREA = [defaultdict(defaultdict) for i in range(CR_NUM_HORIZONTAL)]
  CR_AREA[0]['BRAM'] = 48
  CR_AREA[0]['DSP'] = 96
  CR_AREA[0]['FF'] = 27840
  CR_AREA[0]['LUT'] = 13920
  CR_AREA[0]['URAM'] = 0

  CR_AREA[1]['BRAM'] = 48
  CR_AREA[1]['DSP'] = 96
  CR_AREA[1]['FF'] = 23040
  CR_AREA[1]['LUT'] = 11520
  CR_AREA[1]['URAM'] = 16

  CR_AREA[2]['BRAM'] = 72
  CR_AREA[2]['DSP'] = 120
  CR_AREA[2]['FF'] = 34560
  CR_AREA[2]['LUT'] = 17280
  CR_AREA[2]['URAM'] = 0

  CR_AREA[3]['BRAM'] = 24
  CR_AREA[3]['DSP'] = 72
  CR_AREA[3]['FF'] = 19200
  CR_AREA[3]['LUT'] = 9600
  CR_AREA[3]['URAM'] = 16

  CR_AREA[4]['BRAM'] = 48
  CR_AREA[4]['DSP'] = 96
  CR_AREA[4]['FF'] = 25920
  CR_AREA[4]['LUT'] = 12960
  CR_AREA[4]['URAM'] = 16

  CR_AREA[5]['BRAM'] = 24
  CR_AREA[5]['DSP'] = 120
  CR_AREA[5]['FF'] = 26880
  CR_AREA[5]['LUT'] = 13440
  CR_AREA[5]['URAM'] = 16

  CR_AREA[6]['BRAM'] = 24
  CR_AREA[6]['DSP'] = 120
  CR_AREA[6]['FF'] = 26880
  CR_AREA[6]['LUT'] = 13440
  CR_AREA[6]['URAM'] = 16

  CR_AREA[7]['BRAM'] = 48
  CR_AREA[7]['DSP'] = 48
  CR_AREA[7]['FF'] = 24000
  CR_AREA[7]['LUT'] = 12000
  CR_AREA[7]['URAM'] = 0

class DeviceU280:
  SLR_CNT = 3
  NUM_PER_SLR_HORIZONTAL = 4
  
  SLR_AREA = defaultdict(lambda: defaultdict(list))
  SLR_AREA['BRAM'][0] = 768
  SLR_AREA['DSP'][0] = 1536
  SLR_AREA['FF'][0] = 433920
  SLR_AREA['LUT'][0] = 216960  
  
  SLR_AREA['BRAM'][1] = 384
  SLR_AREA['DSP'][1] = 1344
  SLR_AREA['FF'][1] = 330240
  SLR_AREA['LUT'][1] = 165120  

class Slot:
  def __init__(self, board, down_left_x, down_left_y, up_right_x, up_right_y):
    self.board = board

    self.down_left_x = down_left_x
    self.down_left_y = down_left_y
    self.up_right_x = up_right_x
    self.up_right_y = up_right_y
    
    self.area = {}
    self.initArea()

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
  
  def getPositionX(self):
    return (self.down_left_x + self.up_right_x) / 2

  def getPositionY(self):
    return (self.down_left_y + self.up_right_y) / 2

  def getUpperAndLowerSplit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'
    mid_y = int(self.down_left_y + self.up_right_y) / 2

    upper = Slot(self.board, self.down_left_x, mid_y,            self.up_right_x, self.up_right_y)
    lower = Slot(self.board, self.down_left_x, self.down_left_y, self.up_right_x, mid_y)

    return upper, lower

  def getLeftAndRightSlit(self):
    assert self.down_left_x != self.up_right_x or \
      self.down_left_y != self.up_right_y, 'Cannot split a single CR'
    mid_x = int(self.down_left_x + self.up_right_x) / 2

    left =  Slot(self.board, self.down_left_x, self.down_left_y, mid_x,           self.up_right_y)
    right = Slot(self.board, mid_x,            self.down_left_y, self.up_right_x, self.up_right_y)

    return left, right