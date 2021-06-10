import sys
import json
import os
from autoparallel.BE.CreatePairwiseWrapper import getPairWrapper

def updateClock(pair_wrapper):
  """
  insert the clock buffer into the wrapper RTL
  """
  for i in range(len(pair_wrapper)):
    if 'input ap_clk' in pair_wrapper[i]:
      pair_wrapper[i] = '    input ap_clk_port,'
      break

  for i in range(len(pair_wrapper)):
    if ');' in pair_wrapper[i] and ('input' in pair_wrapper[i] or 'output' in pair_wrapper[i]):
      pair_wrapper[i] += '''
  wire ap_clk; 
  (* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg ( 
    .I(ap_clk_port), 
    .CE(1'b1),
    .O(ap_clk) 
  );      
'''

  return pair_wrapper

def updateNaming(pair_wrapper, slot1_name, slot2_name):
  """
  after we prune the anchors from the anchored wrapper,
  the REF_NAME of the cell is still XXX_anchored
  """
  targets = [
    f'(* black_box *) {slot1_name}',
    f'(* black_box *) {slot2_name}',
    f'module {slot1_name}',
    f'module {slot2_name}'
  ]

  for target in targets:
    for i in range(len(pair_wrapper)):
      if target + ' ' in pair_wrapper[i]:
        pair_wrapper[i] = pair_wrapper[i].replace(target, f'{target}_anchored')
        break

  return pair_wrapper

def getVivadoScriptForSlotPair(
    hub, 
    wrapper_name,
    slot1_name,
    slot2_name):
  fpga_part_name = hub["FPGA_PART_NAME"]

  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'read_verilog "{test_dir}/{wrapper_name}/wrapper.v"')  

  # clock xdc
  script.append(f'read_xdc "{base_dir}/global_stitch/final_top_clk.xdc"')

  # synth
  script.append(f'synth_design -top "{wrapper_name}" -part {fpga_part_name} -mode out_of_context')

  # read in the dcp of slots
  script.append(f'read_checkpoint -cell {slot1_name}_U0 {base_dir}/pruning_anchors/{slot1_name}/{slot1_name}_after_pruning_anchors.dcp')
  script.append(f'read_checkpoint -cell {slot2_name}_U0 {base_dir}/pruning_anchors/{slot2_name}/{slot2_name}_after_pruning_anchors.dcp')

  # place the anchors
  script.append(f'source {base_dir}/ILP_anchor_placement_iter0/{wrapper_name}/place_anchors.tcl')

  # add clock stem
  script.append(f'set_property ROUTE "" [get_nets ap_clk]')
  script.append(f'source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl')
  script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

  script.append(f'write_checkpoint -force {wrapper_name}_before_routed.dcp')

  # Using Quick will result in bad results...
  script.append(f'route_design -preserve -directive Quick')

  # unroute
  script.append(f'set conflict_nets [get_nets -hierarchical -regexp -top_net_of_hierarchical_group -filter {{ ROUTE_STATUS == "CONFLICTS" }} ]')
  script.append(f'route_design -unroute -nets $conflict_nets')

  script.append(f'set anchor_region_cells [get_cells -hierarchical -regexp -filter {{ PBLOCK == "" && PRIMITIVE_TYPE !~ OTHERS.*.* }} ]')
  script.append(f'route_design -unroute -nets [get_nets -of_objects $anchor_region_cells]')
  
  # Re-route
  script.append(f'route_design -preserve')

  script.append(f'write_checkpoint -force {wrapper_name}_routed.dcp')

  return script

if __name__ == '__main__':
  assert len(sys.argv) >= 3, 'input (1) the path to the front end result file; (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  test_dir = f'{base_dir}/test_pairwise_route_stitching'
  os.mkdir(test_dir)

  hub = json.loads(open(hub_path, 'r').read())
  pair_list = hub["AllSlotPairs"]
  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  all_tasks = []
  for pair in pair_list:
    wrapper_name = '_AND_'.join(pair)
    wrapper_dir = f'{test_dir}/{wrapper_name}'
    os.mkdir(wrapper_dir)

    pair_wrapper, _ = getPairWrapper(hub, pair[0], pair[1], 1, in_slot_pipeline_style)
    wrapper_updated_name = updateNaming(pair_wrapper, pair[0], pair[1])
    wrapper_updated_clock = updateClock(wrapper_updated_name)

    open(f'{wrapper_dir}/wrapper.v', 'w').write('\n'.join(wrapper_updated_clock))

    script = getVivadoScriptForSlotPair(hub, wrapper_name, pair[0], pair[1])
    open(f'{wrapper_dir}/route_pair.tcl', 'w').write('\n'.join(script))

    all_tasks.append(f'cd {wrapper_dir} && VIV_VER=2020.1 vivado -mode batch -source route_pair.tcl')

  open(f'{test_dir}/parallel-route-pairs.txt', 'w').write('\n'.join(all_tasks))