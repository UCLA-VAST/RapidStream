import re
from autobridge.Opt.Slot import Slot
from autobridge.Device.DeviceManager import DeviceU250

U250_inst = DeviceU250()

def getAllLagunaRange():
  return 'LAGUNA_X0Y0:LAGUNA_X31Y839'


def __getBufferRegionOfSLRCrossingSlotPair(slot1, slot2):
  assert slot1.down_left_x == slot2.down_left_x
  assert slot1.up_right_x == slot2.up_right_x

  laguna_num_per_CR = 4
  laguna_down_left_x = slot1.down_left_x * laguna_num_per_CR
  laguna_up_right_x = (slot1.up_right_x + 1) * laguna_num_per_CR - 1

  from_slr = min(slot1.getSLR(), slot2.getSLR())
  to_slr = max(slot1.getSLR(), slot2.getSLR())

  if from_slr == 0 and to_slr == 1:
    laguna_down_left_y = 120
    laguna_up_right_y = 359
    slice_down_left_y = 180
    slice_up_right_y = 299
  elif from_slr == 1 and to_slr == 2:
    laguna_down_left_y = 360
    laguna_up_right_y = 599
    slice_down_left_y = 420
    slice_up_right_y = 539
  elif from_slr == 2 and to_slr == 3:
    laguna_down_left_y = 600
    laguna_up_right_y = 839
    slice_down_left_y = 660
    slice_up_right_y = 779
  else:
    assert False

  laguna_region = f' LAGUNA_X{laguna_down_left_x}Y{laguna_down_left_y}:LAGUNA_X{laguna_up_right_x}Y{laguna_up_right_y} '
  slice_around_laguna = __getSliceAroundLagunaSides(
      laguna_down_left_x=laguna_down_left_x, 
      laguna_up_right_x=laguna_up_right_x, 
      slice_down_left_y=slice_down_left_y,
      slice_up_right_y=slice_up_right_y)

  return laguna_region + '\n' + slice_around_laguna

# X index of the SLICE column to the left of the i-th Laguna column
idx_of_left_side_slice_of_laguna_column = (
    7,
    18,
    36,
    49,
    62,
    84,
    96,
    110,
    123,
    138,
    151,
    163,
    181,
    193,
    213,
    224
)

# Y index of the range of SLICEs besides Lagunas
y_idx_of_slice_besides_laguna = (
    (180, 299),
    (420, 539),
    (660, 779)
)

# record the X coordinates of the SLICE to the left of the BRAM column
x_of_left_slice_of_bram_u250 = [
  9, 14, 32, 54,
  58, 89, 92, 112,
  119, 143, 147, 177,
  218, 223
]

    # record the X coordinates of the SLICE to the left of the DSP column
x_of_left_slice_of_dsp_u250 = [
  1, 16, 27, 30,
  34, 41, 52, 56,
  60, 71, 76, 87,
  94, 99, 106, 114,
  121, 128, 141, 145,
  149, 156, 161, 166,
  175, 179, 186, 191,
  196, 205, 216, 229
]

# assume each DSP and BRAM takes 1 unit of width
num_SLICE_column = 233
calibrated_x_pos_of_slice = [
  i + \
  sum(x < i for x in x_of_left_slice_of_bram_u250) + \
  sum(x < i for x in x_of_left_slice_of_dsp_u250) \
    for i in range(num_SLICE_column)]

# map from calibrated x -> orig x
orig_x_pos_of_slice = {calibrated_x_pos_of_slice[i] : i \
                            for i in range(num_SLICE_column)}

calibrated_x_pos_of_bram = [
  calibrated_x_pos_of_slice[i] + 1 \
    for i in x_of_left_slice_of_bram_u250
]

calibrated_x_pos_of_dsp = [
    calibrated_x_pos_of_slice[i] + 1 \
    for i in x_of_left_slice_of_dsp_u250
]

