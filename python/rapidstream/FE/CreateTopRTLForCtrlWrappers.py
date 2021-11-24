#! /usr/bin/python3.6
import logging
from autobridge.HLSParser.vivado_hls.TopRTLParser import TopRTLParser
from autobridge.Codegen.FIFOTemplate import fifo_template
from rapidstream.FE.GlobalRouting import GlobalRouting
import re
import collections


def _addClockBuffer(io_rtl):
  """
  explicitly add a clock buffer so that clock net could be fully routed
  """
  io_rtl_clk_buffer = [io.replace('ap_clk', 'ap_clk_port') for io in io_rtl]
  io_rtl_clk_buffer.append(f'wire ap_clk; ')
  io_rtl_clk_buffer.append(f'(* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg ( ')
  io_rtl_clk_buffer.append(f'  .I(ap_clk_port), ')
  io_rtl_clk_buffer.append(f'  .CE(1\'b1),')
  io_rtl_clk_buffer.append(f'  .O(ap_clk) );')

  return io_rtl_clk_buffer

def getTopIO(top_rtl_parser, target):
  # get the IO section 
  top_io_list = top_rtl_parser.getDirWidthNameOfAllIO()
  assert any(re.search('ap_rst_n', io[-1]) for io in top_io_list)
  
  io_rtl = ['  ' + ' '.join(io) + ',' for io in top_io_list]
  io_rtl[-1] = io_rtl[-1].replace(',', '\n);\n')

  # vitis requires the original parameters be kept
  param_to_value_str = top_rtl_parser.getParamToValueStr()
  param_sec = [f'  parameter {param} = {value};' for param, value in param_to_value_str.items()]

  # if not for cosim, explicity add clock buffers
  if target == 'hw':
    io_rtl = _addClockBuffer(io_rtl)

  return io_rtl + param_sec

def getWireDecl(slot_to_io, top_rtl_parser):
  """
  declare connecting wires
  need to filter out the IOs
  also filter out the ap signals (separately handled)
  """

  wire_decl = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:
      if top_rtl_parser.isIO(io[-1]):
        continue
  
      # add the wire to declaration
      if io[0] == 'output': 
        wire_decl.append('  wire ' + ' '.join(io[1:]) + '_out;')
      elif io[0] == 'input':
        wire_decl.append('  wire ' + ' '.join(io[1:]) + '_in;')

  dups = [item for item, count in collections.Counter(wire_decl).items() if count > 1]
  assert len(dups) == 0, dups

  return wire_decl

def getTopApSignals(slot_to_io):
  """ HLS simulator requires that there is an ap_done at the top level """

  # find which slot has the s_axi_control
  for slot, io_list in slot_to_io.items():
    if any('s_axi' in io[-1] for io in io_list):
      # note the naming convention 
      ap_done_source = [f'{io[-1]}_in' for io in io_list if 'ap_done' in io[-1]]
      ap_start_source = [f'{io[-1]}_out' for io in io_list if 'ap_start' in io[-1]]

      top_ap_signals = []
      top_ap_signals.append(f'wire ap_done = ' + ' & '.join(ap_done_source) + ';')
      top_ap_signals.append('wire ap_idle = ap_done;')
      top_ap_signals.append('wire ap_ready = ap_done;')
      top_ap_signals.append(f'wire ap_start = {ap_start_source[0]};') # only need 1 ap_start
      return top_ap_signals

  assert False

