#! /usr/bin/python3.6
import logging
from autoparallel.FE.Slot import Slot
from autoparallel.FE.TopRTLParser import TopRTLParser
from autoparallel.FE.FIFOTemplate import fifo_template
from autoparallel.FE.GlobalRouting import GlobalRouting
import re

def getTopIO(top_rtl_parser):
  # get the IO section 
  top_io_list = top_rtl_parser.getDirWidthNameOfAllIO()
  assert any(re.search('ap_rst_n', io[-1]) for io in top_io_list)
  
  io_rtl = ['  ' + ' '.join(io) + ',' for io in top_io_list]
  io_rtl[-1] = io_rtl[-1].replace(',', '\n);\n')

  # vitis requires the original parameters be kept
  param_to_value_str = top_rtl_parser.getParamToValueStr()
  param_sec = [f'  parameter {param} = {value};' for param, value in param_to_value_str.items()]

  return io_rtl + param_sec

def __isDataPort(io, top_rtl_parser):
  # filter ap signals.
  if io[-1].startswith('ap_'): 
    return False
  # filter top level IOs (cannot be redefined as wire)
  elif top_rtl_parser.isIO(io[-1]):
    return False
  else:
    return True

def getWireDecl(slot_to_io, ctrl_signals, top_rtl_parser):
  """
  declare connecting wires
  need to filter out the IOs
  also filter out the ap signals (separately handled)
  """

  wire_decl = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:
      if not __isDataPort(io, top_rtl_parser):
        continue

      # add the wire to declaration
      if io[0] == 'output': 
        wire_decl.append('  wire ' + ' '.join(io[1:]) + '_out;')
      elif io[0] == 'input':
        wire_decl.append('  wire ' + ' '.join(io[1:]) + '_in;')
  return wire_decl

def getPipelining(slot_to_io, top_rtl_parser, global_router):
  """
  add pipeline registers to connect the slots
  """

  pipeline = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:  
      if not __isDataPort(io, top_rtl_parser):
        continue

      # choose to work on the output side
      if io[0] != 'output': 
        continue # otherwise we do the same thing twice for each edge

      e_name = top_rtl_parser.getFIFONameFromWire(io[-1])
      pipeline_level = global_router.getPipelineLevelOfEdgeName(e_name)

      # assign the input wire equals the output wire
      if pipeline_level == 0:
        pipeline.append(f'  assign {io[-1]}_in = {io[-1]}_out;')
      else:
        # add the pipeline registers
        for i in range(pipeline_level):
          width = io[1] if len(io) == 3 else ''
          pipeline.append(f'  (* dont_touch = "yes" *) reg {width} {io[-1]}_q{i};')
      
        # connect the head and tail
        pipeline.append(f'  always @ (posedge ap_clk) begin')
        pipeline.append(f'    {io[-1]}_q0 <= {io[-1]}_out;')
        for i in range(1, pipeline_level):
          pipeline.append(f'    {io[-1]}_q{i} <= {io[-1]}_q{i-1};')
        pipeline.append(f'  end')
        pipeline.append(f'  assign {io[-1]}_in = {io[-1]}_q{pipeline_level-1};')
  
  return pipeline

