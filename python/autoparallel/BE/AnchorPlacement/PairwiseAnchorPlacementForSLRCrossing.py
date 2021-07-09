from collections import defaultdict
import itertools
import time
from typing import List, Tuple, Dict
from mip import Model, minimize, CONTINUOUS, xsum

from autoparallel.BE.Utilities import isPairSLRCrossing
from autoparallel.BE.Device.U250 import idx_of_left_side_slice_of_laguna_column
from autobridge.Device.DeviceManager import DeviceU250
from autobridge.Opt.Slot import Slot

U250_inst = DeviceU250()

slice_to_laguna = {idx_of_left_side_slice_of_laguna_column[i] : i \
  for i in range(len(idx_of_left_side_slice_of_laguna_column))}

class SLLChannel:
  """
  each SLLChannel consists of 24 SLL wires
  The bottom/top of those SLL wires are the same with reference to SLICE coordinates
  each channel will correspond to 8 laguna sites, each with 6 RX registers
  if an anchor is upward, it must be placed on the RX at the top side
  otherwise it must be placed on the RX at the bottom side
  """
  def __init__(self, bottom_coor_y, i_th_column: int):
    self.bottom_coor_x = idx_of_left_side_slice_of_laguna_column[i_th_column]
    self.bottom_coor_y = bottom_coor_y
    self.top_coor_x = self.bottom_coor_x
    self.top_coor_y = bottom_coor_y + 60
    self.capacity = 20
    self.bottom_slot_y_min = int(bottom_coor_y / 120) * 120
    self.bottom_slot_y_max = self.bottom_slot_y_min + 119
    self._initRXList(i_th_column, bottom_coor_y)

  def __hash__(self):
    return hash((self.bottom_coor_x, self.bottom_coor_y))

  def _initRXList(self, i_th_column, bottom_coor_y):
    """
    get the laguna RX registers associated with this channel
    """
    bottom_laguna_sites = [
      f'LAGUNA_X{x}Y{y}' for x in (i_th_column*2, i_th_column*2+1) \
        for y in self._get_nearest_laguna_y(bottom_coor_y) ]

    top_laguna_sites = [
      f'LAGUNA_X{x}Y{y}' for x in (i_th_column*2, i_th_column*2+1) \
        for y in self._get_nearest_laguna_y(bottom_coor_y + 60) ]

    # each laguna site has 6 RX registers
    self.bottom_laguna_RX = [f'{site}/RX_REG{i}' for i in range(6) for site in bottom_laguna_sites]
    self.top_laguna_RX = [f'{site}/RX_REG{i}' for i in range(6) for site in top_laguna_sites]    

  def _get_nearest_laguna_y(self, slice_y):
    """
    convert from SLICE coordinate to laguna coordinate
    """
    if 180 <= slice_y <= 299:
      laguna_y = (slice_y - 180) * 2 + 120
    elif 420 <= slice_y <= 539:
      laguna_y = (slice_y - 420) * 2 + 360
    elif 660 <= slice_y <= 779:
      laguna_y = (slice_y - 660) * 2 + 600
    else:
      assert False
    return (laguna_y, laguna_y+1)

  def getCostForAnchor(self, coor_to_cell_types):
    """
    the cost for placing an anchor on this channel
    """
    lut_penalty = lambda types : 2 if any('LUT' in type for type in types) else 1

    def getDistFromCells(coor_to_cell_types: Dict[str, str]) -> List[int]:
      """
      the distances from each endpoint of an anchor. Penalize if an endpoint is LUT
      """
      dist = []
      for loc, type in coor_to_cell_types.items():
        x, y = loc[0], loc[1]
        # determine if the cell is at the top side or bottom side
        if self.bottom_slot_y_min <= y <= self.bottom_slot_y_max:
          orig_dist = abs(x - self.bottom_coor_x) + abs(y - self.bottom_coor_y)
        else:
          orig_dist = abs(x - self.top_coor_x) + abs(y - self.top_coor_y)

        # penaltize wires to LUTs
        dist.append(orig_dist * lut_penalty(type))

      return dist

    dists = getDistFromCells(coor_to_cell_types)

    # avg wire length
    dist_score = sum(dists) / len(dists)

    unbalance_penalty = max(dists) - min(dists)

    # prevent extremely short wires
    hold_penalty = max(0, 10 - min(dists))

    return dist_score + unbalance_penalty + 5 * hold_penalty

  def placeAnchor(self, anchor_dir):
    """
    mark an RX register as occupied by popping it out
    The sites at the top will use the RX from small index to large index
    the sites at the bottom will use the RX from large index to small index
    Note that each SLL is associate with two RX and two TX registers 
    so that it can be used in both directions. But only one of them could be used.
    """
    if anchor_dir == 'UP':
      return self.top_laguna_RX.pop()
    elif anchor_dir == 'DOWN':
      return self.bottom_laguna_RX.pop(0)
    else:
      assert False, anchor_dir


