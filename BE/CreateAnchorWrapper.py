#! /usr/bin/python3.6
import logging
import json

def isCtrlIO(io_name):
  ap_tags = [ 'ap_start', 
              'ap_done', 
              'ap_ready', 
              'ap_idle', 
              'ap_continue', 
              'ap_clk', 
              'ap_rst', 
              'ap_rst_n',
              'ARESET',
              'ap_rst_inv_n',
              'interrupt']
  axi_tags = ['s_axi', 'm_axi', 'S_AXI', 'M_AXI']

  return any(tag in io_name for tag in ap_tags + axi_tags)

def __getDataAndCtrlIOs(io_list):
  data_io = [] 
  ctrl_io = []


  for io in io_list:
    if isCtrlIO(io[-1]):
      ctrl_io.append(io)
    else:
      data_io.append(io)
  
  return data_io, ctrl_io

def addAnchorInfoToJson(fe_result, output_path='.'):
  slot_to_anchor = {}
  slot_to_io = fe_result['SlotIO']
  for slot, io_list in slot_to_io.items():
    data_io, ctrl_io = __getDataAndCtrlIOs(io_list)
    anchor_list = []
    for io in data_io:
      anchor_list.append(io[-1])
    slot_to_anchor[slot] = anchor_list

  fe_result['SlotAnchors'] = slot_to_anchor
  file = open(f'{output_path}/BE_pass1_anchored.json', 'w')
  file.write(json.dumps(fe_result, indent=2))
  
def createAnchorWrapper(fe_result, slot_name, output_path='.'):
  slot_to_io = fe_result['SlotIO']
  slot_to_rtl = fe_result['SlotWrapperRTL']
  io_list = slot_to_io[slot_name]

  file = open(f'{output_path}/{slot_name}_anchored.v', 'w')
  data_io, ctrl_io = __getDataAndCtrlIOs(io_list)

  wrapper = []
  
  # header
  wrapper.append(r'`timescale 1 ns / 1 ps')
  wrapper.append(f'module {slot_name}_anchored (')
  for io in io_list[:-1]:
    wrapper.append('    ' + ' '.join(io) + ',')
  wrapper.append('    ' + ' '.join(io_list[-1]) + ');')

  # anchor registers
  for io in data_io:
    wrapper.append('  ' + '(* dont_touch = "yes" *) reg ' + ' '.join(io[1:]) + '_anchor' + ';')

  # wire connection to inst
  for io in data_io:
    if io[0] == 'output':
      wrapper.append('  ' + 'wire ' + ' '.join(io[1:]) + '_internal' + ';')

  # connect anchors
  wrapper.append('  ' + 'always @ (posedge ap_clk) begin')
  for io in data_io:
    if io[0] == 'input':
      wrapper.append('    ' + f'{io[-1]}_anchor <= {io[-1]};')
    elif io[0] == 'output':
      wrapper.append('    ' + f'{io[-1]}_anchor <= {io[-1]}_internal;')
    else:
      assert False
  wrapper.append('  ' + 'end')

  # instantiate slot wrapper
  wrapper.append('  ' + f'(* keep_hierarchy = "yes" *) {slot_name} {slot_name}_U0 (' )
  for io in io_list: # try to preserve order
    if io in data_io:
      if io[0] == 'input':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_anchor),')
      elif io[0] == 'output':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_internal),')
    elif io in ctrl_io:
      wrapper.append('    ' + f'.{io[-1]}({io[-1]}),') # direct connection to interface
  wrapper[-1] = wrapper[-1].replace(',', ');')

  # ending
  wrapper.append('endmodule')

  file.write('\n'.join(wrapper))

  # add the rtl for the inner module (the slot wrapper)
  # discard the first line (time scale)
  assert 'timescale' in slot_to_rtl[slot_name][0]
  file.write('\n\n')
  file.write('\n'.join(slot_to_rtl[slot_name][1:]))

if __name__ == '__main__':
  fe_result_path = '../FE/FE_result.json'
  fe_result = json.loads(open(fe_result_path, 'r').read())
  for slot_name in fe_result['SlotIO'].keys():
    createAnchorWrapper(fe_result, slot_name)
  addAnchorInfoToJson(fe_result)
