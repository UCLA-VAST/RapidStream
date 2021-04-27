#! /usr/bin/python3.6
import logging
import json
import sys
from autoparallel.BE.GenAnchorConstraints import createAnchorPlacementExtractScript

def getHeader(slot1_name, slot2_name):
  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {slot1_name}_AND_{slot2_name} (']
  return header

def getIODecl(slot1_io : dict, slot2_io : dict, top_io : dict):
  slot_io_merge = {**slot1_io, **slot2_io}
  io_decl = [f'  {" ".join(slot_io_merge[io])} {io},' for io in top_io]
  io_decl[-1] = io_decl[-1].replace(',', ');')
  
  return io_decl

def getConnection(inner_connection, top_io, pipeline_level=1):
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

    # only pipeline _pass_0 connections
    if '_pass_0' not in io:
      connection.append(f'  assign {io}_in = {io}_out;')
      continue     

    # assign the input wire equals the output wire
    if pipeline_level == 0:
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

def getInstance(slot_name : str, slot_io : dict, top_io : dict, inner_connection : dict):
  instance = []
  instance.append(f'  (* black_box *) {slot_name} {slot_name}_U0 (')
  for io, dir_width in slot_io.items():
    if io in top_io:
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

def CreateWrapperForSlotPair(hub, slot1_name, slot2_name, pipeline_level, output_dir, wrapper_name):
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

  # common io of the two slots
  inner_connection = {k : v for k, v in slot1_io.items() if k in slot2_io}
  
  # external io of the wrapper
  top_io = slot1_io.keys() - slot2_io.keys() | \
           slot2_io.keys() - slot1_io.keys()

  # deal with ap_clk
  top_io.add('ap_clk')
  inner_connection.pop('ap_clk')

  header = getHeader(slot1_name, slot2_name)
  io_decl = getIODecl(slot1_io, slot2_io, top_io)

  # pipelined connection between the two slots
  connection, pipeline_reg = getConnection(inner_connection, top_io, pipeline_level)

  slot1_inst = getInstance(slot1_name, slot1_io, top_io, inner_connection)
  slot2_inst = getInstance(slot2_name, slot2_io, top_io, inner_connection)
  ending = ['endmodule\n']

  slot1_def = getEmptyWrapper(slot1_name, slot1_io)
  slot2_def = getEmptyWrapper(slot2_name, slot2_io)

  pair_wrapper = header + io_decl + connection + slot1_inst + slot2_inst + ending + slot1_def + slot2_def

  open(f'{output_dir}/{wrapper_name}.v', 'w').write('\n'.join(pair_wrapper))

  # in the meantime create the placement extraction script
  createAnchorPlacementExtractScript(f'{slot1_name}_AND_{slot2_name}', pipeline_reg, output_dir)

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

  # read in the dcp of slots
  for name, path in dcp_name2path.items():
    script.append(f'read_checkpoint -cell {name}_U0 {path}')
    # delete pblocks immediately after reading incase conflict
    script.append(f'delete_pblock [get_pblock *]')

  # constrain the pipeline registers. get the pblocks based on slot names
  script.append(f'create_pblock wrapper')
  script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks wrapper]')

  # corner case: there may be no anchors between two slots
  script.append( 'catch {add_cells_to_pblock [get_pblocks wrapper] [get_cells -regexp {.*_reg.*} ] }')
  
  for name, path in dcp_name2path.items():
    # convert slot name to pblock
    pblock = name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
    script.append(f'resize_pblock [get_pblocks wrapper] -add {pblock}')
  
  # place and anchors
  script.append(f'place_design')

  # extract anchor placement
  script.append(f'source {wrapper_name}_print_anchor_placement.tcl')

  script.append(f'write_checkpoint {wrapper_name}_placed.dcp')

  open(f'{output_dir}/place.tcl', 'w').write('\n'.join(script))
