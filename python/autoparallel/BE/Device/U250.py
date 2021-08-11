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

  URAM_items = [
    'URAM288_X0Y220:URAM288_X4Y227',
    'URAM288_X0Y156:URAM288_X4Y163',
    'URAM288_X0Y92:URAM288_X4Y99',
    'URAM288_X0Y28:URAM288_X4Y35'
  ]

  return RAMB_items + DSP_items + URAM_items


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
  [UPDATE] do not expand the anchor region
  """
  
  vertical_segment = [['' for j in range(8)] for i in range(5)]
  horizontal_segment = [['' for j in range(9)] for i in range(4)]

  for i in range(8):
    vertical_segment[0][i] = ' '

  for i in range(8):
    vertical_segment[1][i] = f'DSP48E2_X7Y{48*i}:DSP48E2_X7Y{48*i+47} SLICE_X56Y{120*i}:SLICE_X58Y{120*i+119}'
    # vertical_segment[1][i] = f'DSP48E2_X7Y{48*i}:DSP48E2_X7Y{48*i+47} SLICE_X55Y{120*i}:SLICE_X59Y{120*i+119}'

  for i in range(8):
    vertical_segment[2][i] = f'SLICE_X115Y{120*i}:SLICE_X117Y{120*i+119}'
    # vertical_segment[2][i] = f'SLICE_X114Y{120*i}:SLICE_X118Y{120*i+119}'

  for i in range(8):
    vertical_segment[3][i] = f'DSP48E2_X24Y{48*i}:DSP48E2_X24Y{48*i+47} SLICE_X175Y{120*i}:SLICE_X177Y{120*i+119}'
    # vertical_segment[3][i] = f'DSP48E2_X24Y{48*i}:DSP48E2_X24Y{48*i+47} SLICE_X174Y{120*i}:SLICE_X178Y{120*i+119}'

  for i in range(8):
    vertical_segment[4][i] = ' '

  gap = 0

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


DETAILED_SLOT_RANGE = {
  "CR_X0Y0_To_CR_X1Y1" : "{SLICE_X0Y0:SLICE_X56Y119 DSP48E2_X0Y0:DSP48E2_X7Y47 LAGUNA_X0Y0:LAGUNA_X7Y119 RAMB18_X0Y0:RAMB18_X3Y47 RAMB36_X0Y0:RAMB36_X3Y23 URAM288_X0Y0:URAM288_X0Y31}",
  "CR_X2Y0_To_CR_X3Y1" : "{SLICE_X57Y0:SLICE_X116Y119 DSP48E2_X8Y0:DSP48E2_X15Y47 LAGUNA_X8Y0:LAGUNA_X15Y119 RAMB18_X4Y0:RAMB18_X7Y47 RAMB36_X4Y0:RAMB36_X7Y23 URAM288_X1Y0:URAM288_X1Y31}",
  "CR_X4Y0_To_CR_X5Y1" : "{SLICE_X117Y0:SLICE_X175Y119 DSP48E2_X16Y0:DSP48E2_X24Y47 LAGUNA_X16Y0:LAGUNA_X23Y119 RAMB18_X8Y0:RAMB18_X10Y47 RAMB36_X8Y0:RAMB36_X10Y23 URAM288_X2Y0:URAM288_X3Y31}",
  "CR_X6Y0_To_CR_X7Y1" : "{SLICE_X176Y0:SLICE_X232Y119 DSP48E2_X25Y0:DSP48E2_X31Y47 LAGUNA_X24Y0:LAGUNA_X31Y119 RAMB18_X11Y0:RAMB18_X13Y47 RAMB36_X11Y0:RAMB36_X13Y23 URAM288_X4Y0:URAM288_X4Y31}",
  "CR_X0Y2_To_CR_X1Y3" : "{SLICE_X0Y120:SLICE_X56Y239 DSP48E2_X0Y48:DSP48E2_X7Y95 LAGUNA_X0Y120:LAGUNA_X7Y239 RAMB18_X0Y48:RAMB18_X3Y95 RAMB36_X0Y24:RAMB36_X3Y47 URAM288_X0Y32:URAM288_X0Y63}",
  "CR_X2Y2_To_CR_X3Y3" : "{SLICE_X57Y120:SLICE_X116Y239 DSP48E2_X8Y48:DSP48E2_X15Y95 LAGUNA_X8Y120:LAGUNA_X15Y239 RAMB18_X4Y48:RAMB18_X7Y95 RAMB36_X4Y24:RAMB36_X7Y47 URAM288_X1Y32:URAM288_X1Y63}",
  "CR_X4Y2_To_CR_X5Y3" : "{SLICE_X117Y120:SLICE_X175Y239 DSP48E2_X16Y48:DSP48E2_X24Y95 LAGUNA_X16Y120:LAGUNA_X23Y239 RAMB18_X8Y48:RAMB18_X10Y95 RAMB36_X8Y24:RAMB36_X10Y47 URAM288_X2Y32:URAM288_X3Y63}",
  "CR_X6Y2_To_CR_X7Y3" : "{SLICE_X176Y120:SLICE_X232Y239 DSP48E2_X25Y48:DSP48E2_X31Y95 LAGUNA_X24Y120:LAGUNA_X31Y239 RAMB18_X11Y48:RAMB18_X13Y95 RAMB36_X11Y24:RAMB36_X13Y47 URAM288_X4Y32:URAM288_X4Y63}",
  "CR_X0Y4_To_CR_X1Y5" : "{SLICE_X0Y240:SLICE_X56Y359 DSP48E2_X0Y96:DSP48E2_X7Y143 LAGUNA_X0Y240:LAGUNA_X7Y359 RAMB18_X0Y96:RAMB18_X3Y143 RAMB36_X0Y48:RAMB36_X3Y71 URAM288_X0Y64:URAM288_X0Y95}",
  "CR_X2Y4_To_CR_X3Y5" : "{SLICE_X57Y240:SLICE_X116Y359 DSP48E2_X8Y96:DSP48E2_X15Y143 LAGUNA_X8Y240:LAGUNA_X15Y359 RAMB18_X4Y96:RAMB18_X7Y143 RAMB36_X4Y48:RAMB36_X7Y71 URAM288_X1Y64:URAM288_X1Y95}",
  "CR_X4Y4_To_CR_X5Y5" : "{SLICE_X117Y240:SLICE_X175Y359 DSP48E2_X16Y96:DSP48E2_X24Y143 LAGUNA_X16Y240:LAGUNA_X23Y359 RAMB18_X8Y96:RAMB18_X10Y143 RAMB36_X8Y48:RAMB36_X10Y71 URAM288_X2Y64:URAM288_X3Y95}",
  "CR_X6Y4_To_CR_X7Y5" : "{SLICE_X176Y240:SLICE_X232Y359 DSP48E2_X25Y96:DSP48E2_X31Y143 LAGUNA_X24Y240:LAGUNA_X31Y359 RAMB18_X11Y96:RAMB18_X13Y143 RAMB36_X11Y48:RAMB36_X13Y71 URAM288_X4Y64:URAM288_X4Y95}",
  "CR_X0Y6_To_CR_X1Y7" : "{SLICE_X0Y360:SLICE_X56Y479 DSP48E2_X0Y144:DSP48E2_X7Y191 LAGUNA_X0Y360:LAGUNA_X7Y479 RAMB18_X0Y144:RAMB18_X3Y191 RAMB36_X0Y72:RAMB36_X3Y95 URAM288_X0Y96:URAM288_X0Y127}",
  "CR_X2Y6_To_CR_X3Y7" : "{SLICE_X57Y360:SLICE_X116Y479 DSP48E2_X8Y144:DSP48E2_X15Y191 LAGUNA_X8Y360:LAGUNA_X15Y479 RAMB18_X4Y144:RAMB18_X7Y191 RAMB36_X4Y72:RAMB36_X7Y95 URAM288_X1Y96:URAM288_X1Y127}",
  "CR_X4Y6_To_CR_X5Y7" : "{SLICE_X117Y360:SLICE_X175Y479 DSP48E2_X16Y144:DSP48E2_X24Y191 LAGUNA_X16Y360:LAGUNA_X23Y479 RAMB18_X8Y144:RAMB18_X10Y191 RAMB36_X8Y72:RAMB36_X10Y95 URAM288_X2Y96:URAM288_X3Y127}",
  "CR_X6Y6_To_CR_X7Y7" : "{SLICE_X176Y360:SLICE_X232Y479 DSP48E2_X25Y144:DSP48E2_X31Y191 LAGUNA_X24Y360:LAGUNA_X31Y479 RAMB18_X11Y144:RAMB18_X13Y191 RAMB36_X11Y72:RAMB36_X13Y95 URAM288_X4Y96:URAM288_X4Y127}",
  "CR_X0Y8_To_CR_X1Y9" : "{SLICE_X0Y480:SLICE_X56Y599 DSP48E2_X0Y192:DSP48E2_X7Y239 LAGUNA_X0Y480:LAGUNA_X7Y599 RAMB18_X0Y192:RAMB18_X3Y239 RAMB36_X0Y96:RAMB36_X3Y119 URAM288_X0Y128:URAM288_X0Y159}",
  "CR_X2Y8_To_CR_X3Y9" : "{SLICE_X57Y480:SLICE_X116Y599 DSP48E2_X8Y192:DSP48E2_X15Y239 LAGUNA_X8Y480:LAGUNA_X15Y599 RAMB18_X4Y192:RAMB18_X7Y239 RAMB36_X4Y96:RAMB36_X7Y119 URAM288_X1Y128:URAM288_X1Y159}",
  "CR_X4Y8_To_CR_X5Y9" : "{SLICE_X117Y480:SLICE_X175Y599 DSP48E2_X16Y192:DSP48E2_X24Y239 LAGUNA_X16Y480:LAGUNA_X23Y599 RAMB18_X8Y192:RAMB18_X10Y239 RAMB36_X8Y96:RAMB36_X10Y119 URAM288_X2Y128:URAM288_X3Y159}",
  "CR_X6Y8_To_CR_X7Y9" : "{SLICE_X176Y480:SLICE_X232Y599 DSP48E2_X25Y192:DSP48E2_X31Y239 LAGUNA_X24Y480:LAGUNA_X31Y599 RAMB18_X11Y192:RAMB18_X13Y239 RAMB36_X11Y96:RAMB36_X13Y119 URAM288_X4Y128:URAM288_X4Y159}",
  "CR_X0Y10_To_CR_X1Y11" : "{SLICE_X0Y600:SLICE_X56Y719 DSP48E2_X0Y240:DSP48E2_X7Y287 LAGUNA_X0Y600:LAGUNA_X7Y719 RAMB18_X0Y240:RAMB18_X3Y287 RAMB36_X0Y120:RAMB36_X3Y143 URAM288_X0Y160:URAM288_X0Y191}",
  "CR_X2Y10_To_CR_X3Y11" : "{SLICE_X57Y600:SLICE_X116Y719 DSP48E2_X8Y240:DSP48E2_X15Y287 LAGUNA_X8Y600:LAGUNA_X15Y719 RAMB18_X4Y240:RAMB18_X7Y287 RAMB36_X4Y120:RAMB36_X7Y143 URAM288_X1Y160:URAM288_X1Y191}",
  "CR_X4Y10_To_CR_X5Y11" : "{SLICE_X117Y600:SLICE_X175Y719 DSP48E2_X16Y240:DSP48E2_X24Y287 LAGUNA_X16Y600:LAGUNA_X23Y719 RAMB18_X8Y240:RAMB18_X10Y287 RAMB36_X8Y120:RAMB36_X10Y143 URAM288_X2Y160:URAM288_X3Y191}",
  "CR_X6Y10_To_CR_X7Y11" : "{SLICE_X176Y600:SLICE_X232Y719 DSP48E2_X25Y240:DSP48E2_X31Y287 LAGUNA_X24Y600:LAGUNA_X31Y719 RAMB18_X11Y240:RAMB18_X13Y287 RAMB36_X11Y120:RAMB36_X13Y143 URAM288_X4Y160:URAM288_X4Y191}",
  "CR_X0Y12_To_CR_X1Y13" : "{SLICE_X0Y720:SLICE_X56Y839 DSP48E2_X0Y288:DSP48E2_X7Y335 LAGUNA_X0Y720:LAGUNA_X7Y839 RAMB18_X0Y288:RAMB18_X3Y335 RAMB36_X0Y144:RAMB36_X3Y167 URAM288_X0Y192:URAM288_X0Y223}",
  "CR_X2Y12_To_CR_X3Y13" : "{SLICE_X57Y720:SLICE_X116Y839 DSP48E2_X8Y288:DSP48E2_X15Y335 LAGUNA_X8Y720:LAGUNA_X15Y839 RAMB18_X4Y288:RAMB18_X7Y335 RAMB36_X4Y144:RAMB36_X7Y167 URAM288_X1Y192:URAM288_X1Y223}",
  "CR_X4Y12_To_CR_X5Y13" : "{SLICE_X117Y720:SLICE_X175Y839 DSP48E2_X16Y288:DSP48E2_X24Y335 LAGUNA_X16Y720:LAGUNA_X23Y839 RAMB18_X8Y288:RAMB18_X10Y335 RAMB36_X8Y144:RAMB36_X10Y167 URAM288_X2Y192:URAM288_X3Y223}",
  "CR_X6Y12_To_CR_X7Y13" : "{SLICE_X176Y720:SLICE_X232Y839 DSP48E2_X25Y288:DSP48E2_X31Y335 LAGUNA_X24Y720:LAGUNA_X31Y839 RAMB18_X11Y288:RAMB18_X13Y335 RAMB36_X11Y144:RAMB36_X13Y167 URAM288_X4Y192:URAM288_X4Y223}",
  "CR_X0Y14_To_CR_X1Y15" : "{SLICE_X0Y840:SLICE_X56Y959 DSP48E2_X0Y336:DSP48E2_X7Y383 LAGUNA_X0Y840:LAGUNA_X7Y959 RAMB18_X0Y336:RAMB18_X3Y383 RAMB36_X0Y168:RAMB36_X3Y191 URAM288_X0Y224:URAM288_X0Y255}",
  "CR_X2Y14_To_CR_X3Y15" : "{SLICE_X57Y840:SLICE_X116Y959 DSP48E2_X8Y336:DSP48E2_X15Y383 LAGUNA_X8Y840:LAGUNA_X15Y959 RAMB18_X4Y336:RAMB18_X7Y383 RAMB36_X4Y168:RAMB36_X7Y191 URAM288_X1Y224:URAM288_X1Y255}",
  "CR_X4Y14_To_CR_X5Y15" : "{SLICE_X117Y840:SLICE_X175Y959 DSP48E2_X16Y336:DSP48E2_X24Y383 LAGUNA_X16Y840:LAGUNA_X23Y959 RAMB18_X8Y336:RAMB18_X10Y383 RAMB36_X8Y168:RAMB36_X10Y191 URAM288_X2Y224:URAM288_X3Y255}",
  "CR_X6Y14_To_CR_X7Y15" : "{SLICE_X176Y840:SLICE_X232Y959 DSP48E2_X25Y336:DSP48E2_X31Y383 LAGUNA_X24Y840:LAGUNA_X31Y959 RAMB18_X11Y336:RAMB18_X13Y383 RAMB36_X11Y168:RAMB36_X13Y191 URAM288_X4Y224:URAM288_X4Y255}"
}

def getDetailedRangeOfClockRegion(slot_name):
  """
  to express the range of a slot, we use the detailed ranges here, instead of using CLOCKREGION
  This can help avoid including some non-visible resources (e.g. BUFG-GT) into the pblock
  which may make the surface of the pblock uneven and affect our contain routing scheme
  """
  return DETAILED_SLOT_RANGE[slot_name]
