import os
from autoparallel.BE.UniversalWrapperCreater import getWrapperOfSlots
from autoparallel.BE.Utilities import getSlotsInSLRIndex


def getTopLevelWrapperForSLRSlots(top_stitch_dir, slr_name_2_dir_and_width_and_io_name):
  """
  the final top RTL that stitch together the SLR-level checkpoints
  """
  top_wrapper, _, __ = getWrapperOfSlots('top', slr_name_2_dir_and_width_and_io_name, pipeline_level=1)
  open(f'{top_stitch_dir}/top.v', 'w').write('\n'.join(top_wrapper))


def getInterSLRPairs(hub, slr_num):
  """
  find all slot pairs that cross a SLR boundary
  """
  slr_index_2_slots = [getSlotsInSLRIndex(hub, i) for i in range(slr_num)]
  pair_list = hub['AllSlotPairs']

  inter_slr_pairs = []
  for i in range(slr_num-1):
    for pair in pair_list:
      if  (pair[0] in slr_index_2_slots[i]) != (pair[1] in slr_index_2_slots[i]):
        inter_slr_pairs.append("_AND_".join(pair))  
  inter_slr_pairs = list(set(inter_slr_pairs))

  return inter_slr_pairs


def getTopStitchScript(base_dir, hub, slr_num, slr_stitch_dir, top_stitch_dir, get_slr_dcp_path, anchor_placement_dir):
  """
  get the final checkpoint
  """
  fpga_part_name = hub["FPGA_PART_NAME"]
  pair_list = hub['AllSlotPairs']

  script = []

  script.append(f'set_part {fpga_part_name}')
  script.append(f'read_verilog "{top_stitch_dir}/top.v"')  
  script.append(f'read_xdc "{base_dir}/global_stitch/final_top_clk.xdc"')

  # synth
  script.append(f'synth_design -top "top" -part {fpga_part_name} -mode out_of_context')

  # read in the dcp of SLRs
  for slr_index in range(slr_num):
    script.append(f'read_checkpoint -cell slr_{slr_index}_U0 {get_slr_dcp_path(slr_index)}')

  # place the anchors
  inter_slr_pairs = getInterSLRPairs(hub, slr_num)
  for pair_name in inter_slr_pairs:
    anchor_placement_tcl = f'{anchor_placement_dir}/{pair_name}/place_anchors.tcl'
    script.append(f'source {anchor_placement_tcl}')

  # reuse the laguna anchor routes
  for slr_index in range(slr_num):
    script.append(f'source {slr_stitch_dir}/slr_{slr_index}/add_slr_{slr_index}_laguna_route.tcl')

  # add clock stem
  script.append(f'set_property ROUTE "" [get_nets ap_clk]')
  script.append(f'source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl')
  script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

  # SLR boundary should serve as a natural boundary
  script.append(f'delete_pblocks *')

  # theoretically there should be non conflict nets. But we do see the GND net may cause conflicts
  script.append(f'report_route_status')
  script.append(f'write_checkpoint -force top.dcp')

  open(f'{top_stitch_dir}/stitch.tcl', 'w').write('\n'.join(script))


def setupTopStitch(base_dir, hub, slr_name_2_dir_and_width_and_io_name):
  slr_stitch_dir = f'{base_dir}/SLR_level_stitch'
  anchor_placement_dir = f'{base_dir}/ILP_anchor_placement_iter0'
  top_stitch_dir = f'{base_dir}/top_stitch'
  os.mkdir(top_stitch_dir)

  get_slr_dcp_path = lambda slr_index : f'{slr_stitch_dir}/slr_{slr_index}/unset_dcp_hd_reconfigurable/slr_{slr_index}_U0.dcp'

  slr_num = len(slr_name_2_dir_and_width_and_io_name)
  getTopLevelWrapperForSLRSlots(top_stitch_dir, slr_name_2_dir_and_width_and_io_name)
  getTopStitchScript(base_dir, hub, slr_num, slr_stitch_dir, top_stitch_dir, get_slr_dcp_path, anchor_placement_dir)