def getCtrlSignals(slot_to_io):
  # control signals
  ctrl_section = []
  ctrl_section.append(f'  wire ap_start_orig;')
  ctrl_section.append(f'  wire ap_done_final;')
  ctrl_section.append(f'  wire ap_ready_final;')
  ctrl_section.append(f'  wire ap_idle_final;')

  # hls cosim will detect the ap_done signal. Add place holder
  ctrl_section.append(f'  wire ap_done = ap_done_final;')
  ctrl_section.append(f'  wire ap_ready = ap_ready_final;')
  ctrl_section.append(f'  wire ap_idle = ap_idle_final;')
  ctrl_section.append(f'  wire ap_start = ap_start_orig;')

  level = 4   # pipeline 3 times

  # --------- ap_done --------- 
  for slot in slot_to_io.keys(): 
    ctrl_section.append(f'  wire ap_done_{slot};') # connect to module
    for i in range(level): 
      ctrl_section.append(f'  (* dont_touch = "yes" *) reg ap_done_{slot}_q{i};') # pipeline reg

  ctrl_section.append(f'  (* dont_touch = "yes" *) reg ap_done_final_reg_;')
  ctrl_section.append(f'  assign ap_done_final = ap_done_final_reg_;') # connect to s_axi_control

  ctrl_section.append(f'  always @ (posedge ap_clk) begin')
  ctrl_section.append(f'    ap_done_final_reg_ <= 1\'b1 ' + \
    ' '.join([f'& ap_done_{slot}_q{level-1}' for slot in slot_to_io.keys()]) + ';' )
  ctrl_section.append(f'  end')

  # pipeline the ap_done from each slot
  for slot in slot_to_io.keys():
    ctrl_section.append(f'  always @ (posedge ap_clk) begin')
    ctrl_section.append(f'    ap_done_{slot}_q0 <= ap_done_{slot};')
    for i in range(1, level-1): # note the level-1 here
      ctrl_section.append(f'    ap_done_{slot}_q{i} <= ap_done_{slot}_q{i-1};')

    # hold the ap_done of each slot until everyone has asserted
    # prevent staggered pulse signals
    ctrl_section.append(f'    if (ap_done_final_reg_) ')
    ctrl_section.append(f'      ap_done_{slot}_q{level-1} <= ap_done_{slot}_q{level-2};')
    ctrl_section.append(f'    else')
    ctrl_section.append(f'      ap_done_{slot}_q{level-1} <= ap_done_{slot}_q{level-2} | ap_done_{slot}_q{level-1};')
    ctrl_section.append(f'  end')

  # --------- ap_start & ap_rst --------- 
  for slot in slot_to_io.keys(): 

    # pipeline reg
    for i in range(level): 
      ctrl_section.append(f'  (* dont_touch = "yes" *) reg ap_start_{slot}_q{i};')
      ctrl_section.append(f'  (* dont_touch = "yes" *) reg ap_rst_n_{slot}_q{i};')

    ctrl_section.append(f'  always @ (posedge ap_clk) begin')
    ctrl_section.append(f'    ap_start_{slot}_q0 <= ap_start_orig;') # connect to s_axi_control
    ctrl_section.append(f'    ap_rst_n_{slot}_q0 <= ap_rst_n;') # connect to top
    for i in range(1, level):
      ctrl_section.append(f'    ap_start_{slot}_q{i} <= ap_start_{slot}_q{i-1};')
      ctrl_section.append(f'    ap_rst_n_{slot}_q{i} <= ap_rst_n_{slot}_q{i-1};')
    ctrl_section.append(f'  end')

    # connect to module
    ctrl_section.append(f'  wire ap_start_{slot} = ap_start_{slot}_q{level-1};')
    ctrl_section.append(f'  wire ap_rst_n_{slot} = ap_rst_n_{slot}_q{level-1};')

  # --------- other useless ap signals --------- 
  for slot in slot_to_io.keys(): 
    ctrl_section.append(f'  wire ap_idle_{slot};') # dangling signal
    ctrl_section.append(f'  wire ap_ready_{slot};') # dangling signal
    ctrl_section.append(f'  wire ap_continue_{slot} = 1\'b1;')

  ctrl_section.append(f'  assign ap_ready_final = ap_done_final;')
  ctrl_section.append(f'  assign ap_idle_final = ap_done_final;')  

  return ctrl_section

def getSlotInst(slot_to_io, ctrl_signals, top_rtl_parser, s_axi_ctrl_signals, target):
  # instantiate each slot
  slot_insts = []
  
  for slot, io_list in slot_to_io.items():
    # if targeting implementation, we mark the modules as black box
    # so that they can be replaced later by separately implemented DCPs
    tag = '(* black_box *)' if target == 'hw' else ''
    slot_insts.append(f'\n\n {tag}  {slot} {slot}_U0 (')
    for io in io_list:
      if io[-1] in ctrl_signals:
        # seperately handle ap signals
        slot_insts.append(f'    .{io[-1]}({io[-1]}_{slot}),')
      elif top_rtl_parser.isIO(io[-1]):
        # directly connect to top-level IO
        slot_insts.append(f'    .{io[-1]}({io[-1]}),')
      elif io[-1] in s_axi_ctrl_signals:
        slot_insts.append(f'    .{io[-1]}({io[-1]}),') 
      else:
        # differentiate direction for pipelining purpose
        if io[0] == 'input':
          slot_insts.append(f'    .{io[-1]}({io[-1]}_in),')
        elif io[0] == 'output':
          slot_insts.append(f'    .{io[-1]}({io[-1]}_out),')
        else: assert False

    # handle the last io
    slot_insts[-1] = slot_insts[-1].replace(',', '\n  );') 
  
  return slot_insts

def CreateTopRTL(top_rtl_parser, wrapper_creater, top_module_name, global_router):
  slot_to_io = wrapper_creater.getSlotToIO()
  target = wrapper_creater.target

  ctrl_signals = set(['ap_start', 'ap_done', 'ap_idle', 'ap_ready', 'ap_continue', 'ap_rst_n'])
  s_axi_ctrl_signals = set(['ap_start_orig', 'ap_done_final', 'ap_idle_final', 'ap_ready_final'])

  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {top_module_name} (']
  top_io = getTopIO(top_rtl_parser)
  wire_decl = getWireDecl(slot_to_io, ctrl_signals, top_rtl_parser)
  pipeline = getPipelining(slot_to_io, top_rtl_parser, global_router)
  ctrl = getCtrlSignals(slot_to_io)
  slot_insts = getSlotInst(slot_to_io, ctrl_signals, top_rtl_parser, s_axi_ctrl_signals, target)
  ending = ['endmodule']

  # append our fifo template at the end. Separate files may not be detected by HLS when packing into xo 
  new_top = header + top_io + wire_decl + pipeline + ctrl + slot_insts + ending + [fifo_template]

  # add empty wrappers for compatibility with black box if targeting implementation
  if target == 'hw':
    new_top += wrapper_creater.getEmptyWrappers()
  
  return '\n'.join(new_top)
