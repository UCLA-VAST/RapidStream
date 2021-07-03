import json
import re
import sys
import os
import logging
import time
import itertools
from collections import defaultdict
from mip import Model, minimize, CONTINUOUS, xsum
from autoparallel.BE.GenAnchorConstraints import __getBufferRegionSize
from autoparallel.BE.BEManager import loggingSetup
from autoparallel.BE.Device import U250
from autobridge.Device.DeviceManager import DeviceU250
from autoparallel.BE.Device import U250
from autobridge.Opt.Slot import Slot

U250_inst = DeviceU250()
######################### ILP placement ############################################

def __getWeightMatchingBins(slot1_name, slot2_name, bin_size_x, bin_size_y):
  """
  quantize the buffer region into disjoint bins
  """
  col_width, row_width = __getBufferRegionSize(None, None) # TODO: should automatically choose a suitable buffer region size
  buffer_pblock = U250.getBufferRegionBetweenSlotPair(slot1_name, slot2_name, col_width, row_width)

  # convert the pblock representation of the buffer region into individul bins
  bins = []
  slice_regions = re.findall(r'SLICE_X\d+Y\d+[ ]*:[ ]*SLICE_X\d+Y\d+', buffer_pblock)
  for slice_region in slice_regions:
    match_res = re.findall(r'SLICE_X(\d+)Y(\d+)[ ]*:[ ]*SLICE_X(\d+)Y(\d+)', slice_region) # output format is [(val1, val2, val3, val4)]
    left_down_x, left_down_y, up_right_x, up_right_y = map(int, match_res[0])

    # note that the boundaries in pblocks are inclusive
    bins += [(x, y) for x in range(left_down_x, up_right_x + 1, bin_size_x) \
                    for y in range(left_down_y, up_right_y + 1, bin_size_y) ]

  # calibrate the positions
  bins_calibrated = [U250.getCalibratedCoordinates('SLICE', orig_x, orig_y) \
            for orig_x, orig_y in bins]

  return bins_calibrated


def __getEdgeCost(neighbor_cell_loc2types, FDRE_loc):
  """
  use the distance as the cost function
  If the target is a LUT, we add a penalty to the distance
  """
  dist = lambda loc1, loc2 : abs(loc1[0] -loc2[0]) + abs(loc1[1] - loc2[1])
  lut_penalty = lambda types : 3 if any('LUT' in type for type in types) else 1

  dists = [dist(cell_loc, FDRE_loc) * lut_penalty(types) for cell_loc, types in neighbor_cell_loc2types.items()]

  # the total wire length
  dist_score = sum(dists) / len(neighbor_cell_loc2types)

  # want the anchor to be near the mid point
  unbalance_penalty = max(dists) - min(dists)
  weight = 1

  # TODO: maybe penalize extreme long wires

  final_score = dist_score + weight * unbalance_penalty

  return final_score

def __getILPResults(anchor2bin2var):
  """
  interpret the ILP solving results. Map anchor to locations
  """
  anchor_2_slice_xy = {}
  for anchor, bin2var in anchor2bin2var.items():
    for bin, var in bin2var.items():
      var_value = round(var.x)
      assert abs(var.x - var_value) < 0.000001, var.x # check that we are correctly treating each ILP var as CONTINOUS

      if var_value == 1:
        # get the original coordinates
        orig_x = U250.getSliceOrigXCoordinates(bin[0])
        orig_y = bin[1]

        anchor_2_slice_xy[anchor] = (orig_x, orig_y)

  return anchor_2_slice_xy

