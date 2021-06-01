import json
import re
import sys
import os
from collections import defaultdict
from mip import Model, minimize, CONTINUOUS, xsum
from autoparallel.BE.GenAnchorConstraints import __getBufferRegionSize
from autobridge.Device.DeviceManager import DeviceU250

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
    bins += [(x, y) for x in range(left_down_x, up_right_x, bin_size_x) \
                    for y in range(left_down_y, up_right_y, bin_size_y) ]

  return bins


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
  m = Model()

  anchor2bin2cost = {} # for each anchor, the cost of each bin

  for anchor in anchor_connections.keys():
    bin2cost = {bin : __getEdgeCost(anchor_connections[anchor], bin) for bin in bins }
    anchor2bin2cost[anchor] = bin2cost

  # create ILP variables.
  # Note that we use the CONTINOUS type due to this special case
  anchor2bin2var = {}
  for anchor in anchor_connections.keys():
    bin2var = {bin : m.add_var(var_type=CONTINUOUS, lb=0, ub=1) for bin in bins}
    anchor2bin2var[anchor] = bin2var

  bin2anchor2var = defaultdict(dict)
  for anchor, bin2var in anchor2bin2var.items():
    for bin, var in bin2var.items():
      bin2anchor2var[bin][anchor] = var

  # each anchor is placed once
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

  m.optimize()

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
  """
  slot1_name, slot2_name = pair_name.split('_AND_')

  # so far we assume the connected cells are all SLICE. not sure other types are possible
  assert all(loc.startswith('SLICE_') for locs in anchor_connections.values() for loc in locs)

  get_coord = lambda locs : [tuple(map(int, re.findall(r'[XY](\d+)', loc))) for loc in locs]
  anchor_connections = {anchor : get_coord(locs) for anchor, locs in anchor_connections.items()}

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
  assert total_usage_percent < 0.6, 'buffer region too crowded!'

  # seems that this num must be integer, otherwise we cannot treat each ILP var as CONTINOUS
  allowed_usage_per_bin = round(bin_size * max_usage_ratio_per_bin) 

  # run the ILP model and write out the results
  __ILPSolving(anchor_connections, bins, allowed_usage_per_bin)


def collectAllConnectionsOfTargetAnchors(pair_name):
  """
  for a pair of anchors, collect all connections of the anchors in between the two slots
  """
  pair_dir = f'{anchor_placement_dir}/' + pair_name
  os.mkdir(pair_dir)
  
  slot1_name, slot2_name = pair_name.split('_AND_')
  connection1 = json.loads(open(get_anchor_connection_path(slot1_name), 'r').read())
  connection2 = json.loads(open(get_anchor_connection_path(slot2_name), 'r').read())

  # get the common anchors
  common_anchor_connections = {}
  for anchor, locs_part1 in connection1.items():
    if anchor in connection2:
      locs_part2 = connection2[anchor]
      common_anchor_connections[anchor] = locs_part1 + locs_part2

  open(f'{pair_dir}/common_anchor_connections.json', 'w').write(json.dumps(common_anchor_connections, indent=2))
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

  if iter == 0:
    get_anchor_connection_path = lambda slot_name : f'{base_dir}/parallel_run/{slot_name}/{slot_name}_placed_free_run/anchor_connections.json'
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