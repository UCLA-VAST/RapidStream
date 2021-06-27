import sys
import json
import re
import os
from autoparallel.BE.UniversalWrapperCreater import getWrapperOfSlots, addAnchorToNonTopIOs
from autoparallel.BE.TopLevelStitch import setupTopStitch
from autoparallel.BE.Utilities import getSlotsInSLRIndex

def getAnchorWrapperOfSLRWrapper(hub, slr_wrapper_name, external_io_name_2_dir_and_width):
  """
  add another layer of wrapper around the SLR-level wrapper to insert the anchor registers
  """
  io_list = [[*dir_and_width, io_name] \
    for io_name, dir_and_width in external_io_name_2_dir_and_width.items()]
  slr_anchor_wrapper = addAnchorToNonTopIOs(hub, slr_wrapper_name, io_list)
  return slr_anchor_wrapper


def getSLRLevelWrapperWithIOAnchors(hub, slr_num):
  """
  get a wrapper for all slots within an SLR
  """
  get_io_name_2_dir_and_width = lambda slot_io_list : {io[-1] : io[0:-1] for io in slot_io_list}

  slr_name_2_dir_and_width_and_io_name = {}

  for slr_index in range(slr_num):
    wrapper_name = f'slr_{slr_index}'

    os.mkdir(f'{slr_stitch_dir}/{wrapper_name}')
    slr_slots = getSlotsInSLRIndex(hub, slr_index)

    slr_slot_name_2_dir_and_width_and_io_name = {
      f'{name}_ctrl' : get_io_name_2_dir_and_width(hub['SlotIO'][name]) for name in slr_slots}

    slr_wrapper, external_io_name_2_dir_and_width, _ = \
      getWrapperOfSlots(wrapper_name, slr_slot_name_2_dir_and_width_and_io_name, pipeline_level=1)

    slr_anchor_wrapper = \
      getAnchorWrapperOfSLRWrapper(hub, wrapper_name, external_io_name_2_dir_and_width)

    final_rtl = slr_anchor_wrapper + slr_wrapper

    open(f'{slr_stitch_dir}/{wrapper_name}/{wrapper_name}_wrapper.v', 'w').write('\n'.join(final_rtl))

    slr_name_2_dir_and_width_and_io_name[wrapper_name] = external_io_name_2_dir_and_width

  return slr_name_2_dir_and_width_and_io_name


def extractLagunaAnchorRoutes(slr_name):
  """
  record the ROUTE property of the nets to/from laguna anchors.
  Will reuse them later in the final stitch
  """
  script = []
  script.append(f'set target {slr_name}')
  script.append(
r'''
set laguna_anchors [get_cells -hierarchical -regexp -filter { LOC =~  ".*LAGUNA.*" } ]
set laguna_anchor_nets [get_nets  -regexp -top_net_of_hierarchical_group -filter { TYPE != "GROUND" && TYPE != "POWER" && NAME !~  ".*ap_clk.*" && ROUTE_STATUS != "HIERPORT" }  -of_objects ${laguna_anchors} ]
set file [open "add_${target}_laguna_route.tcl" "w"]
foreach net ${laguna_anchor_nets} {
  # check if the net connects to a laguna anchor
  set laguna_anchor [get_cells -of_objects [get_nets -segment $net] -filter {LOC =~ LAGUNA*}]
  if {$laguna_anchor != [] } {
    set net_route [get_property ROUTE $net]
    puts $file "set_property ROUTE ${net_route} \[get_nets ${net} \]"
  }
}
close $file
''')

  return script


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
      # make a copy of the script in local dir and make corresponding modifications
      local_placement_tcl_path = f'{slr_stitch_dir}/slr_{slr_index}/{"_AND_".join(pair)}_place_anchors.tcl'
      placement_tcl = open(anchor_placement_tcl).read().split('\n')

      # the anchors in the 2nd wrapper layer, need to update hierarchy in the original placement script
      if pair[0] in slot_names_in_slr and pair[1] in slot_names_in_slr:
        placement_tcl = \
          [re.sub(r'^  ', f'  slr_{slr_index}_U0/', line) for line in placement_tcl]
      
      open(local_placement_tcl_path, 'w').write('\n'.join(placement_tcl))
      script.append(f'source {local_placement_tcl_path}')

    # reuse the laguna anchor routes
    # for name in slot_names_in_slr:
    #   script.append(f'source {base_dir}/slot_routing/{name}/add_{name}_ctrl_U0_laguna_route.tcl')

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

    script += extractLagunaAnchorRoutes(f'slr_{slr_index}')

    open(f'{slr_stitch_dir}/slr_{slr_index}/stitch_slr_{slr_index}.tcl', 'w').write('\n'.join(script))

  pruneAnchors(slr_num)
  getSLRStitchParallelTasks(slr_num)

def pruneAnchors(slr_num):
  """
  after we mark the checkpoint as non-ooc, use write_checkpoint -cell
  to remove the anchored wrapper
  """
  for slr_index in range(slr_num):
    slr_dir = f'{slr_stitch_dir}/slr_{slr_index}'

    script = []
    script.append(f'open_checkpoint {slr_dir}/unset_dcp_ooc/slr_{slr_index}_routed.dcp')
    script.append(f'set_property HD.RECONFIGURABLE 1 [get_cells slr_{slr_index}_U0]')
    script.append( 'set anchor_cells [get_cells -regexp .*q0_reg.*]')
    script.append( 'route_design -unroute -nets [get_nets -of_object ${anchor_cells} -filter {TYPE != "GOURND" && TYPE != "POWER" && NAME !~ "*ap_clk*"} ]')
    script.append(f'write_checkpoint -cell slr_{slr_index}_U0 {slr_dir}/slr_{slr_index}_no_anchor.dcp')
    
    open(f'{slr_dir}/prune_anchors.tcl', 'w').write('\n'.join(script))


def getSLRStitchParallelTasks(slr_num):
  parallel = []
  for slr_index in range(slr_num):
    cmd = []
    cmd += [f'cd {slr_stitch_dir}/slr_{slr_index}/']
    cmd += [f'VIV_VER=2020.1 vivado -mode batch -source stitch_slr_{slr_index}.tcl']
    cmd += [f'{unset_ooc_script} slr_{slr_index}_routed.dcp']
    cmd += [f'VIV_VER=2020.1 vivado -mode batch -source prune_anchors.tcl']
    cmd += [f'{unset_hd_reconfigurable_script} slr_{slr_index}_no_anchor.dcp']
    parallel += [ ' && '.join(cmd) ]

  open(f'{slr_stitch_dir}/parallel_slr_stitch.txt', 'w').write('\n'.join(parallel))

###################### TEST ##########################

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())

  current_path = os.path.dirname(os.path.realpath(__file__))
  unset_ooc_script = f'{current_path}/../../../bash/unset_ooc.sh'
  unset_hd_reconfigurable_script = f'{current_path}/../../../bash/unset_hd_reconfigurable.sh'

  get_pruned_dcp_path = lambda slot_name : f'{base_dir}/slot_routing/{slot_name}/unset_dcp_hd_reconfigurable/{slot_name}_ctrl.dcp'
  slr_stitch_dir = f'{base_dir}/SLR_level_stitch'
  anchor_placement_dir = f'{base_dir}/ILP_anchor_placement_iter0'
  os.mkdir(slr_stitch_dir)

  slr_name_2_dir_and_width_and_io_name = getSLRLevelWrapperWithIOAnchors(hub, slr_num=4)
  getSLRStitchScript(hub, slr_num=4)

  setupTopStitch(base_dir, hub, slr_name_2_dir_and_width_and_io_name)