def getSLICEYFromLagunaY(laguna_y: int) -> int:
  """
  get the y of the slice in the same row as the laguna
  """
  if 120 <= laguna_y <= 359:
    slice_y = (laguna_y-120) / 2 + 180
  elif 360 <= laguna_y <= 599:
    slice_y = (laguna_y-360) / 2 + 420
  elif 600 <= laguna_y <= 839:
    slice_y = (laguna_y -600) / 2 + 660
  else:
    assert False
  
  return int(slice_y)

# note that one column of slice corresponds to 2 columns of laguna
# thus we have the j dimension
calibrated_x_pos_of_laguna = [
  x for x in idx_of_left_side_slice_of_laguna_column \
      for j in range(2)
]

def getSliceOrigXCoordinates(calibrated_x):
  return orig_x_pos_of_slice[calibrated_x]

def getCalibratedCoordinatesFromSiteName(site_name):
  type, orig_x, orig_y = re.findall(r'(.*)_X(\d+)Y(\d+)', site_name)[0]
  orig_x, orig_y = map(int, (orig_x, orig_y))
  return getCalibratedCoordinates(type, orig_x, orig_y)

def getCalibratedCoordinates(type, orig_x, orig_y):
  if type == 'SLICE':
    return (calibrated_x_pos_of_slice[orig_x], orig_y)
  elif type == 'DSP48E2':
    # each DSP is 2.5X the height of a SLICE
    return (calibrated_x_pos_of_dsp[orig_x], orig_y * 2.5)
  elif type == 'RAMB36':
    # each RAMB36 is 5X the height
    return (calibrated_x_pos_of_bram[orig_x], orig_y * 5)
  elif type == 'RAMB18':
    # each RAMB18 is 2.5X the height of a SLICE
    return (calibrated_x_pos_of_bram[orig_x], orig_y * 2.5)
  elif type == 'LAGUNA':
    x = calibrated_x_pos_of_laguna[orig_x]
    y = getSLICEYFromLagunaY(orig_y)
    return (x, y)
  else:
    assert False, f'unsupported type {type}'


def __getSliceAroundLagunaSides(
    laguna_down_left_x, 
    laguna_up_right_x, 
    slice_down_left_y,
    slice_up_right_y):
  # note that each laguna column actually spans 2 in X dimension.
  # e.g. LAGUNA_X0Y... and LAGUNA_X1Y... are in the same physical column
  start_from_ith_laguna_column = int((laguna_down_left_x+1) / 2) # round to floor
  end_at_jth_laguna_column = int((laguna_up_right_x+1) / 2)

  SLICE_around_laguna = []

  # note that there is no +1
  # the last laguna column is X31 -> (31+1)/2 = 16 -> the last index should be 15
  for i in range(start_from_ith_laguna_column, end_at_jth_laguna_column): 
    # two columns of SLICEs to the left and to the right of the laguna columns
    # note that the index of SLICE jumps 1 because of the laguna column, so it should be +2 here
    # although only 2 columns of SLICEs are included
    #
    # UPDATE: seems that the right SLICE column is not suitable to connect to the laguna sites
    # try using two columns to the left
    #
    # UPDATE 06-06-21: the SLICE to the right share the same switch box to the laguna registers
    # Use the right column may minimize the anchor routes that spill out into the slot region
    # Also, one SLICE column is enough to cover all SLL connections. Each laguna column contains 720 wires
    # one SLICE column with a height of 120 has 120 * 16 = 1920 registers, far more than enough to cover the maximal 720 connections
    
    # ************** FIXME: this part must sync with getAllLagunaBufferRegions() ********************
    idx_SLICE_to_the_left = idx_of_left_side_slice_of_laguna_column[i]
    idx_hidden_SLICE = idx_SLICE_to_the_left + 1
    idx_SLICE_to_the_right = idx_hidden_SLICE + 1
    # ***********************************************************************************************

    # note that the Y coordinate of laguna and SLICE is NOT the same
    # select the SLICE column to the right of the laguna column.
    SLICE_around_laguna.append(f'SLICE_X{idx_SLICE_to_the_right}Y{slice_down_left_y}:SLICE_X{idx_SLICE_to_the_right}Y{slice_up_right_y}')
  return '\n'.join(SLICE_around_laguna)


