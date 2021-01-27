from collections import defaultdict
import re

# TODO: calibrate resource when DDRs are enabled
class DeviceU250:

  FPGA_PART_NAME = 'xcu250-figd2104-2L-e'
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
  
  @staticmethod
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
  
  @staticmethod
  def shrinkClockRegionPblock(pblock_def : str) :
    assert re.search(r'CLOCKREGION_X\d+Y\d+:CLOCKREGION_X\d+Y\d+', pblock_def), f'unexpected format of the pblock {pblock_def}'
    DL_x, DL_y, UR_x, UR_y = [int(val) for val in re.findall(r'[XY](\d+)', pblock_def)] # DownLeft & UpRight

    assert DL_x+1 == UR_x and DL_y+1 == UR_y, f'currently only supports translation of 4-CR pblocks'
    
    SLICE_height = 120
    DSP48E2_height = 48
    LAGUNA_height = 120
    RAMB18_height = 48
    RAMB36_height = 24
    URAM288_height = 32
    
    pblock_DL_y = int(DL_y/2)
    pblock_UR_y = int(UR_y/2)

    if DL_x == 0:
      return f'''
        SLICE_X2Y{4 + pblock_DL_y * SLICE_height}:SLICE_X56Y{115 + pblock_UR_y * SLICE_height} 
        DSP48E2_X0Y{2 + pblock_DL_y * DSP48E2_height}:DSP48E2_X7Y{45 + pblock_UR_y * DSP48E2_height} 
        LAGUNA_X0Y{8 + pblock_DL_y * LAGUNA_height}:LAGUNA_X7Y{117 + pblock_UR_y * LAGUNA_height} 
        RAMB18_X0Y{2 + pblock_DL_y * RAMB18_height}:RAMB18_X3Y{45 + pblock_UR_y * RAMB18_height} 
        RAMB36_X0Y{1 + pblock_DL_y * RAMB36_height}:RAMB36_X3Y{22 + pblock_UR_y * RAMB36_height} 
        URAM288_X0Y{4 + pblock_DL_y * URAM288_height}:URAM288_X0Y{27 + pblock_UR_y * URAM288_height} '''
    elif DL_x == 2:
      return f'''
        SLICE_X59Y{4 + pblock_DL_y * SLICE_height}:SLICE_X114Y{115 + pblock_UR_y * SLICE_height} 
        DSP48E2_X8Y{2 + pblock_DL_y * DSP48E2_height}:DSP48E2_X15Y{45 + pblock_UR_y * DSP48E2_height} 
        LAGUNA_X8Y{8 + pblock_DL_y * LAGUNA_height}:LAGUNA_X15Y{117 + pblock_UR_y * LAGUNA_height} 
        RAMB18_X4Y{2 + pblock_DL_y * RAMB18_height}:RAMB18_X7Y{45 + pblock_UR_y * RAMB18_height} 
        RAMB36_X4Y{1 + pblock_DL_y * RAMB36_height}:RAMB36_X7Y{22 + pblock_UR_y * RAMB36_height} 
        URAM288_X1Y{4 + pblock_DL_y * URAM288_height}:URAM288_X1Y{27 + pblock_UR_y * URAM288_height}
      '''
    elif DL_x == 4:
      return f'''
        SLICE_X119Y{4 + pblock_DL_y * SLICE_height}:SLICE_X175Y{115 + pblock_UR_y * SLICE_height} 
        DSP48E2_X16Y{2 + pblock_DL_y * DSP48E2_height}:DSP48E2_X24Y{45 + pblock_UR_y * DSP48E2_height} 
        LAGUNA_X16Y{8 + pblock_DL_y * LAGUNA_height}:LAGUNA_X23Y{117 + pblock_UR_y * LAGUNA_height} 
        RAMB18_X8Y{2 + pblock_DL_y * RAMB18_height}:RAMB18_X10Y{45 + pblock_UR_y * RAMB18_height} 
        RAMB36_X8Y{1 + pblock_DL_y * RAMB36_height}:RAMB36_X10Y{22 + pblock_UR_y * RAMB36_height} 
        URAM288_X2Y{4 + pblock_DL_y * URAM288_height}:URAM288_X3Y{27 + pblock_UR_y * URAM288_height}
      '''
    elif DL_x == 6:
      return f'''
        SLICE_X178Y{4 + pblock_DL_y * SLICE_height}:SLICE_X230Y{115 + pblock_UR_y * SLICE_height} 
        DSP48E2_X25Y{2 + pblock_DL_y * DSP48E2_height}:DSP48E2_X31Y{45 + pblock_UR_y * DSP48E2_height} 
        LAGUNA_X24Y{8 + pblock_DL_y * LAGUNA_height}:LAGUNA_X31Y{117 + pblock_UR_y * LAGUNA_height} 
        RAMB18_X11Y{2 + pblock_DL_y * RAMB18_height}:RAMB18_X13Y{45 + pblock_UR_y * RAMB18_height} 
        RAMB36_X11Y{1 + pblock_DL_y * RAMB36_height}:RAMB36_X13Y{22 + pblock_UR_y * RAMB36_height} 
        URAM288_X4Y{4 + pblock_DL_y * URAM288_height}:URAM288_X4Y{27 + pblock_UR_y * URAM288_height}      
      '''

  """
    resize_pblock pblock_1 -add {
      SLICE_X2Y4:SLICE_X56Y115 
      DSP48E2_X0Y2:DSP48E2_X7Y45 
      LAGUNA_X0Y8:LAGUNA_X7Y119 
      RAMB18_X0Y2:RAMB18_X3Y45 
      RAMB36_X0Y1:RAMB36_X3Y22 
      URAM288_X0Y4:URAM288_X0Y27
    } 
    resize_pblock pblock_2 -add {
      SLICE_X59Y4:SLICE_X114Y115 
      DSP48E2_X8Y2:DSP48E2_X15Y45 
      LAGUNA_X8Y8:LAGUNA_X15Y119 
      RAMB18_X4Y2:RAMB18_X7Y45 
      RAMB36_X4Y1:RAMB36_X7Y22 
      URAM288_X1Y4:URAM288_X1Y27
    }
    resize_pblock pblock_3 -add {
      SLICE_X119Y4:SLICE_X175Y115 
      DSP48E2_X16Y2:DSP48E2_X24Y45 
      LAGUNA_X16Y8:LAGUNA_X23Y119 
      RAMB18_X8Y2:RAMB18_X10Y45 
      RAMB36_X8Y1:RAMB36_X10Y22 
      URAM288_X2Y4:URAM288_X3Y27
    } 
    resize_pblock pblock_4 -add {
      SLICE_X178Y4:SLICE_X230Y115 
      DSP48E2_X25Y2:DSP48E2_X31Y45 
      LAGUNA_X24Y8:LAGUNA_X31Y119 
      RAMB18_X11Y2:RAMB18_X13Y45 
      RAMB36_X11Y1:RAMB36_X13Y22 
      URAM288_X4Y4:URAM288_X4Y27
    }
  """

class DeviceU280:
  FPGA_PART_NAME = 'xcu280-fsvh2892-2L-e'

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
  
  @staticmethod
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