def __ILPSolving(anchor_connections, bins, allowed_usage_per_bin):
  """
  set up and solve the weight matching ILP
  """
  start_time = time.perf_counter()
  get_time_stamp = lambda : time.perf_counter() - start_time

  m = Model()

  logging.info(f'calculate bin cost... {get_time_stamp()}')
  anchor2bin2cost = {} # for each anchor, the cost of each bin

  for anchor in anchor_connections.keys():
    bin2cost = {bin : __getEdgeCost(anchor_connections[anchor], bin) for bin in bins }
    anchor2bin2cost[anchor] = bin2cost

  # create ILP variables.
  # Note that we use the CONTINOUS type due to this special case
  logging.info(f'create ILP variables... {get_time_stamp()}')
  anchor2bin2var = {}
  for anchor in anchor_connections.keys():
    bin2var = {bin : m.add_var(var_type=CONTINUOUS, lb=0, ub=1) for bin in bins}
    anchor2bin2var[anchor] = bin2var

  bin2anchor2var = defaultdict(dict)
  for anchor, bin2var in anchor2bin2var.items():
    for bin, var in bin2var.items():
      bin2anchor2var[bin][anchor] = var

  # each anchor is placed once
  logging.info(f'adding constraints... {get_time_stamp()}')
  for anchor in anchor_connections.keys():
    bin2var = anchor2bin2var[anchor]
    m += xsum(var for var in bin2var.values()) == 1

  # limit on bin size
  for bin, anchor2var in bin2anchor2var.items():
    m += xsum(var for var in anchor2var.values()) <= allowed_usage_per_bin

  # objective
  var_and_cost = []
  for anchor, bin2cost in anchor2bin2cost.items():
    bin2var = anchor2bin2var[anchor]
    for bin in bin2cost.keys():
      var_and_cost.append((bin2var[bin], bin2cost[bin]))
  m.objective = minimize(xsum(var * cost for var, cost in var_and_cost))

  logging.info(f'start the solving process... {get_time_stamp()}')
  m.optimize()
  logging.info(f'finish the solving process... {get_time_stamp()}')

  return __getILPResults(anchor2bin2var)


def runILPWeightMatchingPlacement(pair_name, anchor_connections):
  """
  formulate the anchor placement algo as a weight matching problem.
  Quantize the buffer region into separate bins and assign a cost for each bin
  minimize the total cost.
  Note that we could use CONTINOUS ILP variables in this special case
  anchor_connections: anchor_name -> coordinates -> type(s)
  """
  slot1_name, slot2_name = pair_name.split('_AND_')

  # set up the bins
  # bin_size_x = 1 && bin_size_y = 1 means that we treat each SLICE as a bin
  bin_size_x = 1
  bin_size_y = 1
  num_FDRE_per_SLICE = 16
  bin_size = bin_size_x * bin_size_y * num_FDRE_per_SLICE

  # note that the coordinates of the bins are calibrated
  # need to convert back to the original coordinates at the end
  bins = __getWeightMatchingBins(slot1_name, slot2_name, bin_size_x, bin_size_y)

  # set up allowd
  num_anchor = len(anchor_connections)
  num_FDRE = len(bins) * bin_size
  total_usage_percent = num_anchor / num_FDRE
  max_usage_ratio_per_bin = 0.5 if total_usage_percent < 0.4 else total_usage_percent + 0.1
  assert total_usage_percent < 0.9, f'{pair_name}: buffer region too crowded! {num_anchor} / {num_FDRE} = {num_anchor/num_FDRE}'

  # seems that this num must be integer, otherwise we cannot treat each ILP var as CONTINOUS
  allowed_usage_per_bin = round(bin_size * max_usage_ratio_per_bin) 

  logging.info(f'num_FDRE: {num_FDRE}')
  logging.info(f'num_anchor: {num_anchor}')
  logging.info(f'total_usage_percent: {total_usage_percent}')
  logging.info(f'allowed_usage_per_bin: {allowed_usage_per_bin}')

  # run the ILP model and write out the results
  anchor_2_slice_xy = __ILPSolving(anchor_connections, bins, allowed_usage_per_bin)
  return anchor_2_slice_xy

  

######################### update placement results ############################################

