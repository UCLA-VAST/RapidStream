import sys
import json
import os
import re
from autoparallel.BE.CreatePairwiseWrapper import getPairWrapper

def insertAnchorForAllTopIOs(pair_wrapper):
  """
  temporary hack to insert anchor registers for IOs as well
  """
  # first collect the inputs and the outputs
  is_top_io = lambda line : any(kw in line for kw in ['input ap_clk', '_axi_', 'ap_rst_n,', 'interrupt'])
  input_decl = []
  output_decl = []
  for line in pair_wrapper:
    if is_top_io(line):
      continue
    elif 'input ' in line:
      input_decl.append(line)
    elif 'output ' in line:
      output_decl.append(line)
    elif  'wire ' in line or 'reg ' in line:
      break
    
  num_line = len(pair_wrapper)
  # update the IO name
  for i in range(num_line):
    if is_top_io(pair_wrapper[i]):
      continue
    if 'input ' in pair_wrapper[i]:
      pair_wrapper[i] = pair_wrapper[i].replace(',', '_in_io,').replace(');', '_in_io);')
    elif 'output ' in pair_wrapper[i]:
      pair_wrapper[i] = pair_wrapper[i].replace(',', '_out_io,').replace(');', '_out_io);')
    elif 'wire ' in pair_wrapper[i] or 'reg ' in pair_wrapper[i]:
      break

  # add anchor declaration
  io_anchor_decl = []
  io_anchor_decl += [decl.replace('input', '(* dont_touch = "yes" *) reg').replace(',', '_q0;').replace(');', '_q0;') for decl in input_decl]
  io_anchor_decl += [decl.replace('output', '(* dont_touch = "yes" *) reg').replace(',', '_q0;').replace(');', '_q0;') for decl in output_decl]

  # add internal anchor net declaration
  inner_io_net_decl = []
  inner_io_net_decl += [decl.replace('input', 'wire').replace(',', ';').replace(');', ';') for decl in input_decl]
  inner_io_net_decl += [decl.replace('output', 'wire').replace(',', ';').replace(');', ';') for decl in output_decl]

  # connect the io anchors
  input_names = [re.search(r' ([^ ]*)(,|\);)', line).group(1) for line in input_decl]
  output_names = [re.search(r' ([^ ]*)(,|\);)', line).group(1) for line in output_decl]
  io_anchor_connect = []
  io_anchor_connect += [f'always @ (posedge ap_clk) {in_name}_q0 <= {in_name}_in_io;' for in_name in input_names]
  io_anchor_connect += [f'assign {in_name} = {in_name}_q0;' for in_name in input_names]
  io_anchor_connect += [f'always @ (posedge ap_clk) {out_name}_q0 <= {out_name};' for out_name in output_names]
  io_anchor_connect += [f'assign {out_name}_out_io = {out_name}_q0;' for out_name in output_names]

  for i in range(num_line):
    if 'wire ap_clk;' in pair_wrapper[i]:
      pair_wrapper[i+1:i+1] = inner_io_net_decl + io_anchor_decl + io_anchor_connect
      break

  return pair_wrapper

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
      pair_wrapper[i+1:i+1] = [
        '  wire ap_clk;' ,
        '  (* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg (' ,
        '    .I(ap_clk_port),' ,
        '    .CE(1\'b1),',
        '    .O(ap_clk)',
        '  ); '     
      ]
      break

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
  pair_list = hub['AllSlotPairs']

  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'read_verilog "{test_dir}/{wrapper_name}/wrapper.v"')  

  # clock xdc
  script.append(f'read_xdc "{base_dir}/global_stitch/final_top_clk.xdc"')

  # synth
  script.append(f'synth_design -top "{wrapper_name}" -part {fpga_part_name} -mode out_of_context')

  # read in the dcp of slots
  script.append(f'read_checkpoint -cell {slot1_name}_U0 {get_pruned_dcp_path(slot1_name)}')
  script.append(f'read_checkpoint -cell {slot2_name}_U0 {get_pruned_dcp_path(slot1_name)}')

  # place the anchors
  for pair in pair_list:
    if slot1_name in pair or slot2_name in pair:
      
      script.append(f'source -notrace {base_dir}/ILP_anchor_placement_iter0/{"_AND_".join(pair)}/place_anchors.tcl')

  # add clock stem
  script.append(f'set_property ROUTE "" [get_nets ap_clk]')
  script.append(f'source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl')
  script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

  # the final stitching in preserve mode is not constrained by the pblock
  script.append(f'delete_pblocks *')

  # theoretically there should be non conflict nets. But we do see the GND net may cause conflicts
  script.append(f'route_design -unroute -nets [get_nets -hierarchical -filter {{ ROUTE_STATUS == "CONFLICTS" }}]')

  script.append(f'write_checkpoint -force {wrapper_name}_before_routed.dcp')

  script.append(f'route_design -preserve')

  script.append(f'write_checkpoint -force {wrapper_name}_routed.dcp')

  return script

if __name__ == '__main__':
  assert len(sys.argv) >= 3, 'input (1) the path to the front end result file; (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  test_dir = f'{base_dir}/test_pairwise_route_stitching'
  get_pruned_dcp_path = lambda slot_name : f'{base_dir}/slot_routing/{slot_name}/unset_dcp_ooc/phys_opt_routed_with_ooc_clock.dcp'
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
    wrapper_all_anchored = insertAnchorForAllTopIOs(wrapper_updated_clock)

    open(f'{wrapper_dir}/wrapper.v', 'w').write('\n'.join(wrapper_all_anchored))

    script = getVivadoScriptForSlotPair(hub, wrapper_name, pair[0], pair[1])
    open(f'{wrapper_dir}/route_pair.tcl', 'w').write('\n'.join(script))

    all_tasks.append(f'cd {wrapper_dir} && VIV_VER=2020.1 vivado -mode batch -source route_pair.tcl')

  open(f'{test_dir}/parallel-route-pairs.txt', 'w').write('\n'.join(all_tasks))