def _get_anchor_2_sll_dir(hub, slot1_name, slot2_name, anchor_to_coor_to_cell_types):
  """
  each anchor will use one SLL connection.
  get which direction will the SLL will be used, upward or downward
  """
  slot1 = Slot(U250_inst, slot1_name)
  slot2 = Slot(U250_inst, slot2_name)
  up_slot = slot1 if slot1.down_left_y > slot2.down_left_y else slot2

  # get the downward IO of the upper slot
  up_slot_io = hub['PathPlanningWire'][up_slot.getRTLModuleName()]['DOWN']
  # double check that the information in the hub is consistent
  all_io = hub['SlotIO'][up_slot.getRTLModuleName()]
  io_from_all_directions = list(itertools.chain.from_iterable(hub['PathPlanningWire'][up_slot.getRTLModuleName()].values()))
  if not len(all_io) == len(io_from_all_directions) + 1: # +1 because of ap_clk
    name_all_io = [io[-1] for io in all_io]
    name_io_from_all_directions = [io[-1] for io in io_from_all_directions]
    diff_list = set(name_all_io) - set(name_io_from_all_directions)
    assert all('_axi_' in d or 'clk' in d for d in diff_list)

  # the output wire of the upper slot will travel DOWN the sll
  get_sll_dir = lambda in_or_out : 'DOWN' if in_or_out == 'output' else 'UP'
  slot_io_2_sll_dir = {io[-1] : get_sll_dir(io[0]) for io in up_slot_io}

  anchor_2_sll_dir = {}
  for anchor in anchor_to_coor_to_cell_types.keys():
    hls_var_name = anchor.split('_q0_reg')[0]
    anchor_2_sll_dir[anchor] = slot_io_2_sll_dir[hls_var_name]

  return anchor_2_sll_dir


def getSLLChannelToAnchorCost(sll_channel_list: List[SLLChannel], anchor_to_coor_to_cell_types):
  """
  We need to assign a score if an anchor is placed in a bin
  To prevent hold violation, we neglect the length of the SLL. Thus the distance will be 
  (1) the source cell to the input of the SLL
  (2) the output of the SLL to the destination cells
  
  return: SLL channel -> anchor -> score
  """
  sll_to_anchor_to_cost = {}

  for sll_channel in sll_channel_list:
    anchor_to_cost = {anchor : sll_channel.getCostForAnchor(coor_to_cell_types) \
      for anchor, coor_to_cell_types in anchor_to_coor_to_cell_types.items()}
    sll_to_anchor_to_cost[sll_channel] = anchor_to_cost

  anchor_to_sll_to_cost = defaultdict(dict)
  for sll, anchor_to_cost in sll_to_anchor_to_cost.items():
    for anchor, cost in anchor_to_cost.items():
      anchor_to_sll_to_cost[anchor][sll] = cost

  return sll_to_anchor_to_cost, anchor_to_sll_to_cost