def moveAnchorsOntoLagunaSites(hub, anchor_2_slice_xy, slot1_name, slot2_name):
  """
  for an SLR-crossing pair, move the anchor registers to the nearby laguna sites
  (1) determine the direction of each anchor: anchor_2_sll_dir
  get the io_name2dir dict for each slot
  for the slot on the top, an output anchor is a downward anchor and an input anchor is an upward anchor

  (2) determine if an anchor should go to TX or RX: anchor2TXorRX
  if a downward anchor is at the up side, assign to TX
  if a downward anchor is at the down side, assign to RX
  if a upward anchor is at the up side, assign to RX
  if a upward anchor is at the down side, assign to TX

  (3) determine the specific laguna reg for each anchor: anchor2laguna
  if an anchor is at the up side, use the SLL from large index to small index
  if an anchor is at the down side, use the SLL from small index to large index
  assert that at most 12 FDREs can be placed into the same SLICE site
  """

  def __is_slr_crossing_pair():
    slot1 = Slot(U250_inst, slot1_name)
    slot2 = Slot(U250_inst, slot2_name)

    if slot1.down_left_x != slot2.down_left_x:
      return False
    else:
      up_slot = slot1 if slot1.down_left_y > slot2.down_left_y else slot2
      if not any(y == up_slot.down_left_y for y in [4, 8, 12]):
        return False
      else:
        return True

        
  def __get_anchor_2_sll_dir():
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
    for anchor in anchor_2_slice_xy.keys():
      hls_var_name = anchor.split('_q0_reg')[0]
      anchor_2_sll_dir[anchor] = slot_io_2_sll_dir[hls_var_name]

    return anchor_2_sll_dir


  def __get_anchor_2_top_or_bottom():
    """
    whether an anchor is placed at the upper or the lower SLR
    """
    get_top_or_bottom = lambda slice_y : 'TOP' if any(bot <= slice_y <= bot + 59 for bot in [240, 480, 720]) else 'BOTTOM'
    anchor_2_top_or_bottom = {anchor : get_top_or_bottom(slice_xy[1]) for anchor, slice_xy in anchor_2_slice_xy.items()}
    return anchor_2_top_or_bottom


  def __get_anchor_2_tx_or_rx():
    """
    whether an anchor will be place at the RX or TX laguna register
    """
    anchor_2_tx_or_rx = {}
    for anchor in anchor_2_slice_xy.keys():
      if anchor_2_sll_dir[anchor] == 'UP' and anchor_2_top_or_bottom[anchor] == 'BOTTOM':
        choice = 'TX'
      elif  anchor_2_sll_dir[anchor] == 'UP' and anchor_2_top_or_bottom[anchor] == 'TOP':
        choice = 'RX'
      elif  anchor_2_sll_dir[anchor] == 'DOWN' and anchor_2_top_or_bottom[anchor] == 'BOTTOM':
        choice = 'RX'
      elif  anchor_2_sll_dir[anchor] == 'DOWN' and anchor_2_top_or_bottom[anchor] == 'TOP':
        choice = 'TX'
      else:
        assert False
      anchor_2_tx_or_rx[anchor] = choice

    return anchor_2_tx_or_rx


  def __get_laguna_block_2_anchor_list():
    """
    each SLICE site corresponds to 4 laguna sites, and we call them a laguna block
    get the mapping from each laguna block to all anchors to be placed on this block
    """
    idx_of_right_side_slice_of_laguna_column = [x + 2 for x in U250.idx_of_left_side_slice_of_laguna_column]
    # note that each laguna column has 2 units in Y dimension
    right_slice_x_2_laguna_x = {idx : i * 2 for i, idx in enumerate(idx_of_right_side_slice_of_laguna_column)}

    def __get_nearest_laguna_y(slice_y):
      if 180 <= slice_y <= 299:
        laguna_y = (slice_y - 180) * 2 + 120
      elif 420 <= slice_y <= 539:
        laguna_y = (slice_y - 420) * 2 + 360
      elif 660 <= slice_y <= 779:
        laguna_y = (slice_y - 660) * 2 + 600
      else:
        assert False
      return laguna_y

    slice_xy_2_anchor_list = defaultdict(list)
    for anchor, slice_xy in anchor_2_slice_xy.items():
      slice_xy_2_anchor_list[slice_xy].append(anchor)

    laguna_block_2_anchor_list = {}
    slice_xy_2_laguna_block = {}
    for slice_xy, anchor_list in slice_xy_2_anchor_list.items():
      first_laguna_x = right_slice_x_2_laguna_x[slice_xy[0]]
      first_laguna_y = __get_nearest_laguna_y(slice_xy[1])
      laguna_block_2_anchor_list[(first_laguna_x, first_laguna_y)] = anchor_list
      slice_xy_2_laguna_block[f'SLICE_X{slice_xy[0]}Y{slice_xy[1]}'] = f'LAGUNA_X{first_laguna_x}Y{first_laguna_y}'

    laguna_block_str_2_anchor_list = {f'LAGUNA_X{xy[0]}Y{xy[1]}' : anchor_list for xy, anchor_list in laguna_block_2_anchor_list.items()}
    open('laguna_block_2_anchor_list.json', 'w').write(json.dumps(laguna_block_str_2_anchor_list, indent=2))
    open('slice_xy_2_laguna_block.json', 'w').write(json.dumps(slice_xy_2_laguna_block, indent=2))

    return laguna_block_2_anchor_list


  def __get_anchor_to_laguna():
    """
    the general ILP placement map anchors to SLICE sites, but each SLICE corresponds to 4 laguna sites.
    Need to map each anchor to a specific laguna.
    Note that the laguna registers are paired up. 
    The strategy is that for the upper SLR anchors, we choose the sites with X == 0 in the "laguna block"
    Likewise we choose the lagunas with X == 1 in the laguna block for lower SLR anchors.
    """
    # there are 4 laguna sites for each slice site. Each site corresponds to 6 SLL wires. Each SLL wire connects two laguna sites. 
    anchor_2_laguna = {}
    num_sll_per_laguna = 6
    for laguna_block_xy, anchor_list in laguna_block_2_anchor_list.items():
      top_or_bottom = anchor_2_top_or_bottom[anchor_list[0]]
      for i, anchor in enumerate(anchor_list):
        if top_or_bottom == 'TOP': # avoid SLL conflict
          X = laguna_block_xy[0] 
          Y = laguna_block_xy[1] + int(i / num_sll_per_laguna)
        elif top_or_bottom == 'BOTTOM':
          X = laguna_block_xy[0] + 1
          Y = laguna_block_xy[1] + int(i / num_sll_per_laguna)
        else:
          assert False

        site_name = f'LAGUNA_X{X}Y{Y}'
        tx_or_rx = anchor_2_tx_or_rx[anchor]
        bel_name = f'{tx_or_rx}_REG{i % num_sll_per_laguna}'
        anchor_2_laguna[anchor] = f'{site_name}/{bel_name}'

    return anchor_2_laguna

  def  __laguna_rule_check():
    """
    check that each SLL is only used by one anchor register
    """
    laguna_2_anchor = {laguna : anchor for anchor, laguna in anchor_2_laguna.items()}
    for laguna in laguna_2_anchor.keys():
      match = re.search(r'LAGUNA_X(\d+)Y(\d+)/.X_REG(\d)', laguna)
      x = int(match.group(1))
      y = int(match.group(2))
      reg = int(match.group(3))

      if f'LAGUNA_X{x}Y{y+120}/TX_REG{reg}'  in laguna_2_anchor or \
         f'LAGUNA_X{x}Y{y+120}/RX_REG{reg}'  in laguna_2_anchor or \
         f'LAGUNA_X{x}Y{y-120}/TX_REG{reg}'  in laguna_2_anchor or \
         f'LAGUNA_X{x}Y{y-120}/RX_REG{reg}'  in laguna_2_anchor:
        assert False

  # ---------- main ----------#

  if not __is_slr_crossing_pair():
    return {anchor : f'SLICE_X{xy[0]}Y{xy[1]}' for anchor, xy in anchor_2_slice_xy.items() }

  anchor_2_sll_dir = __get_anchor_2_sll_dir()
  anchor_2_top_or_bottom = __get_anchor_2_top_or_bottom()
  anchor_2_tx_or_rx =  __get_anchor_2_tx_or_rx()
  laguna_block_2_anchor_list = __get_laguna_block_2_anchor_list()
  anchor_2_laguna = __get_anchor_to_laguna()

  __laguna_rule_check()

  return anchor_2_laguna



