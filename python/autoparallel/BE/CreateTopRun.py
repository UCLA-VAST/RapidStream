import logging
import json
import sys
import re
import os
from autoparallel.BE.CreateVivadoRun import createClockFromBUFGXDC

def createTopRunScript(hub, rtl_path, xdc_path, final_slot_run_dir, interconnect_placement_path):
  """
  Synthesize the top with each slot wrapper marked as blackboxes
  Read in the post-routing slot wrappers
  Read in the placement of the interconnect
  Do the final routing
  """
  script = []

  device = hub["FPGA_PART_NAME"]
  assert device == 'xcu250-figd2104-2L-e', 'currently only U250 is supported'

  # create project
  script.append(f'create_project stitch ./stitch -part {device}')    

  if device == 'xcu250-figd2104-2L-e':
    board_id = 'xilinx.com:au250:part0:1.3'
    script.append(f'set_property board_part {board_id} [current_project]')

  # add the rtl for the new top
  script.append(f'set rtl_files [glob {rtl_path}/*.v]')
  script.append(r'read_verilog ${rtl_files}')
  script.append(r'set_property top final_top.v [current_fileset]')

  script.append(f'update_compile_order -fileset sources_1')

  # create clock
  script.append(f'add_files -fileset constrs_1 {xdc_path}')

  # set OOC
  script.append('set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} -value {-mode out_of_context} -objects [get_runs synth_1]')

  # run synthesis of the top
  script.append('launch_runs synth_1 -jobs 56')
  script.append('wait_on_run synth_1')

  # add checkpoints of each slot
  slot_names = hub["SlotIO"].keys()
  for slot_name in slot_names:
    script.append(f'read_checkpoint -cell {slot_name}_ctrl_U0 {final_slot_run_dir}/{slot_name}/{slot_name}_after_pruning_anchors.dcp')

  # open the synthesized top along with the dcps
  script.append('update_compile_order -fileset sources_1')
  script.append('open_run synth_1 -name synth_1')

  # apply the placement of interconnct logic
  script.append(f'source -notrace {interconnect_placement_path}')

  script.append(f'write_checkpoint before_global_stitch.dcp')

  script.append(f'route_design')
  script.append(f'phys_opt_design')

  script.append(f'write_checkpoint after_global_stitch.dcp')

  return script

def updateSlotType(orig_rtl):
  """
  The routing happens in the anchored wrapper. 
  After routing we prune away the anchors, so the checkpoints are logically the same as the ctrl wrappers
  However, the type of the checkpoints are still anchored wrappers
  Thus in the top file we change the type of each black box to be anchored wrappers
  """
  
  # note the space after the _ctrl
  return re.sub(r'(CR_X[\d]+Y[\d]+_To_CR_X[\d]+Y[\d]+)_ctrl ', r'\1_anchored ', orig_rtl)

def addBUFGToTopRTL(hub, rtl_dir):
  # the new top RTL
  top_rtl_from_fe = hub["NewTopRTL"]

  # set up black box
  orig_top_rtl = top_rtl_from_fe.replace('(* keep_hierarchy = "yes" *)', '(* black_box *)')

  # add explicit BUFGCE
  top_rtl_list = orig_top_rtl.split('\n')
  for i in range(len(top_rtl_list)):
    if re.search(r'input[ ]+ap_clk', top_rtl_list[i]):
      top_rtl_list[i] = re.sub(r'input[ ]+ap_clk', 'input ap_clk_port', top_rtl_list[i])
    elif ');' in top_rtl_list[i]:
      plugin = []
      plugin.append(f'wire ap_clk; ')
      plugin.append(f'(* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg ( ')
      plugin.append(f'  .I(ap_clk_port), ')
      plugin.append(f'  .CE(1\'b1),')
      plugin.append(f'  .O(ap_clk) );')
      top_rtl_list[i+1:i+1] = plugin
      break

  top_with_bufg = '\n'.join(top_rtl_list)

  top_updated_type = updateSlotType(top_with_bufg)

  top_rtl_path = f'{rtl_dir}/final_top.v'
  open(top_rtl_path, 'w').write(top_updated_type)

def getSlotWrapperShell(hub, rtl_dir):
  # get a shell for each ctrl wrapper
  wrapper_name2rtl = hub["SlotWrapperRTL"]
  for name, rtl_list in wrapper_name2rtl.items():    
    # replace the actual inner compute slot as a empty shell
    state = 0
    beg = -1
    for i in range(len(rtl_list)):
      if state == 0: # the start of inner module header
        if 'module' in rtl_list[i]:
          state = 1
          beg = i
      elif state == 1: # the end of the inner module header
        if ');' in rtl_list[i]:
          io = rtl_list[beg:i+1]
          state = 2
      elif state == 2:
        if 'endmodule' in rtl_list[i]:
          io.append('endmodule')
          break
        if re.search('^[ ]*input|^[ ]*output', rtl_list[i]):
          io.append(rtl_list[i])

    wrapper_rtl = '\n'.join(io)
    wrapper_rtl_updated_type = updateSlotType(wrapper_rtl)

    wrapper_path = f'{rtl_dir}/{name}_ctrl.v'
    open(wrapper_path, 'w').write(wrapper_rtl_updated_type)

def setupTopRunRTL(hub, stitch_dir):
  """
  mark each slot wrapper instances as blackbox
  create an empty shell for each wrapper
  add explicit BUFG to the top RTL
  *** update the type of the blackbox to be XXX_anchored
  to match the type of the slots after we remove the anchor registers
  """
  rtl_dir = f'{stitch_dir}/rtl'
  os.mkdir(rtl_dir)

  addBUFGToTopRTL(hub, rtl_dir)
  getSlotWrapperShell(hub, rtl_dir)

def createTopRun(hub, base_dir, final_slot_run_dir, interconnect_placement_path):
  """
  Assemble the post-place DCPs and post-route DCPs
  """

  stitch_dir = f'{base_dir}/global_stitch'
  os.mkdir(stitch_dir)

  # prepare the modified top RTL
  setupTopRunRTL(hub, stitch_dir)

  # prepare the clock xdc
  createClockFromBUFGXDC('final_top', stitch_dir)

  stitch_script = createTopRunScript(hub, f'{stitch_dir}/rtl', f'{stitch_dir}/final_top_clk.xdc', final_slot_run_dir, interconnect_placement_path)
  open(f'{stitch_dir}/final_stitch.tcl', 'w').write('\n'.join(stitch_script))