def getSLLChannels(slot1_name: str, slot2_name: str) -> List[SLLChannel]:
  """
  get all SLL channels between a slot pair
  each channel should have an input coor, an output coor, and 24 RX names
  first get the X coor of the 4 columns
  """
  slot1 = Slot(U250_inst, slot1_name)
  slot2 = Slot(U250_inst, slot2_name)
  i_th_column_range = range(slot1.down_left_x * 2, slot1.up_right_x * 2)

  pair_down_left_y = min(slot1.down_left_y, slot2.down_left_y)
  if pair_down_left_y == 2:
    sll_bottom_y_range = range(180, 240)
  elif pair_down_left_y == 6:
    sll_bottom_y_range = range(420, 480)
  elif pair_down_left_y == 10:
    sll_bottom_y_range = range(660, 720)
  else:
    assert False

  sll_channels = [SLLChannel(y, i) for y in sll_bottom_y_range for i in i_th_column_range]

  return sll_channels


def placeAnchorToSLLChannel(anchor_to_sll_to_cost) -> Dict[str, SLLChannel]:
  """
  run ILP to map anchor to channels
  """
  start_time = time.perf_counter()
  get_time_stamp = lambda : time.perf_counter() - start_time

  m = Model()

  anchor_to_sll_to_var = {}
  for anchor, sll_to_cost in anchor_to_sll_to_cost.items():
    sll_to_var = {sll : m.add_var(var_type=CONTINUOUS, lb=0, ub=1) for sll in sll_to_cost.keys()}
    anchor_to_sll_to_var[anchor] = sll_to_var

  sll_to_anchor_to_var = defaultdict(dict)
  for anchor, sll_to_var in anchor_to_sll_to_var.items():
    for sll, var in sll_to_var.items():
      sll_to_anchor_to_var[sll][anchor] = var

  # each anchor is placed once
  for anchor, sll_to_var in anchor_to_sll_to_var.items():
    m += xsum(var for var in sll_to_var.values()) == 1

  # limit on sll capacity, currently set to 20/24
  for sll, anchor_to_var in sll_to_anchor_to_var.items():
    m += xsum(var for var in anchor_to_var.values()) <= sll.capacity

  # objective
  var_and_cost = []
  for anchor, sll_to_cost in anchor_to_sll_to_cost.items():
    sll_to_var = anchor_to_sll_to_var[anchor]
    for sll in sll_to_cost.keys():
      var_and_cost.append((sll_to_var[sll], sll_to_cost[sll]))
  m.objective = minimize(xsum(var * cost for var, cost in var_and_cost))

  m.optimize()

  anchor_to_sll = {}
  for anchor, sll_to_var in anchor_to_sll_to_var.items():
    for sll, var in sll_to_var.items():
      var_value = round(var.x)
      assert abs(var.x - var_value) < 0.000001, var.x

      if var_value == 1:
        anchor_to_sll[anchor] = sll

  return anchor_to_sll


def placeLagunaAnchors(hub, pair_name, anchor_to_coor_to_cell_types):
  """
  separally handle the anchor placement for SLR crossing pairs
  The source cannot be too close to the chose SLL
  There are 4 laguna columns between a pair of slots
  Each column has 1440 SLL wires
  We divide the 1440 SLL into 60 channels, each of 24 wire.
  Wires in the same channel has the same src/sink position thus are deemed the same
  Thus we have 4 * 60 = 240 bins, each with a capacity of 24
  Each SLL is of 60 SLICE high, thus each bin has a input coor and an output coor differed by 60

  """
  
  slot1_name, slot2_name = pair_name.split('_AND_')
  assert isPairSLRCrossing(slot1_name, slot2_name)

  sll_channels = getSLLChannels(slot1_name, slot2_name)

  _, anchor_to_sll_to_cost = getSLLChannelToAnchorCost(sll_channels, anchor_to_coor_to_cell_types)

  anchor_to_sll = placeAnchorToSLLChannel(anchor_to_sll_to_cost)

  anchor_to_sll_dir = _get_anchor_2_sll_dir(hub, slot1_name, slot2_name, anchor_to_coor_to_cell_types)

  anchor_to_laguna_reg = {}
  for anchor, sll in anchor_to_sll.items():
    anchor_dir = anchor_to_sll_dir[anchor]
    anchor_to_laguna_reg[anchor] = sll.placeAnchor(anchor_dir)

  return anchor_to_laguna_reg