##################### helper #####################################


def writePlacementResults(anchor_2_loc):
  """
  write out the results as a tcl file to place the anchors into the calculated positions
  """
  f = open('place_anchors.tcl', 'w')
  f.write('place_cell { \\\n')
  for anchor, loc in anchor_2_loc.items():
    f.write(f'  {anchor} {loc} \\\n') # note that spaces are not allowed after \
  f.write('}\n')
  f.close()


def collectAllConnectionsOfTargetAnchors(pair_name):
  """
  for a pair of anchors, collect all connections of the anchors in between the two slots
  """  
  slot1_name, slot2_name = pair_name.split('_AND_')
  connection1 = json.loads(open(get_anchor_connection_path(slot1_name), 'r').read())
  connection2 = json.loads(open(get_anchor_connection_path(slot2_name), 'r').read())

  # get the common anchors
  common_anchor_connections = {} # anchor_reg_name -> site_coordinates -> all types of the cells in this site
  for anchor, locs_part1 in connection1.items():
    if anchor in connection2:
      locs_part2 = connection2[anchor]
      site_name2types = defaultdict(list)

      for site_name_and_type in locs_part1 + locs_part2:
        [(site_name, type)] = site_name_and_type.items()

        # convert the site name to coordinates
        site_coordinate = U250.getCalibratedCoordinatesFromSiteName(site_name)
        site_name2types[site_coordinate].append(type)

      assert(site_name2types)
      common_anchor_connections[anchor] = dict(site_name2types)

  return common_anchor_connections

