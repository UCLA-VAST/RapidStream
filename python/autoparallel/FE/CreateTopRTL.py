#! /usr/bin/python3.6
import logging
from autoparallel.FE.Slot import Slot
from autoparallel.FE.TopRTLParser import TopRTLParser
import re

def getTopIO(top_rtl_parser):
  # get the IO section 
  top_io_list = top_rtl_parser.getDirWidthNameOfAllIO()
  assert any(re.search('ap_rst_n', io[-1]) for io in top_io_list)
  
  io_rtl = ['module Top (']
  io_rtl += ['  ' + ' '.join(io) + ',' for io in top_io_list]
  io_rtl[-1] = io_rtl[-1].replace(',', '\n);')

  return io_rtl

def getWireDecl(slot_to_io, ctrl_signals):
  # declare connecting wires
  wire_decl = []
  for slot, io_list in slot_to_io.items():
    for io in io_list:
      if io[0] == 'output' and \
        not io[-1].startswith('ap_'):
        wire_decl.append('  wire ' + ' '.join(io[1:]) + ';')
  return wire_decl

def getCtrlSignals(slot_to_io):
  # control signals
  ctrl_section = []
  ctrl_section.append(f'  wire ap_start_orig;')
  ctrl_section.append(f'  wire ap_done_final;')
  ctrl_section.append(f'  wire ap_ready_final;')
  ctrl_section.append(f'  wire ap_idle_final;')

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

def CreateTopRTL(top_rtl_parser, wrapper_creater):
  slot_to_io = wrapper_creater.getSlotToIO()
  ctrl_signals = set(['ap_start', 'ap_done', 'ap_idle', 'ap_ready', 'ap_continue', 'ap_rst_n'])

  header = ['`timescale 1 ns / 1 ps']
  top_io = getTopIO(top_rtl_parser)
  wire_decl = getWireDecl(slot_to_io, ctrl_signals)
  ctrl = getCtrlSignals(slot_to_io)
  slot_insts = getSlotInst(slot_to_io, ctrl_signals)
  ending = ['endmodule']

  new_top = header + top_io + wire_decl + ctrl + slot_insts + ending
  open('wrapper_rtl/Top.v', 'w').write('\n'.join(new_top))
