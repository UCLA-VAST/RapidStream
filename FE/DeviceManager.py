from collections import defaultdict
import copy

# TODO: calibrate resource when DDRs are enabled
class DeviceU250:

  # SLR level
  SLR_NUM = 4

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
  def getLagunaPositionY():
    return [3, 4, 7, 8, 11, 12]

  CR_NUM_HORIZONTAL = 8  
  CR_NUM_VERTICAL = 16  
  CR_NUM_VERTICAL_PER_SLR = 4 # each die has 4 CRs vertically

  # Clock Region level
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

  # CR_AREA[7]['BRAM'] = 48
  # CR_AREA[7]['DSP'] = 48
  # CR_AREA[7]['FF'] = 24000
  # CR_AREA[7]['LUT'] = 12000
  # CR_AREA[7]['URAM'] = 0

  # consumed by Vitis IP
  CR_AREA[7]['BRAM'] = 0
  CR_AREA[7]['DSP'] = 0
  CR_AREA[7]['FF'] = 0
  CR_AREA[7]['LUT'] = 0
  CR_AREA[7]['URAM'] = 0

  TOTAL_AREA = {}
  TOTAL_AREA['BRAM'] = 5376
  TOTAL_AREA['DSP'] = 12288
  TOTAL_AREA['FF'] = 3456000
  TOTAL_AREA['LUT'] = 1728000
  TOTAL_AREA['URAM'] = 1280
  
class DeviceU280:
  SLR_NUM = 3
  
  SLR_AREA = defaultdict(lambda: defaultdict(list))
  SLR_AREA['BRAM'][0] = 768
  SLR_AREA['DSP'][0] = 1536
  SLR_AREA['FF'][0] = 433920
  SLR_AREA['LUT'][0] = 216960  
  
  SLR_AREA['BRAM'][1] = 384
  SLR_AREA['DSP'][1] = 1344
  SLR_AREA['FF'][1] = 330240
  SLR_AREA['LUT'][1] = 165120  

  LAGUNA_PER_CR = 480
  def getLagunaPositionY():
    return [3, 4, 7, 8, 11, 12]

  CR_NUM_HORIZONTAL = 8
  CR_NUM_VERTICAL = 16
  CR_NUM_VERTICAL_PER_SLR = 4 # each die has 4 CRs vertically

  TOTAL_AREA = {}
  TOTAL_AREA['BRAM'] = 4032
  TOTAL_AREA['DSP'] = 9024
  TOTAL_AREA['FF'] = 2607360
  TOTAL_AREA['LUT'] = 1303680
  TOTAL_AREA['URAM'] = 960

  # Clock Region level
  CR_AREA = [defaultdict(defaultdict) for i in range(CR_NUM_HORIZONTAL)]
  CR_AREA[0]['BRAM'] = 48
  CR_AREA[0]['DSP']  = 72
  CR_AREA[0]['FF']   = 29760
  CR_AREA[0]['LUT']  = 14880
  CR_AREA[0]['URAM'] = 0

  CR_AREA[1]['BRAM'] = 48
  CR_AREA[1]['DSP']  = 72
  CR_AREA[1]['FF']   = 24960
  CR_AREA[1]['LUT']  = 12480
  CR_AREA[1]['URAM'] = 16

  CR_AREA[2]['BRAM'] = 72
  CR_AREA[2]['DSP']  = 90
  CR_AREA[2]['FF']   = 36480
  CR_AREA[2]['LUT']  = 18240
  CR_AREA[2]['URAM'] = 0

  CR_AREA[3]['BRAM'] = 24
  CR_AREA[3]['DSP']  = 54
  CR_AREA[3]['FF']   = 21120
  CR_AREA[3]['LUT']  = 10560
  CR_AREA[3]['URAM'] = 16

  CR_AREA[4]['BRAM'] = 48
  CR_AREA[4]['DSP']  = 72
  CR_AREA[4]['FF']   = 27840
  CR_AREA[4]['LUT']  = 13920
  CR_AREA[4]['URAM'] = 16

  CR_AREA[5]['BRAM'] = 24
  CR_AREA[5]['DSP']  = 90
  CR_AREA[5]['FF']   = 28800
  CR_AREA[5]['LUT']  = 14400
  CR_AREA[5]['URAM'] = 16

  CR_AREA[6]['BRAM'] = 24
  CR_AREA[6]['DSP']  = 90
  CR_AREA[6]['FF']   = 28800
  CR_AREA[6]['LUT']  = 14400
  CR_AREA[6]['URAM'] = 16

  # CR_AREA[7]['BRAM'] = 48
  # CR_AREA[7]['DSP']  = 36
  # CR_AREA[7]['FF']   = 25920
  # CR_AREA[7]['LUT']  = 12960
  # CR_AREA[7]['URAM'] = 0

  # consumed by Vitis IP
  CR_AREA[7]['BRAM'] = 0
  CR_AREA[7]['DSP']  = 0
  CR_AREA[7]['FF']   = 0
  CR_AREA[7]['LUT']  = 0
  CR_AREA[7]['URAM'] = 0

class DeviceManager:
  def __init__(self, board_name):
    if board_name == 'U250':
      self.board = DeviceU250
    elif board_name == 'U280':
      self.board = DeviceU280
    else:
      assert False, f'unsupported device: {board_name}'

  def getBoard(self):
    return self.board