#! /usr/bin/python3.6
import logging
import json
import sys
from autoparallel.BE.GenAnchorConstraints import createAnchorPlacementExtractScript, __getBufferRegionSize
from autoparallel.BE.Device import U250
from typing import List, Set, Dict, Tuple

def getHeader(slot1_name, slot2_name):
  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {slot1_name}_AND_{slot2_name} (']
  return header

def getIODecl(slot1_io : dict, slot2_io : dict, wrapper_io : dict):
  slot_io_merge = {**slot1_io, **slot2_io}
  io_decl = [f'  {" ".join(slot_io_merge[io])} {io},' for io in wrapper_io]
  io_decl[-1] = io_decl[-1].replace(',', ');')
  
  return io_decl

def getConnection(inner_connection, pipeline_level, in_slot_pipeline_style):
  """
  get the RTL to connect the slots
  data links will be pipelined
  wires of passing edge will be directly connected
  @param connection: the RTL section
  @param pipeline_reg: all the pipeline registers instantiated
  """
  assert pipeline_level == 1, f'currently only support pipeline_level of 1'

  connection = []
  pipeline_regs = []
  for io, dir_width in inner_connection.items():
    width = dir_width[1] if len(dir_width) == 2 else ''
    connection.append(f'  wire {width} {io}_in;')
    connection.append(f'  wire {width} {io}_out;')

    if in_slot_pipeline_style == 'REG':
      assert False
      # only pipeline _pass_0 connections
      if '_pass_0' not in io:
        connection.append(f'  assign {io}_in = {io}_out;')
        continue     
    else:
      assert  in_slot_pipeline_style == 'LUT' or \
              in_slot_pipeline_style == 'WIRE' or \
              in_slot_pipeline_style == 'DOUBLE_REG'

    # assign the input wire equals the output wire
    if pipeline_level == 0:
      assert False
      connection.append(f'  assign {io}_in = {io}_out;')
    else:
      # add the pipeline registers
      for i in range(pipeline_level):
        connection.append(f'  (* dont_touch = "yes" *) reg {width} {io}_q{i};')
        
        # format: input/output width name
        # to be used for placement extraction
        pipeline_regs.append(dir_width + [f'{io}_q{i}'])
    
      # connect the head and tail
      connection.append(f'  always @ (posedge ap_clk) begin')
      connection.append(f'    {io}_q0 <= {io}_out;')
      for i in range(1, pipeline_level):
        connection.append(f'    {io}_q{i} <= {io}_q{i-1};')
      connection.append(f'  end')
      connection.append(f'  assign {io}_in = {io}_q{pipeline_level-1};')

  return connection, pipeline_regs

def getInstance(slot_name : str, slot_io : dict, wrapper_io : dict, inner_connection : dict):
  instance = []
  instance.append(f'  (* black_box *) {slot_name} {slot_name}_U0 (')
  for io, dir_width in slot_io.items():
    if io in wrapper_io:
      instance.append(f'    .{io}({io}),')
    elif io in inner_connection:
      if 'input' in dir_width:
        instance.append(f'    .{io}({io}_in),')
      elif 'output' in dir_width:
        instance.append(f'    .{io}({io}_out),')
      else:
        assert False
    else:
      assert False
  instance[-1] = instance[-1].replace(',', ');\n')

  return instance

def getEmptyWrapper(slot_name, slot_io):
  """ in order for black_box modules to be recognized by vivado """
  empty_wrapper = []
  empty_wrapper.append(f'\n\nmodule {slot_name} (')
  empty_wrapper += [' '.join(dir_width) + ' ' + io + ',' for io, dir_width in slot_io.items()]
  empty_wrapper[-1] = empty_wrapper[-1].replace(',', '')
  empty_wrapper.append(f');')
  empty_wrapper.append(f'endmodule')
  return empty_wrapper

def getTopIOAndInnerConnectionOfPair(hub, slot1_name, slot2_name) -> Tuple[Set, Dict]:
  slot1_io = hub['SlotIO'][slot1_name]
  slot2_io = hub['SlotIO'][slot2_name]

  # io name -> dir + width (in string)
  convert = lambda slot_io : {io[-1] : io[0:-1] for io in slot_io }
  slot1_io = convert(slot1_io)
  slot2_io = convert(slot2_io)

  # common io of the two slots
  inner_connection = {k : v for k, v in slot1_io.items() if k in slot2_io}
  
  # external io of the wrapper
  wrapper_io = slot1_io.keys() - slot2_io.keys() | \
           slot2_io.keys() - slot1_io.keys()

  # deal with ap_clk
  wrapper_io.add('ap_clk')
  inner_connection.pop('ap_clk')

  return wrapper_io, inner_connection

def getPairWrapper(hub, slot1_name, slot2_name, pipeline_level, in_slot_pipeline_style):
  """ 
  group together two neighbor slots 
  Wires of passing edges should not be pipelined
  Also create the script to extract the placement of pipeline registers
  """
  slot1_io = hub['SlotIO'][slot1_name]
  slot2_io = hub['SlotIO'][slot2_name]

  # io name -> dir + width (in string)
  convert = lambda slot_io : {io[-1] : io[0:-1] for io in slot_io }
  slot1_io = convert(slot1_io)
  slot2_io = convert(slot2_io)

  wrapper_io, inner_connection = getTopIOAndInnerConnectionOfPair(hub, slot1_name, slot2_name)

  header = getHeader(slot1_name, slot2_name)
  io_decl = getIODecl(slot1_io, slot2_io, wrapper_io)

  # pipelined connection between the two slots
  connection, pipeline_regs = getConnection(inner_connection, pipeline_level, in_slot_pipeline_style)

  slot1_inst = getInstance(slot1_name, slot1_io, wrapper_io, inner_connection)
  slot2_inst = getInstance(slot2_name, slot2_io, wrapper_io, inner_connection)
  ending = ['endmodule\n']

  slot1_def = getEmptyWrapper(slot1_name, slot1_io)
  slot2_def = getEmptyWrapper(slot2_name, slot2_io)

  pair_wrapper = header + io_decl + connection + slot1_inst + slot2_inst + ending + slot1_def + slot2_def

  return pair_wrapper, pipeline_regs

def CreateWrapperForSlotPair(hub, slot1_name, slot2_name, pipeline_level, output_dir, wrapper_name, in_slot_pipeline_style):
  pair_wrapper, pipeline_regs = getPairWrapper(hub, slot1_name, slot2_name, pipeline_level, in_slot_pipeline_style)
  
  open(f'{output_dir}/{wrapper_name}.v', 'w').write('\n'.join(pair_wrapper))

  # in the meantime create the placement extraction script
  createAnchorPlacementExtractScript(f'{slot1_name}_AND_{slot2_name}', pipeline_regs, output_dir)

  return pair_wrapper

def createVivadoScriptForSlotPair(
    hub, 
    wrapper_name,
    wrapper_path, 
    dcp_name2path : dict,
    clk_xdc_path,
    output_dir = '.'):
  fpga_part_name = hub["FPGA_PART_NAME"]

  script = []

  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'read_verilog "{wrapper_path}"')  

  # clock xdc
  script.append(f'read_xdc "{clk_xdc_path}"')

  # synth
  script.append(f'synth_design -top "{wrapper_name}" -part {fpga_part_name} -mode out_of_context')
  script.append(f'write_checkpoint synth.dcp')

  # make Vivado place the anchors on lagunas
  # will be automatically invalidated for non-SLR-crossing pairs
  script.append(f'set_property USER_SLL_REG 1 [get_cells -regexp {{ .*q0_reg.* }} ]')

  # read in the dcp of slots
  for name, path in dcp_name2path.items():
    script.append(f'read_checkpoint -cell {name}_U0 {path}')
    # delete pblocks immediately after reading incase conflict
    script.append(f'delete_pblock [get_pblock *]')

  # constrain the pipeline registers. get the pblocks based on slot names
  script.append(f'create_pblock buffer_for_anchors')
  script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks buffer_for_anchors]')

  # corner case: there may be no anchors between two slots
  script.append( 'catch {add_cells_to_pblock [get_pblocks buffer_for_anchors] [get_cells -regexp {.*q0_reg.*} ] }')
  
  assert len(dcp_name2path) == 2
  names = list(dcp_name2path.keys())
  col_width, row_width = __getBufferRegionSize(None, None) # TODO: should automatically choose a suitable buffer region size
  buffer_between_two_slots = U250.getBufferRegionBetweenSlotPair(names[0], names[1], col_width, row_width)

  # note that we need to include lagunas into the pblocks
  # otherwise the placer will deem no SLL could be used
  # since there are only 1 pipeline register, the registers will not be placed onto laguna sites (which require a pair)
  script.append(f'resize_pblock [get_pblocks buffer_for_anchors] -add {{{buffer_between_two_slots}}}')
  
  # constrain the timing with placeholder LUTs
  if hub['InSlotPipelineStyle'] == 'LUT':
    script.append(setMaxDelayFromLut())
    
  # report the anchor usage of the buffer region
  script.append(f'report_utilization -pblocks [get_pblocks buffer_for_anchors]')

  # place and anchors
  # Using Quick will result in bad results...
  script.append(f'place_design -directive RuntimeOptimized')

  # extract anchor placement
  script.append(f'source {wrapper_name}_print_anchor_placement.tcl')

  script.append(f'write_checkpoint {wrapper_name}_placed.dcp')

  open(f'{output_dir}/place.tcl', 'w').write('\n'.join(script))

