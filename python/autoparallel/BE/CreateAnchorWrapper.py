#! /usr/bin/python3.6
import logging
import json
  
def createAnchorWrapper(fe_result, slot_name, output_path='.'):
  slot_to_io = fe_result['SlotIO']
  slot_to_rtl = fe_result['SlotWrapperRTL']
  io_list = slot_to_io[slot_name]

  all_top_io = fe_result['TopIO']
  top_io_names = set(io[-1] for io in all_top_io)

  internal_io_list = [io for io in io_list if io[-1] not in top_io_names]
  local_top_io_list = [io for io in io_list if io[-1] in top_io_names]

  file = open(f'{output_path}/{slot_name}_anchored.v', 'w')

  wrapper = []
  
  # header
  wrapper.append(r'`timescale 1 ns / 1 ps')
  wrapper.append(f'module {slot_name}_anchored (')
  for io in io_list[:-1]:
    wrapper.append('    ' + ' '.join(io) + ',')
  wrapper.append('    ' + ' '.join(io_list[-1]) + ');')

  # anchor registers
  for io in internal_io_list:
    wrapper.append('  ' + '(* dont_touch = "yes" *) reg ' + ' '.join(io[1:]) + '_q0' + ';')

  # wire connection to inst
  for io in internal_io_list:
    if io[0] == 'output':
      wrapper.append('  ' + 'wire ' + ' '.join(io[1:]) + '_internal' + ';')

  # connect anchors
  wrapper.append('  ' + 'always @ (posedge ap_clk) begin')
  for io in internal_io_list:
    if io[0] == 'input':
      wrapper.append('    ' + f'{io[-1]}_q0 <= {io[-1]};')
    elif io[0] == 'output':
      wrapper.append('    ' + f'{io[-1]}_q0 <= {io[-1]}_internal;')
    else:
      assert False
  wrapper.append('  ' + 'end')

  # instantiate slot wrapper. DO NOT change the suffix '_U0'
  wrapper.append('  ' + f'(* dont_touch = "yes" *) {slot_name}_ctrl {slot_name}_U0 (' )
  for io in io_list: # try to preserve order
    if io in internal_io_list:
      if io[0] == 'input':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_q0),')
      elif io[0] == 'output':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_internal),')
    elif io in local_top_io_list:
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
