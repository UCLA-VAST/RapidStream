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


def runILPWeightMatchingPlacement(pair_name, anchor_connection_json_path):
  """
  formulate the anchor placement algo as a weight matching problem.
  Quantize the buffer region into separate bins and assign a cost for each bin
  minimize the total cost.
  Note that we could use CONTINOUS ILP variables in this special case
  """
  slot1_name, slot2_name = pair_name.split('_AND_')
  anchor_connections = json.loads(open(anchor_connection_json_path, 'r').read())

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


def setupPairwiseILPAnchorPlacement(hub):
  """
  run an ILP for each pair of slots
  """
  pair_list = hub["AllSlotPairs"]
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    pair_dir = f'{ilp_dir}/' + wrapper_name
    os.mkdir(pair_dir)
    
    connection1 = json.loads(open(f'{extraction_dir}/{pair[0]}/anchor_connection.json', 'r').read())
    connection2 = json.loads(open(f'{extraction_dir}/{pair[1]}/anchor_connection.json', 'r').read())

    # get the common anchors
    common_anchor_connections = {}
    for anchor, locs_part1 in connection1.items():
      if anchor in connection2:
        locs_part2 = connection2[anchor]
        common_anchor_connections[anchor] = locs_part1 + locs_part2

    open(f'{pair_dir}/common_anchor_connections.json', 'w').write(json.dumps(common_anchor_connections, indent=2))


def setupAnchorConnectionExtraction(hub, get_slot_dcp_path, anchor_connection_extraction_script_path):
  """
  open each placed slot, extract which cells connect to the anchors
  """
  tasks = []
  for slot_name in hub['SlotIO'].keys():
    result_dir = f'{extraction_dir}/{slot_name}'
    src_dcp_path = get_slot_dcp_path(slot_name)

    os.mkdir(result_dir)

    script = []
    script.append(f'open_checkpoint {src_dcp_path}')
    script.append(f'source {anchor_connection_extraction_script_path}')

    open(f'{result_dir}/extract_anchor_connection.tcl', 'w').write('\n'.join(script))

    tasks.append(f'cd {result_dir} && VIV_VER=2020.1 vivado -mode batch -source extract_anchor_connection.tcl')

  open(f'{extraction_dir}/parallel-extraction.txt', 'w').write('\n'.join(tasks))


if __name__ == '__main__':
  assert len(sys.argv) >= 4, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  option = sys.argv[3]
  hub = json.loads(open(hub_path, 'r').read())

  anchor_placement_dir = f'{base_dir}/parallel_ILP_anchor_placement'
  ilp_dir = f'{anchor_placement_dir}/ilp_placement'
  extraction_dir = f'{anchor_placement_dir}/connection_extraction'

  if option == 'SetupAnchorConnectionExtraction':
    os.mkdir(anchor_placement_dir)
    os.mkdir(extraction_dir)
    os.mkdir(ilp_dir)

    current_path = os.path.dirname(os.path.realpath(__file__))
    extraction_script_path = f'{current_path}/../../../tcl/extractSrcAndDstOfAnchors.tcl'

    slot_placement_dir = f'{base_dir}/parallel_run'
    get_slot_dcp_path = lambda slot_name : f'{slot_placement_dir}/{slot_name}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp'
    setupAnchorConnectionExtraction(hub, anchor_placement_dir, get_slot_dcp_path, extraction_script_path)

  elif option == 'MergeAnchorConnectionForSlotPairs':
    setupPairwiseILPAnchorPlacement(hub)

  elif option == 'WeightMatchPlacement':
    pair_name = sys.argv[4]
    anchor_connection_json = f'{ilp_dir}/{pair_name}/common_anchor_connections.json'
    runILPWeightMatchingPlacement(pair_name, anchor_connection_json)

  else:
    assert False, f'unrecognized option {option}'