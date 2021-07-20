import itertools
import logging
import json
import operator
import time

from collections import defaultdict
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

  def __str__(self):
    return self.getString()

  def getString(self):
    return f'X{self.bottom_coor_x}Y{self.bottom_coor_y} <-> X{self.top_coor_x}Y{self.top_coor_y}'  

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

  def getCostForAnchor(self, list_of_cell_property_dict: List[Dict], anchor_direction: str) -> float:
    """
    the cost for placing an anchor on this channel
    """
    SLR_crossing_penalty = 10
    SLL_length = 60

    lut_penalty = lambda num_lut_on_path : 1 + 0.3 * num_lut_on_path

    def getDistFromCells(list_of_cell_property_dict: List[Dict]) -> List[int]:
      """
      Distance between the RX of the SLL and the end cell.
      If the connection goes up, the dist is between the end cells and the top_coor
      Else the dist is between the end cells and the bottom_coor
      """
      dists = []
      # for loc, type in coor_to_cell_types.items():
      for cell_property_dict in list_of_cell_property_dict:
        loc = cell_property_dict["normalized_coordinate"]

        x, y = loc[0], loc[1]

        # determine if the cell is at the top side or bottom side
        is_cell_at_bottom = self.bottom_slot_y_min <= y <= self.bottom_slot_y_max

        if anchor_direction == 'DOWN':
          if is_cell_at_bottom:
            orig_dist = abs(x - self.bottom_coor_x) + abs(y - self.bottom_coor_y)
          else:
            # if a connection goes down, the end cell at the top will connect to 
            # the input of the SLL at the top, then travel through SLL to the RX at the bottom
            orig_dist = SLR_crossing_penalty + SLL_length + abs(x - self.top_coor_x) + abs(y - self.top_coor_y)

        elif anchor_direction == 'UP':
          if is_cell_at_bottom:
            # if a connection goes up, the end cell at the bottom will connect to
            # the input of the SLL at the bottom, then travel through SLL to the RX at the top
            orig_dist = SLR_crossing_penalty + SLL_length + abs(x - self.bottom_coor_x) + abs(y - self.bottom_coor_y)
          else:
            orig_dist = abs(x - self.top_coor_x) + abs(y - self.top_coor_y)

        else:
          assert False

        # penaltize wires to LUTs
        dists.append(orig_dist * lut_penalty(cell_property_dict["num_lut_on_path"]))

      return dists

    dists = getDistFromCells(list_of_cell_property_dict)

    # avg wire length
    dist_score = sum(dists) / len(dists)

    unbalance_penalty = max(dists) - min(dists)

    # prevent extremely short wires
    hold_penalty = max(0, 10 - min(dists))

    return dist_score + unbalance_penalty + hold_penalty


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


def _get_anchor_2_sll_dir(hub, slot1_name, slot2_name, anchor_connections: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
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
  for anchor in anchor_connections.keys():
    hls_var_name = anchor.split('_q0_reg')[0]
    anchor_2_sll_dir[anchor] = slot_io_2_sll_dir[hls_var_name]

  return anchor_2_sll_dir


def getSLLChannelToAnchorCost(
    sll_channel_list: List[SLLChannel], 
    anchor_connections: Dict[str, List[Dict]], 
    anchor_to_sll_dir: Dict[str, str]):
  """
  We need to assign a score if an anchor is placed in a bin
  To prevent hold violation, we neglect the length of the SLL. Thus the distance will be 
  (1) the source cell to the input of the SLL
  (2) the output of the SLL to the destination cells
  
  return: SLL channel -> anchor -> score
  """
  sll_to_anchor_to_cost = {}

  for sll_channel in sll_channel_list:
    anchor_to_cost = {anchor : sll_channel.getCostForAnchor(list_of_cell_property_dict, anchor_to_sll_dir[anchor]) \
      for anchor, list_of_cell_property_dict in anchor_connections.items()}
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


def _analyzeILPResults(anchor_to_sll_to_cost, anchor_to_selected_bin):
  """
  get how optimal is the final position for each anchor
  """
  anchor_to_sll_string_to_cost = {}
  for anchor, sll_to_cost in anchor_to_sll_to_cost.items():
    anchor_to_sll_string_to_cost[anchor] = {sll.getString() : cost for sll, cost in sll_to_cost.items()}
  open('debug_anchor_to_bin_to_cost.json', 'w').write(json.dumps(anchor_to_sll_string_to_cost, indent=2))

  ilp_report = {}

  for anchor, chosen_bin in anchor_to_selected_bin.items():
    ilp_report[anchor] = {}

    bin2cost = anchor_to_sll_to_cost[anchor]
    all_cost_list = [[cost, bin] for bin, cost in bin2cost.items()]
    all_cost_list = sorted(all_cost_list, key=operator.itemgetter(0))
    cost_value_list = [x[0] for x in all_cost_list]

    ilp_report[anchor]['curr_cost'] = bin2cost[chosen_bin]
    ilp_report[anchor]['min_cost'] = all_cost_list[0][0]
    ilp_report[anchor]['max_cost'] = all_cost_list[-1][0]
    ilp_report[anchor]['rank_of_chosen_bin'] = cost_value_list.index(bin2cost[chosen_bin])
    ilp_report[anchor]['total_bin_num'] = len(all_cost_list)
    ilp_report[anchor]['bin_location'] = chosen_bin.getString()
    optimal_bin = all_cost_list[0][1]
    ilp_report[anchor]['optimal_location'] = optimal_bin.getString()
    
  ranks = [anchor_info['rank_of_chosen_bin'] for anchor_info in ilp_report.values()]
  if len(ranks):
    logging.info(f'average rank of the final placed bins: {sum(ranks) / len(ranks)}')
    logging.info(f'worst rank of the final placed bins: {max(ranks)}')
  else:
    logging.warning(f'no anchors between the pair')

  open('ilp_quality_report.json', 'w').write(json.dumps(ilp_report, indent=2))


def placeLagunaAnchors(hub, pair_name: str, anchor_connections: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
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

  anchor_to_sll_dir = _get_anchor_2_sll_dir(hub, slot1_name, slot2_name, anchor_connections)

  _, anchor_to_sll_to_cost = getSLLChannelToAnchorCost(sll_channels, anchor_connections, anchor_to_sll_dir)

  anchor_to_sll = placeAnchorToSLLChannel(anchor_to_sll_to_cost)

  _analyzeILPResults(anchor_to_sll_to_cost, anchor_to_sll)

  anchor_to_laguna_reg = {}
  for anchor, sll in anchor_to_sll.items():
    anchor_dir = anchor_to_sll_dir[anchor]
    anchor_to_laguna_reg[anchor] = sll.placeAnchor(anchor_dir)

  return anchor_to_laguna_reg