def setMaxDelayFromLut():
  return '''
set placeholder_luts [get_cells -hierarchical -filter { PRIMITIVE_TYPE == CLB.LUT.LUT1 && NAME =~  "*_lut*" } ]
foreach lut $placeholder_luts {
  
  puts "--- processing ${lut} --- "

  set all_nets_of_lut [get_nets -segments -of_objects [get_cells ${lut} ]]

  set anchor_pin [get_pins -of_objects ${all_nets_of_lut}  -filter { PARENT_CELL =~  "*_q0_reg*" } ]

  # the placeholder LUT may be of paths in different directions.
  if { ${anchor_pin} != "" } {
    puts $anchor_pin

    set lut_pin [ get_pins  -filter { PARENT_CELL =~  "*_lut*" } -of_objects [ get_nets -of_objects [get_pins ${anchor_pin}] -segments ] ]

    puts $lut_pin

    set dir [get_property DIRECTION [get_pins ${lut_pin} ] ]

    if { ${dir} == "OUT" } {
      puts "constrain path from LUT to anchor FDRE"
      set_max_delay 1 -datapath_only -from ${lut_pin} -to ${anchor_pin}
    } else {
      puts "constrain path from anchor FDRE to LUT"
      set_max_delay 1 -datapath_only -from ${anchor_pin} -to ${lut_pin}
    }
  }
}  
  '''