def getBufferRegionBetweenSlotPair(slot_name1, slot_name2, col_width_each_side, row_width_each_side):
  """
  Given a pair of neighbor slots, return the tight buffer region in between
  to help constrain the anchor placement  
  For cross-SLR pairs, return the included laguna sites along with the neighbor SLICEs
  """

  idx_1st_col_CR_X = [0] * 9
  idx_1st_col_CR_X[0] = 0 # index of the first SLICE column in the 0-th CR column
  idx_1st_col_CR_X[1] = 31 # index of the first SLICE column in the 1-th CR column
  idx_1st_col_CR_X[2] = 57 # 2-th CR column
  idx_1st_col_CR_X[3] = 95 # 3-th CR column
  idx_1st_col_CR_X[4] = 117 # 4-th CR column
  idx_1st_col_CR_X[5] = 146 # 5-th CR column
  idx_1st_col_CR_X[6] = 176 # 6-th CR column    
  idx_1st_col_CR_X[7] = 206 # 7-th CR column    
  idx_1st_col_CR_X[8] = 233 # pseudo 8-th CR column. There are 232 columns in total 

  Slot_SLICE_height = 120 # 2x2 slot
  CR_SLICE_height = 60
  
  slot1 = Slot(U250_inst, slot_name1)
  slot2 = Slot(U250_inst, slot_name2)

  #******************************************
  # a hack to prevent routing conflicts between slots and anchors
  # see comment in __getBufferRegionSize()
  assert col_width_each_side == 4
  assert row_width_each_side == 5
  if (slot1.down_left_x == 4 and slot2.down_left_x == 6) or \
      (slot1.down_left_x == 6 and slot2.down_left_x == 4):
    col_width_each_side = 3
  #******************************************

  if slot1.isToTheLeftOf(slot2) or slot1.isToTheRightOf(slot2):
    orient = 'HORIZONTAL'
  elif slot1.isAbove(slot2) or slot1.isBelow(slot2):
    orient = 'VERTICAL'
  else:
    assert False

  if orient == 'HORIZONTAL':
    y_range_beg = slot1.down_left_y * CR_SLICE_height
    y_range_end = y_range_beg + Slot_SLICE_height - 1 # 2x2 slot
    
    # shrink buffer regions of horizontal pairs
    # to avoid the slight overlapping with the buffer regions of vertical pairs
    y_range_beg_delta = y_range_beg + row_width_each_side
    y_range_end_delta = y_range_end - row_width_each_side # 2x2 slot

    # the values are selected to avoid spliting a switchbox
    # sync with getAllBoundaryBufferRegions()
    if slot1.down_left_x + slot2.down_left_x == 2:
      x_range_beg = 56
      x_range_end = 58
    elif slot1.down_left_x + slot2.down_left_x == 6:
      x_range_beg = 115
      x_range_end = 117
    elif slot1.down_left_x + slot2.down_left_x == 10:
      x_range_beg = 175
      x_range_end = 177
    else:
      assert False

    return f'SLICE_X{x_range_beg}Y{y_range_beg_delta}:SLICE_X{x_range_end}Y{y_range_end_delta} '
  
  elif orient == 'VERTICAL':
    # the buffer region for cross-SLR vertical pairs should only include the buffer around laguna sites
    if slot1.getSLR() != slot2.getSLR():
      return __getBufferRegionOfSLRCrossingSlotPair(slot1, slot2)
      
    # non-slr-crossing pair
    x_range_beg = idx_1st_col_CR_X[slot1.down_left_x]
    x_range_end = idx_1st_col_CR_X[slot1.up_right_x+1] - 1
    mid_SLICE_row_idx = max(slot1.down_left_y, slot2.down_left_y) *  CR_SLICE_height
    y_range_beg = mid_SLICE_row_idx - row_width_each_side
    y_range_end = mid_SLICE_row_idx + row_width_each_side - 1
    slice_buffer_region = f'SLICE_X{x_range_beg}Y{y_range_beg}:SLICE_X{x_range_end}Y{y_range_end} '

    return slice_buffer_region

  else:
    assert False


