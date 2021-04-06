import logging
import json
import sys

def createTopRunScript(hub, top_rtl_path, xdc_path, parallel_run_dir):
  script = []

  device = hub["FPGA_PART_NAME"]
  assert device == 'xcu250-figd2104-2L-e', 'currently only U250 is supported'

  # create project
  script.append(f'create_project stitch ./stitch -part {device}')    

  if device == 'xcu250-figd2104-2L-e':
    board_id = 'xilinx.com:au250:part0:1.3'
    script.append(f'set_property board_part {board_id} [current_project]')

  # add the rtl for the new top
  script.append(f'add_files {top_rtl_path}')
  script.append(f'update_compile_order -fileset sources_1')

  # create clock
  script.append(f'add_files -fileset constrs_1 {xdc_path}')

  # set OOC
  script.append('set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} -value {-mode out_of_context} -objects [get_runs synth_1]')

  # add checkpoints for each slot
  compute_slots = hub["ComputeSlots"]
  for slot_name in compute_slots:
    cell_name = f'{slot_name}_routing_U0'
    script.append(f'read_checkpoint -cell {cell_name} {parallel_run_dir}/{slot_name}/{slot_name}_routed_free_run/{slot_name}_routed_free_run.dcp')

  # run synthesis
  script.append('launch_runs synth_1 -jobs 56')
  script.append('wait_on_run synth_1')
  script.append('update_compile_order -fileset sources_1')
  script.append('open_run synth_1 -name synth_1')
  script.append('write_checkpoint stitch.dcp')

  return script