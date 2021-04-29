#! /usr/bin/python3.6
import logging
import json
  
def getStrictAnchoredIO(hub, slot_name):
  """ which IOs will connect to other slots with anchor registers """
  anchored_io_and_wired_io = getAnchoredIOAndWiredIO(hub, slot_name)
  return [io for io in anchored_io_and_wired_io if '_pass_0' in io[-1]]

def getAnchoredIOAndWiredIO(hub, slot_name):
  """ 
  which IOs of the slot will connect to other slots
  In the actual top RTL, some IOs will be registered while some are connected by direct wire
  However, in this wrapper we also create an anchor register for those wire-connected IOs
  because we need to properly constrain the orientation of the connection
  """
  slot_to_io = hub['SlotIO']
  io_list = slot_to_io[slot_name]

  all_top_io = hub['TopIO']
  top_io_names = set(io[-1] for io in all_top_io)

  non_top_io_list = [io for io in io_list if io[-1] not in top_io_names] # not in top_io
  return non_top_io_list

def getLocalTopLevelPorts(hub, slot_name):
  """
  get those IOs of the slot that belong to the top-level ports
  They will be left unconstrainted 
  """
  slot_to_io = hub['SlotIO']
  io_list = slot_to_io[slot_name]

  all_top_io = hub['TopIO']
  top_io_names = set(io[-1] for io in all_top_io)

  local_top_io_list = [io for io in io_list if io[-1] in top_io_names] # in top_io
  return local_top_io_list

def createAnchorWrapper(hub, slot_name, output_path='.'):
  """
  Top-level ports will be directly connected
  All other IOs will be registered
  """
  slot_to_io = hub['SlotIO']
  slot_to_rtl = hub['SlotWrapperRTL']
  io_list = slot_to_io[slot_name]

  # IOs that are not top-level port
  non_top_io_list = getAnchoredIOAndWiredIO(hub, slot_name)
  
  # top-level ports are unconstrained
  local_top_io_list = getLocalTopLevelPorts(hub, slot_name)

  wrapper = []
  
  # header
  wrapper.append(r'`timescale 1 ns / 1 ps')
  wrapper.append(f'module {slot_name}_anchored (')
  for io in io_list[:-1]:
    wrapper.append('    ' + ' '.join(io) + ',')
  wrapper.append('    ' + ' '.join(io_list[-1]) + ');')

  # anchor registers
  for io in non_top_io_list:
    wrapper.append('  ' + '(* dont_touch = "yes" *) reg ' + ' '.join(io[1:]) + '_q0' + ';')

  # wire connection to inst
  for io in non_top_io_list:
    if io[0] == 'output':
      wrapper.append('  ' + 'wire ' + ' '.join(io[1:]) + '_internal' + ';')
      wrapper.append(f'  assign {io[-1]} = {io[-1]}_q0;')

  # connect anchors
  wrapper.append('  ' + 'always @ (posedge ap_clk) begin')
  for io in non_top_io_list:
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
    if io in non_top_io_list:
      if io[0] == 'input':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_q0),')
      elif io[0] == 'output':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_internal),')
    elif io in local_top_io_list:
      wrapper.append('    ' + f'.{io[-1]}({io[-1]}),') # direct connection to interface
  wrapper[-1] = wrapper[-1].replace(',', ');')

  # ending
  wrapper.append('endmodule')

  file = open(f'{output_path}/{slot_name}_anchored.v', 'w')
  file.write('\n'.join(wrapper))

  # add the rtl for the inner module (the slot wrapper)
  # discard the first line (time scale)
  assert 'timescale' in slot_to_rtl[slot_name][0]
  file.write('\n\n')
  file.write('\n'.join(slot_to_rtl[slot_name][1:]))

if __name__ == '__main__':
  fe_result_path = '../FE/hub.json'
  hub = json.loads(open(fe_result_path, 'r').read())
  for slot_name in hub['SlotIO'].keys():
    createAnchorWrapper(hub, slot_name)