def getAllLagunaBufferRegions(add_empty_space):
  """ 
  one column of SLICE to the right of all laguna columns 
  FIXME: this function must sync with __getSliceAroundLagunaSides()
  The laguna columns have similar effect as a boundary
  Thus we should leave some gap around the laguna columns in the placement stage
  This can help routing
  """
  slice_besides_laguna = []
  for x in idx_of_left_side_slice_of_laguna_column:
    for y_beg, y_end in y_idx_of_slice_besides_laguna:
      
      # slightly enlarge the buffer region. This can help create additional empty space to help routing
      if add_empty_space:
        y_beg -= 2
        y_end += 2

      # ******* sync with __getSliceAroundLagunaSides() ********
      x_slice_on_the_left = x
      x_hidden_slice = x + 1
      x_slice_on_the_right = x + 2
      slice_besides_laguna.append(f' SLICE_X{x_slice_on_the_left}Y{y_beg}:SLICE_X{x_slice_on_the_right}Y{y_end} ')
      # ********************************************************

  return '\n'.join(slice_besides_laguna)


def getAllBoundaryBufferRegions(col_width, row_width, is_for_placement: bool):
  """
  create a buffer region among 2x2 slots
  use the concise clockregion-based pblock subtract this buffer region
  """

  # for each slot, get the index of the first and the last SLICE column
  idx_1st_col_Slot_X = [0] * 4
  idx_last_col_Slot_X = [0] * 4

  idx_1st_col_Slot_X[0] = 0 # index of the first SLICE column in the 0-th CR column
  idx_1st_col_Slot_X[1] = 57 # 2-th CR column
  idx_1st_col_Slot_X[2] = 117 # 4-th CR column
  idx_1st_col_Slot_X[3] = 176 # 6-th CR column

  idx_last_col_Slot_X[3] = 232 # index of the last SLICE column in the 7-th CR column
  idx_last_col_Slot_X[2] = idx_1st_col_Slot_X[3] - 1 # 5-th CR column
  idx_last_col_Slot_X[1] = idx_1st_col_Slot_X[2] - 1 # 3-th CR column
  idx_last_col_Slot_X[0] = idx_1st_col_Slot_X[1] - 1 # 1-th CR column

  # each CR has 60 SLICE vertically, each slot 120
  CR_SLICE_height = 60
  Slot_SLICE_height = 120 # 2x2 slot

  last_row_idx = 959 # Y index of the highest SLICE
  last_col_idx = 232 # X index of the rightest SLICE

  # the vertical columns of the buffer region
  # manually selected to avoid spliting switch boxes. 
  # Sync with getBufferRegionBetweenSlotPair() 
  col_buffer_region_pblock = []

  # during placement, we should leave some gap between the slot and the anchor region
  if not is_for_placement: # for routing, the exact buffer region
    col_buffer_region_pblock.append(f'SLICE_X56Y0:SLICE_X58Y959')
    col_buffer_region_pblock.append(f'SLICE_X115Y0:SLICE_X117Y959')
    col_buffer_region_pblock.append(f'SLICE_X175Y0:SLICE_X177Y959')
  else: # for placement, expand the buffer region
    col_buffer_region_pblock.append(f'SLICE_X55Y0:SLICE_X59Y959')
    col_buffer_region_pblock.append(f'SLICE_X114Y0:SLICE_X118Y959')
    col_buffer_region_pblock.append(f'SLICE_X174Y0:SLICE_X178Y959')    

  # the horizontal rows of the buffer region
  # exclude the region for the up and down device boundaries & die boundaries
  row_buffer_region_pblock = []
  for i in range(8):
    if i % 2 == 1: # only need buffer at the down side
      row_buffer_region_pblock.append(f'SLICE_X0Y{i * 120}:SLICE_X232Y{i * 120 + row_width - 1} ')
    else: # only need buffer at the up side
      row_buffer_region_pblock.append(f'SLICE_X0Y{(i+1) * 120 - row_width}:SLICE_X232Y{(i+1) * 120 - 1} ')

  return '\n'.join(col_buffer_region_pblock) + '\n' + '\n'.join(row_buffer_region_pblock)


