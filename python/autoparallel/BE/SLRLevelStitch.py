import sys
import json
import re
import os
from autoparallel.BE.UniversalWrapperCreater import getWrapperOfSlots, addAnchorToNonTopIOs

def getAnchorWrapperOfSLRWrapper(hub, slr_wrapper_name, external_io_name_2_dir_and_width):
  """
  add another layer of wrapper around the SLR-level wrapper to insert the anchor registers
  """
  io_list = [[*dir_and_width, io_name] \
    for io_name, dir_and_width in external_io_name_2_dir_and_width.items()]
  slr_anchor_wrapper = addAnchorToNonTopIOs(hub, slr_wrapper_name, io_list)
  return slr_anchor_wrapper


def getSlotsInSLRIndex(hub, slr_index):
  """
  get all slots within a given SLR
  """
  all_slot_names = hub['SlotIO'].keys()
  slots_in_slr = []
  for name in all_slot_names:
    match = re.search(r'CR_X(\d+)Y(\d+)_To_CR_X(\d+)Y(\d+)', name)
    DL_y = int(match.group(2))
    UR_y = int(match.group(4))

    # assume that each SLR has 4 rows of clock regions
    if slr_index * 4 <= DL_y <= slr_index * 4 + 3:
      if slr_index * 4 <= UR_y <= slr_index * 4 + 3:
        slots_in_slr.append(name)

  return slots_in_slr

def getSLRLevelWrapperWithIOAnchors(hub, slr_num):
  """
  get a wrapper for all slots within an SLR
  """
  get_io_name_2_dir_and_width = lambda slot_io_list : {io[-1] : io[0:-1] for io in slot_io_list}

  for slr_index in range(slr_num):
    os.mkdir(f'{slr_stitch_dir}/slr_{slr_index}')
    slr_slots = getSlotsInSLRIndex(hub, slr_index)
      
    slr_slot_name_2_dir_and_width_and_io_name = {
      f'{name}_ctrl' : get_io_name_2_dir_and_width(hub['SlotIO'][name]) for name in slr_slots}

    slr_wrapper, external_io_name_2_dir_and_width, _ = \
      getWrapperOfSlots(f'slr_{slr_index}', slr_slot_name_2_dir_and_width_and_io_name, pipeline_level=1)

    slr_anchor_wrapper = \
      getAnchorWrapperOfSLRWrapper(hub, f'slr_{slr_index}', external_io_name_2_dir_and_width)

    final_rtl = slr_anchor_wrapper + slr_wrapper

    open(f'{slr_stitch_dir}/slr_{slr_index}/slr_{slr_index}_wrapper.v', 'w').write('\n'.join(final_rtl))

def getSLRStitchScript(hub, slr_num):
  """
  get the vivado script to stitch all slots within an SLR
  """
  fpga_part_name = hub["FPGA_PART_NAME"]
  pair_list = hub['AllSlotPairs']

  for slr_index in range(slr_num):
    script = []

    script.append(f'set_part {fpga_part_name}')
    script.append(f'read_verilog "{slr_stitch_dir}/slr_{slr_index}/slr_{slr_index}_wrapper.v"')  
    script.append(f'read_xdc "{base_dir}/global_stitch/final_top_clk.xdc"')

    # synth
    script.append(f'synth_design -top "slr_{slr_index}_anchored" -part {fpga_part_name} -mode out_of_context')

    # read in the dcp of slots
    slot_names_in_slr = getSlotsInSLRIndex(hub, slr_index)
    for name in slot_names_in_slr:
      script.append(f'read_checkpoint -cell slr_{slr_index}_U0/{name}_ctrl_U0 {get_pruned_dcp_path(name)}')

    # place the anchors
    for pair in pair_list:
      if pair[0] not in slot_names_in_slr and pair[1] not in slot_names_in_slr:
        continue

      anchor_placement_tcl = f'{anchor_placement_dir}/{"_AND_".join(pair)}/place_anchors.tcl'
      local_placement_tcl_path = f'{slr_stitch_dir}/slr_{slr_index}/{"_AND_".join(pair)}_place_anchors.tcl'
      placement_tcl = open(anchor_placement_tcl).read().split('\n')

      # the anchors in the 2nd wrapper layer, need to update hierarchy in the original placement script
      if pair[0] in slot_names_in_slr and pair[1] in slot_names_in_slr:
        placement_tcl = \
          [re.sub(r'^  ', f'  slr_{slr_index}_U0/', line) for line in placement_tcl]
      
      open(local_placement_tcl_path, 'w').write('\n'.join(placement_tcl))
      script.append(f'source {local_placement_tcl_path}')

    # reuse the laguna anchor routes
    for name in slot_names_in_slr:
      script.append(f'source {base_dir}/slot_routing/{name}/add_{name}_ctrl_U0_laguna_route.tcl')

    # add clock stem
    script.append(f'set_property ROUTE "" [get_nets ap_clk]')
    script.append(f'source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl')
    script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

    # SLR boundary should serve as a natural boundary
    script.append(f'delete_pblocks *')

    # theoretically there should be non conflict nets. But we do see the GND net may cause conflicts
    script.append(f'report_route_status')
    script.append(f'write_checkpoint -force slr_{slr_index}_before_unroute_conflict.dcp')
    script.append(f'route_design -unroute -nets [get_nets -hierarchical -filter {{ ROUTE_STATUS == "CONFLICTS" }}]')
    script.append(f'write_checkpoint -force slr_{slr_index}_before_routed.dcp')
    script.append(f'route_design -preserve')
    script.append(f'write_checkpoint -force slr_{slr_index}_routed.dcp')

    open(f'{slr_stitch_dir}/slr_{slr_index}/stitch_slr_{slr_index}.tcl', 'w').write('\n'.join(script))

  parallel = [f'cd {slr_stitch_dir}/slr_{slr_index}/ && VIV_VER=2020.1 vivado -mode batch -source stitch_slr_{slr_index}.tcl' \
    for slr_index in range(slr_num)]
  open(f'{slr_stitch_dir}/parallel_slr_stitch.txt', 'w').write('\n'.join(parallel))

###################### TEST ##########################

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())
  get_pruned_dcp_path = lambda slot_name : f'{base_dir}/slot_routing/{slot_name}/unset_dcp_hd_reconfigurable/{slot_name}_ctrl.dcp'
  slr_stitch_dir = f'{base_dir}/SLR_level_stitch'
  anchor_placement_dir = f'{base_dir}/ILP_anchor_placement_iter0'
  os.mkdir(slr_stitch_dir)

  getSLRLevelWrapperWithIOAnchors(hub, slr_num=4)
  getSLRStitchScript(hub, slr_num=4)
