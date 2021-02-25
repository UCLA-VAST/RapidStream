#! /usr/bin/python3.6
import logging
from autoparallel.FE.Slot import Slot
from autoparallel.FE.TopRTLParser import TopRTLParser
from autoparallel.FE.FIFOTemplate import fifo_template
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

def getWireDecl(slot_to_io, ctrl_signals, top_rtl_parser):
  """
  declare connecting wires
  need to filter out the IOs
  also filter out the ap signals (separately handled)
  """

  wire_decl = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:
      # a wire will be the input of one module
      # and the output of another, so avoid declare twice
      if io[0] != 'output': 
        continue

      # filter ap signals. Handled separately
      if io[-1].startswith('ap_'): 
        continue

      # IO cannot be redefined as wire
      if top_rtl_parser.isIO(io[-1]):
        continue

      # add the wire to declaration
      wire_decl.append('  wire ' + ' '.join(io[1:]) + ';')
  return wire_decl

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

  for slot in slot_to_io.keys(): 
    ctrl_section.append(f'  wire ap_start_{slot} = ap_start_orig;')
    ctrl_section.append(f'  wire ap_done_{slot};')
    ctrl_section.append(f'  wire ap_idle_{slot};')
    ctrl_section.append(f'  wire ap_ready_{slot};')
    ctrl_section.append(f'  wire ap_continue_{slot} = 1\'b1;')
    ctrl_section.append(f'  wire ap_rst_n_{slot} = ap_rst_n;')

  ctrl_section.append(f'  assign ap_done_final = 1\'b1 ' + \
    ' '.join([f'& ap_done_{slot}' for slot in slot_to_io.keys()]) + ';' )
  ctrl_section.append(f'  assign ap_ready_final = ap_done_final;')
  ctrl_section.append(f'  assign ap_idle_final = ap_done_final;')

  return ctrl_section

def getSlotInst(slot_to_io, ctrl_signals):
  # instantiate each slot
  slot_insts = []
  
  for slot, io_list in slot_to_io.items():
    slot_insts.append(f'\n\n  {slot} {slot}_U0 (')
    for io in io_list:
      # differential control signal
      if io[-1] in ctrl_signals:
        slot_insts.append(f'    .{io[-1]}({io[-1]}_{slot}),')
      else:
        slot_insts.append(f'    .{io[-1]}({io[-1]}),')

    # handle the last io
    slot_insts[-1] = slot_insts[-1].replace(',', '\n  );') 
  
  return slot_insts

def CreateTopRTL(top_rtl_parser, wrapper_creater, top_module_name):
  slot_to_io = wrapper_creater.getSlotToIO()
  ctrl_signals = set(['ap_start', 'ap_done', 'ap_idle', 'ap_ready', 'ap_continue', 'ap_rst_n'])

  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {top_module_name} (']
  top_io = getTopIO(top_rtl_parser)
  wire_decl = getWireDecl(slot_to_io, ctrl_signals, top_rtl_parser)
  ctrl = getCtrlSignals(slot_to_io)
  slot_insts = getSlotInst(slot_to_io, ctrl_signals)
  ending = ['endmodule']

  # append our fifo template at the end. Separate files may not be detected by HLS when packing into xo 
  new_top = header + top_io + wire_decl + ctrl + slot_insts + ending + [fifo_template]
  open(f'wrapper_rtl/{top_module_name}.v', 'w').write('\n'.join(new_top))