def getAllDSPAndBRAMInBoundaryBufferRegions(col_width, row_width):
  """
  should sync up with getAllBoundaryBufferRegions()
  get the DSP and BRAM tiles that fall in the anchor buffer region
  """
  assert col_width == 4
  assert row_width == 5

  # only BRAMs in the horizontable buffer region will be discarded
  RAMB_items = [
    'RAMB18_X0Y334:RAMB18_X13Y337',
    'RAMB18_X0Y238:RAMB18_X13Y241',
    'RAMB18_X0Y142:RAMB18_X13Y145',
    'RAMB18_X0Y46:RAMB18_X13Y49',
    'RAMB36_X0Y167:RAMB36_X13Y168',
    'RAMB36_X0Y119:RAMB36_X13Y120',
    'RAMB36_X0Y71:RAMB36_X13Y72',
    'RAMB36_X0Y23:RAMB36_X13Y24'      
  ]

  # two columns of DSPs in the vertical buffer region will be discarded
  DSP_items = [
    'DSP48E2_X7Y0:DSP48E2_X7Y383',
    'DSP48E2_X24Y0:DSP48E2_X24Y383',

    'DSP48E2_X0Y334:DSP48E2_X31Y337',
    'DSP48E2_X0Y238:DSP48E2_X31Y241',
    'DSP48E2_X0Y142:DSP48E2_X31Y145',
    'DSP48E2_X0Y46:DSP48E2_X31Y49'
  ]

  return RAMB_items + DSP_items 


def getAnchorPblock(slot: Slot):
  vertical_segment, horizontal_segment = generateAnchorInclusivePblock()

  pblock = f'CLOCKREGION_X{slot.down_left_x}Y{slot.down_left_y}:CLOCKREGION_X{slot.up_right_x}Y{slot.up_right_y} '

  pblock += ' ' + vertical_segment[int((slot.down_left_x) / 2)][int(slot.down_left_y / 2)]
  
  pblock += ' ' + vertical_segment[int((slot.up_right_x) / 2 + 1)][int(slot.down_left_y / 2)]

  pblock += ' ' + horizontal_segment[int((slot.down_left_x) / 2)][int((slot.down_left_y) / 2)]

  pblock += ' ' + horizontal_segment[int((slot.down_left_x) / 2)][int((slot.up_right_y) / 2 + 1)]

  return pblock


def getLagunaAnchorInclusivePblock(slot_name):
  slot = Slot(U250_inst, slot_name)

  basic_pblock = getAnchorPblock(slot)

  laugna_inclusive_pblock = ''
  if slot.down_left_y > 0 and slot.up_right_y < 15:
    if slot.down_left_y % 4 == 0:
      laugna_inclusive_pblock = getAnchorPblock(Slot(slot.board, slot.getNeighborSlotName('DOWN')))
    else:
      laugna_inclusive_pblock = getAnchorPblock(Slot(slot.board, slot.getNeighborSlotName('UP')))

  return basic_pblock + ' ' + laugna_inclusive_pblock