def getPipelining(slot_to_io, top_rtl_parser, global_router, in_slot_pipeline_style):
  """
  add pipeline registers to connect the slots
  Differentiate whether we include the interconnect registesr in slot wrappers
  Now that we decide to put the pipeline of passing edges inside the slot, 
  we should not pipeline them outside slots
  """

  pipeline = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:

      # choose to work on the output side
      if io[0] != 'output': 
        continue # otherwise we do the same thing twice for each edge

      if top_rtl_parser.isIO(io[-1]):
        continue
      
      # check if the io belongs to a passing wire
      # orig_io_name = io[-1].split('_pass_')[0]
      # e_name = top_rtl_parser.getFIFONameFromWire(orig_io_name)
      # edge_latency = global_router.getPipelineLevelOfEdgeName(e_name)

      # [a potential equivalent implementation]
      # ------------------------------------------------
      # if edge_latency > 1: # the edge will pass through other slots
      #   # the actual pipelining registers are in the passed slots
      #   pipeline_level = 0

      #   # corner case: still add the pipelining for the first segment, only for the income full_n
      #   # otherwise the broadcast issue of the full_n will be serious
        
      # elif edge_latency == 1: # the edge connect two neighbors
      #   # the pipelining registers are between the two neighbors
      #   pipeline_level = 1
      # else:
      #   assert False
      # -------------------------------------------------
      # Do it in a easier way. Just check '_pass_0'
      if in_slot_pipeline_style == 'REG':
        if re.search('_pass_0', io[-1]):
          pipeline_level = 1
        else:
          pipeline_level = 0
      elif in_slot_pipeline_style == 'LUT':
        pipeline_level = 1
      elif in_slot_pipeline_style == 'WIRE':
        pipeline_level = 1
      elif in_slot_pipeline_style == 'DOUBLE_REG':
        pipeline_level = 1
      elif in_slot_pipeline_style == 'INVERT_CLOCK':
        pipeline_level = 1
      else:
        assert False

      # assign the input wire equals the output wire
      if pipeline_level == 0:
        pipeline.append(f'  assign {io[-1]}_in = {io[-1]}_out;')
      else:
        # add the pipeline registers
        for i in range(pipeline_level):
          width = io[1] if len(io) == 3 else ''
          pipeline.append(f'  (* dont_touch = "yes" *) reg {width} {io[-1]}_q{i};')
      
        # connect the head and tail
        if in_slot_pipeline_style == 'INVERT_CLOCK':
          pipeline.append(f'  always @ (negedge ap_clk) begin')
        else:
          pipeline.append(f'  always @ (posedge ap_clk) begin')

        pipeline.append(f'    {io[-1]}_q0 <= {io[-1]}_out;')
        for i in range(1, pipeline_level):
          pipeline.append(f'    {io[-1]}_q{i} <= {io[-1]}_q{i-1};')
        pipeline.append(f'  end')
        pipeline.append(f'  assign {io[-1]}_in = {io[-1]}_q{pipeline_level-1};')
  
  return pipeline

def getSlotInst(slot_to_io, top_rtl_parser):
  # instantiate each slot
  slot_insts = []
  
  for slot, io_list in slot_to_io.items():

    slot_insts.append(f'\n\n  (* keep_hierarchy = "yes" *) {slot}_ctrl {slot}_ctrl_U0 (')
    for io in io_list:
      if top_rtl_parser.isIO(io[-1]):
        # directly connect to top-level IO
        slot_insts.append(f'    .{io[-1]}({io[-1]}),')
      else:
        # differentiate direction for pipelining purpose
        if io[0] == 'input':
          slot_insts.append(f'    .{io[-1]}({io[-1]}_in),')
        elif io[0] == 'output':
          slot_insts.append(f'    .{io[-1]}({io[-1]}_out),')
        else: assert False, io[0]

    # handle the last io
    slot_insts[-1] = slot_insts[-1].replace(',', '\n  );') 
  
  return slot_insts

def CreateTopRTLForCtrlWrappers(top_rtl_parser, wrapper_creater, top_module_name, global_router, target):
  slot_to_io = wrapper_creater.getSlotNameToIOList()
  
  # whether the pipeline regs are in slots or between slots
  in_slot_pipeline_style = wrapper_creater.in_slot_pipeline_style

  # to differentiate with the original top
  if target == 'hw':
    top_module_name += '_hw_test'

  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {top_module_name} (']
  top_io = getTopIO(top_rtl_parser, target)
  wire_decl = getWireDecl(slot_to_io, top_rtl_parser)
  top_ap_signals = getTopApSignals(slot_to_io)
  pipeline = getPipelining(slot_to_io, top_rtl_parser, global_router, in_slot_pipeline_style)
  slot_insts = getSlotInst(slot_to_io, top_rtl_parser)
  ending = ['endmodule']

  # append our fifo template at the end. Separate files may not be detected by HLS when packing into xo 
  new_top = header + top_io + wire_decl + pipeline + top_ap_signals + slot_insts +  ending + [fifo_template]
  # new_top = header + top_io + wire_decl + pipeline + slot_insts + ending

  return '\n'.join(new_top)
