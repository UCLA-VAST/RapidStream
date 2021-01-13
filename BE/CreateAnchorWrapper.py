#! /usr/bin/python3.6
import logging
import json

def __getDataAndCtrlIOs(io_list):
  data_io = [] 
  ctrl_io = []
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

  for io in io_list:
    if any(tag in io[-1] for tag in ap_tags + axi_tags):
      ctrl_io.append(io)
    else:
      data_io.append(io)
  
  return data_io, ctrl_io

def addAnchorInfoToJson(fe_result):
  slot_to_anchor = {}
  slot_to_io = fe_result['SlotIO']
  for slot, io_list in slot_to_io.items():
    data_io, ctrl_io = __getDataAndCtrlIOs(io_list)
    anchor_list = []
    for io in data_io:
      anchor_list.append(io[-1])
    slot_to_anchor[slot] = anchor_list

  fe_result['SlotAnchors'] = slot_to_anchor
  file = open('BE_pass1_anchored.json', 'w')
  file.write(json.dumps(fe_result, indent=2))
  
def createAnchorWrapper(fe_result):
  slot_to_io = fe_result['SlotIO']
  for slot, io_list in slot_to_io.items():
    file = open(f'{slot}_anchored.v', 'w')
    data_io, ctrl_io = __getDataAndCtrlIOs(io_list)

    wrapper = []
    
    # header
    wrapper.append(r'`timescale 1 ns / 1 ps')
    wrapper.append(f'module {slot}_anchored (')
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
    wrapper.append('  ' + f'(* keep_hierarchy = "yes" *) {slot} {slot}_U0 (' )
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

if __name__ == '__main__':
  fe_result_path = '../FE/FE_result.json'
  fe_result = json.loads(open(fe_result_path, 'r').read())
  createAnchorWrapper(fe_result)
  addAnchorInfoToJson(fe_result)