def generateAnchorInclusivePblock():
  """
  expand the buffer region a little to allow more routing space for anchor nets
  """
  
  vertical_segment = [['' for j in range(8)] for i in range(5)]
  horizontal_segment = [['' for j in range(9)] for i in range(4)]

  for i in range(8):
    vertical_segment[0][i] = ' '

  for i in range(8):
    # vertical_segment[1][i] = f'DSP48E2_X7Y{48*i}:DSP48E2_X7Y{48*i+47} SLICE_X56Y{120*i}:SLICE_X58Y{120*i+119}'
    vertical_segment[1][i] = f'DSP48E2_X7Y{48*i}:DSP48E2_X7Y{48*i+47} SLICE_X55Y{120*i}:SLICE_X59Y{120*i+119}'

  for i in range(8):
    # vertical_segment[2][i] = f'SLICE_X115Y{120*i}:SLICE_X117Y{120*i+119}'
    vertical_segment[2][i] = f'SLICE_X114Y{120*i}:SLICE_X118Y{120*i+119}'

  for i in range(8):
    # vertical_segment[3][i] = f'DSP48E2_X24Y{48*i}:DSP48E2_X24Y{48*i+47} SLICE_X175Y{120*i}:SLICE_X177Y{120*i+119}'
    vertical_segment[3][i] = f'DSP48E2_X24Y{48*i}:DSP48E2_X24Y{48*i+47} SLICE_X174Y{120*i}:SLICE_X178Y{120*i+119}'

  for i in range(8):
    vertical_segment[4][i] = ' '

  gap = 1

  for i in range(4):
    horizontal_segment[0][i*2+1] = f'RAMB36_X0Y{23+48*i}:RAMB36_X3Y{24+48*i} RAMB18_X0Y{46+96*i}:RAMB18_X3Y{49+96*i} DSP48E2_X0Y{46+96*i}:DSP48E2_X7Y{49+96*i} SLICE_X0Y{115+240*i-gap}:SLICE_X58Y{124+240*i+gap}'

  for i in range(4):
    horizontal_segment[1][i*2+1] = f'RAMB36_X4Y{23+48*i}:RAMB36_X7Y{24+48*i} RAMB18_X4Y{46+96*i}:RAMB18_X7Y{49+96*i} DSP48E2_X7Y{46+96*i}:DSP48E2_X15Y{49+96*i} SLICE_X56Y{115+240*i-gap}:SLICE_X117Y{124+240*i+gap}'

  for i in range(4):
    horizontal_segment[2][i*2+1] = f'RAMB36_X8Y{23+48*i}:RAMB36_X10Y{24+48*i} RAMB18_X8Y{46+96*i}:RAMB18_X10Y{49+96*i} DSP48E2_X16Y{46+96*i}:DSP48E2_X24Y{49+96*i} SLICE_X115Y{115+240*i-gap}:SLICE_X177Y{124+240*i+gap}' 

  for i in range(4):
    horizontal_segment[3][i*2+1] = f'RAMB36_X11Y{23+48*i}:RAMB36_X13Y{24+48*i} RAMB18_X11Y{46+96*i}:RAMB18_X13Y{49+96*i} DSP48E2_X24Y{46+96*i}:DSP48E2_X31Y{49+96*i} SLICE_X175Y{115+240*i-gap}:SLICE_X232Y{124+240*i+gap}'   

  for i in range(5):
    horizontal_segment[0][i*2] = ' '
    horizontal_segment[1][i*2] = ' '
    horizontal_segment[2][i*2] = ' '
    horizontal_segment[3][i*2] = ' '

  return vertical_segment, horizontal_segment


def constrainAnchorNetsAndSlot(slot_name, pblock_def):
  """
  add 2nd level pblock for anchors
  since anchors are outside of the slot, anchor nets are not constrained.
  thus they may go far into the nearby slots.
  the 2nd level pblock aims to constraint the anchor nets within the current slot + the anchor region
  """
  script = []

  script.append(f'create_pblock anchor_pblock')
  script.append(f'resize_pblock [get_pblocks anchor_pblock] -add {{ {pblock_def} }}') # the clock regions for the slot

  slot = Slot(U250_inst, slot_name)
  script.append(f'resize_pblock [get_pblocks anchor_pblock] -add {{ {getAnchorPblock(slot)} }}') 

  # constrain non-laguna anchors. No need to worry about the routing of laguna anchors
  script.append(f'add_cells_to_pblock [get_pblocks anchor_pblock] [get_cells *q0_reg* -filter {{LOC !~ *LAGUNA* }}]') 
  script.append(f'add_cells_to_pblock [get_pblocks anchor_pblock] [get_cells {slot_name}_ctrl_U0]') # constrain all anchors
  script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks anchor_pblock]')
  script.append(f'set_property SNAPPING_MODE ON [get_pblocks anchor_pblock]')

  return script
