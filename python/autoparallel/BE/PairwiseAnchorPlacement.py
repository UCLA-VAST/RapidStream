import json
import re
import sys
import os
import logging
import time
from collections import defaultdict, OrderedDict
from mip import Model, minimize, CONTINUOUS, xsum
from autoparallel.BE.GenAnchorConstraints import __getBufferRegionSize
from autoparallel.BE.BEManager import loggingSetup
from autobridge.Device.DeviceManager import DeviceU250
from autobridge.Device.ResourceMapU250 import ResourceMapU250

def __getWeightMatchingBins(slot1_name, slot2_name, bin_size_x, bin_size_y):
  """
  quantize the buffer region into disjoint bins
  """
  col_width, row_width = __getBufferRegionSize(None, None) # TODO: should automatically choose a suitable buffer region size
  buffer_pblock = DeviceU250.getBufferRegionBetweenSlotPair(slot1_name, slot2_name, col_width, row_width)

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
  resource_map_u250 = ResourceMapU250()
  bins_calibrated = [resource_map_u250.getCalibratedCoordinates('SLICE', orig_x, orig_y) \
            for orig_x, orig_y in bins]

  return bins_calibrated


def __getEdgeCost(neighbor_cell_locs, FDRE_loc):
  """
  use the distance as the cost function
  TODO: penalize long wires and congestion 
  """
  dist = lambda loc1, loc2 : abs(loc1[0] -loc2[0]) + abs(loc1[1] - loc2[1])
  return sum(dist(cell_loc, FDRE_loc) for cell_loc in neighbor_cell_locs) / len(neighbor_cell_locs)


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

  __writePlacementResults(anchor2bin2var)


def __writePlacementResults(anchor2bin2var):
  """
  write out the results as a tcl file to place the anchors into the calculated positions
  """
  f = open('result.tcl', 'w')
  f.write('place_cell { \\ \n')
  for anchor, bin2var in anchor2bin2var.items():
    for bin, var in bin2var.items():
      var_value = round(var.x)

      # check that we are correctly treating each ILP var as CONTINOUS
      assert abs(var.x - var_value) < 0.000001, var.x

      if var_value == 1:
        f.write(f'  {anchor} SLICE_X{bin[0]}Y{bin[1]} \\\n') # note that spaces are not allowed after \
  f.write('}\n')
  f.close()


def runILPWeightMatchingPlacement(pair_name, anchor_connections):
  """
  formulate the anchor placement algo as a weight matching problem.
  Quantize the buffer region into separate bins and assign a cost for each bin
  minimize the total cost.
  Note that we could use CONTINOUS ILP variables in this special case
  anchor_connections: anchor_name -> list of coordinates
  """
  slot1_name, slot2_name = pair_name.split('_AND_')

  # set up the bins
  # bin_size_x = 1 && bin_size_y = 1 means that we treat each SLICE as a bin
  bin_size_x = 1
  bin_size_y = 1
  num_FDRE_per_SLICE = 16
  bin_size = bin_size_x * bin_size_y * num_FDRE_per_SLICE
  bins = __getWeightMatchingBins(slot1_name, slot2_name, bin_size_x, bin_size_y)

  # set up allowd
  num_anchor = len(anchor_connections)
  num_FDRE = len(bins) * bin_size
  total_usage_percent = num_anchor / num_FDRE
  max_usage_ratio_per_bin = 0.5 if total_usage_percent < 0.4 else total_usage_percent + 0.1
  assert total_usage_percent < 0.7, f'{pair_name}: buffer region too crowded! {num_anchor} / {num_FDRE} = {num_anchor/num_FDRE}'

  # seems that this num must be integer, otherwise we cannot treat each ILP var as CONTINOUS
  allowed_usage_per_bin = round(bin_size * max_usage_ratio_per_bin) 

  logging.info(f'num_FDRE: {num_FDRE}')
  logging.info(f'num_anchor: {num_anchor}')
  logging.info(f'total_usage_percent: {total_usage_percent}')
  logging.info(f'allowed_usage_per_bin: {allowed_usage_per_bin}')

  # run the ILP model and write out the results
  __ILPSolving(anchor_connections, bins, allowed_usage_per_bin)


def __adjustConnectionFormat(common_anchor_connections):
  """
  The outputs of the connection extraction tcl may have some flaws.
  e.g. two site names in one entry: "SLICE_X139Y112 SLICE_X139Y112"
  Processing those flaws is easier in python.
  We remove duplicated site names and process the case where multiple site names are merged together
  In some corner cases, anchor may have empty connections
  """
  def adjust_format(anchor, connections):
    connections_splited = [site_name for site_names in connections for site_name in site_names.split(' ')]
    connections_deduplicated = list(set(connections_splited))
    
    # corner case: if the source of the ap_done anchor reg is a 1'b1, there may be no connections to the slot
    if any(site_name == "" for site_name in connections_deduplicated):
      assert 'ap_done_Boundary' in anchor
    
    connections_non_zero = [site_name for site_name in connections_deduplicated if site_name]

    return connections_non_zero


  return {anchor : adjust_format(anchor, connections) \
      for anchor, connections in common_anchor_connections.items()}

def collectAllConnectionsOfTargetAnchors(pair_name):
  """
  for a pair of anchors, collect all connections of the anchors in between the two slots
  """
  pair_dir = f'{anchor_placement_dir}/' + pair_name
  
  slot1_name, slot2_name = pair_name.split('_AND_')
  connection1 = json.loads(open(get_anchor_connection_path(slot1_name), 'r').read())
  connection2 = json.loads(open(get_anchor_connection_path(slot2_name), 'r').read())

  # get the common anchors
  common_anchor_connections = {} # anchor_reg_name -> list of site names
  for anchor, locs_part1 in connection1.items():
    if anchor in connection2:
      locs_part2 = connection2[anchor]

      # remove repetitives. Multiple destinations may be in the same site
      common_anchor_connections[anchor] = list(OrderedDict.fromkeys(locs_part1 + locs_part2))
  open(f'{pair_dir}/common_anchor_connections.json', 'w').write(json.dumps(common_anchor_connections, indent=2))
  
  # post processing corner cases not easily handled in tcl
  anchor_connection_adjusted = __adjustConnectionFormat(common_anchor_connections)
  open(f'{pair_dir}/common_anchor_connections_adjusted.json', 'w').write(json.dumps(anchor_connection_adjusted, indent=2))

  # convert the site name to coordinates
  resource_map_u250 = ResourceMapU250()
  anchor_connection_calibrated = {
    anchor : \
      [resource_map_u250.getCalibratedCoordinatesFromSiteName(site_name) for site_name in site_names] \
        for anchor, site_names in anchor_connection_adjusted.items()}
  
  return anchor_connection_calibrated

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

    touch_flag = f'touch {anchor_placement_dir}/{pair_name}/done.flag'

    tasks.append(f'cd {anchor_placement_dir}/{pair_name} && {guard1} && {guard2} && {ilp_placement} && {touch_flag}')

  open(f'{anchor_placement_dir}/parallel-ilp-placement-iter{iter}.txt', 'w').write('\n'.join(tasks))

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
    runILPWeightMatchingPlacement(pair_name, common_anchor_connections)
    
  else:
    assert False, f'unrecognized option {option}'