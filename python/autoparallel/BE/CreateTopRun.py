import logging
import json
import sys
import re
import os

def createTopRunScript(hub, rtl_path, xdc_path, parallel_run_dir, target):
  """
  target => placed or routed
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

  # add checkpoints of compute slots for each slot
  compute_slots = hub["ComputeSlots"]
  for slot_name in compute_slots:
    cell_name = f'{slot_name}_routing_U0/{slot_name}_U0'
    dcp_name = f'{slot_name}_{target}_free_run_compute'
    dcp_dir = f'{parallel_run_dir}/{slot_name}/{dcp_name}'
    script.append(f'read_checkpoint -cell {cell_name} {dcp_dir}/{dcp_name}.dcp')

  # run synthesis
  script.append('launch_runs synth_1 -jobs 56')
  script.append('wait_on_run synth_1')
  script.append('update_compile_order -fileset sources_1')
  script.append('open_run synth_1 -name synth_1')
  script.append('write_checkpoint stitch.dcp')

  # prepare for interconnect placement extraction
  script.append('set target_cells [get_cells -hierarchical -regexp -filter { STATUS != "FIXED" && PRIMITIVE_TYPE !~ OTHERS.others.* } ]')
  script.append('place_design -directive RuntimeOptimized')

  return script

def setupTopRunRTL(hub, top_run_dir):
  rtl_dir = f'{top_run_dir}/rtl'
  os.mkdir(rtl_dir)

  # the new top RTL
  new_top_rtl = hub["NewTopRTL"]
  top_rtl_path = f'{rtl_dir}/final_top.v'
  open(top_rtl_path, 'w').write(new_top_rtl)

  # each routing slot
  wrapper_name2rtl = hub["SlotWrapperRTL"]
  for name, rtl_list in wrapper_name2rtl.items():
    # mark each inner compute slot as blackbox
    rtl_list_copy = rtl_list[:]
    for i in range(len(rtl_list_copy)):
      if 'dont_touch' in rtl_list_copy[i] and f' {name} ' in rtl_list_copy[i] and f'{name}_U0' in rtl_list_copy[i]:
        rtl_list_copy[i] = re.sub(r'\(.*\)', '(* black_box *)', rtl_list_copy[i])
        break
    
    # replace the actual inner compute slot as a empty shell
    state = 0
    for i in range(len(rtl_list_copy)):
      if state == 0: # the start of inner module header
        if re.search(f'module[ ]+{name}[ ]*\(', rtl_list_copy[i]):
          state = 1
      elif state == 1: # the end of the inner module header
        if ');' in rtl_list_copy[i]:
          state = 2
      elif state == 2: 
        # find the remaining delcaration of input/output
        io = []
        for j in range(i, len(rtl_list_copy)):
          if 'endmodule' in rtl_list_copy[j]:
            break
          if 'input' in rtl_list_copy[j] or 'output' in rtl_list_copy[j]:
            io.append(rtl_list_copy[j])

        # remove the contents of the inner module
        rtl_list_copy[i:] = io
        rtl_list_copy.append('endmodule')
        break

    wrapper_path = f'{rtl_dir}/{name}_routing.v'
    open(wrapper_path, 'w').write('\n'.join(rtl_list_copy))