def setupAnchorPlacement(hub):
  """
  poll on if the initial placement of each slot has finished
  If two slots of a pair are both ready, start the ILP anchor placement
  """
  tasks = []
  for slot1_name, slot2_name in hub["AllSlotPairs"]:
    pair_name = f'{slot1_name}_AND_{slot2_name}'
    os.mkdir(f'{anchor_placement_dir}/{pair_name}')
    
    guard1 = f'until [ -f {get_anchor_connection_path(slot1_name)}.done.flag ]; do sleep 10; done'
    guard2 = f'until [ -f {get_anchor_connection_path(slot2_name)}.done.flag ]; do sleep 10; done'

    ilp_placement = f'python3.6 -m autoparallel.BE.PairwiseAnchorPlacement {hub_path} {base_dir} RUN {iter} {pair_name}'

    touch_flag = f'touch {anchor_placement_dir}/{pair_name}/place_anchors.tcl.done.flag'

    tasks.append(f'cd {anchor_placement_dir}/{pair_name} && {guard1} && {guard2} && {ilp_placement} && {touch_flag}')

  open(f'{anchor_placement_dir}/parallel-ilp-placement-iter{iter}.txt', 'w').write('\n'.join(tasks))


def setupSlotClockRouting(anchor_2_loc):
  """
  help setup the clock routing for the slots
  create/place all anchor cells and connect them with clock
  """
  script = []
  
  # create cells
  script.append('create_cell -reference FDRE { \\')
  for anchor in anchor_2_loc.keys():
    script.append(f'  {anchor} \\') # note that spaces are not allowed after \
  script.append('}')

  # place cells
  script.append('place_cell { \\')
  for anchor, loc in anchor_2_loc.items():
    script.append(f'  {anchor} {loc} \\') # note that spaces are not allowed after \
  script.append('}')
  
  # connect to clock
  script.append('connect_net -net ap_clk -objects { \\')
  for anchor in anchor_2_loc.keys():
    script.append(f'  {anchor}/C \\') # note that spaces are not allowed after \
  script.append('}')

  open('create_and_place_anchors_for_clock_routing.tcl', 'w').write('\n'.join(script))


if __name__ == '__main__':
  assert len(sys.argv) >= 5, 'input (1) the path to the front end result file; (2) the target directory; (3) which action; (4) which iteration'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  option = sys.argv[3]
  iter = int(sys.argv[4])
  hub = json.loads(open(hub_path, 'r').read())

  loggingSetup()

  if iter == 0:
    get_anchor_connection_path = lambda slot_name : f'{base_dir}/parallel_run/{slot_name}/anchor_connections.json'
  else:
    get_anchor_connection_path = lambda slot_name : f'{base_dir}/placement_opt_iter{iter}/{slot_name}/anchor_connections.json'

  anchor_placement_dir = f'{base_dir}/ILP_anchor_placement_iter{iter}'

  # run this before the ILP anchor placement, setup for the later steps
  if option == 'SETUP':
    os.mkdir(anchor_placement_dir)    
    setupAnchorPlacement(hub)

  # run the ILP placement for the given slot pairs
  elif option == 'RUN':
    pair_name = sys.argv[5]
    common_anchor_connections = collectAllConnectionsOfTargetAnchors(pair_name) 
    anchor_2_slice_xy = runILPWeightMatchingPlacement(pair_name, common_anchor_connections)

    slot1_name, slot2_name = pair_name.split('_AND_')
    anchor_2_loc = moveAnchorsOntoLagunaSites(hub, anchor_2_slice_xy, slot1_name, slot2_name)
    writePlacementResults(anchor_2_loc)
    
    setupSlotClockRouting(anchor_2_loc)
    
  else:
    assert False, f'unrecognized option {option}'