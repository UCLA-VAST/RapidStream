#! /usr/bin/python3.6
import logging
import json
import sys

def getHeader(slot1_name, slot2_name):
  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {slot1_name}_AND_{slot2_name} (']
  return header

def getIODecl(slot1_io : dict, slot2_io : dict, top_io : dict):
  slot_io_merge = {**slot1_io, **slot2_io}
  io_decl = [f'  {" ".join(slot_io_merge[io])} {io},' for io in top_io]
  io_decl += ['  input ap_start,']

  # leave the output ap signals dangling as they are not used here
  # io_decl += ['  output ap_done,']
  # io_decl += ['  output ap_idle,']
  # io_decl += ['  output ap_ready,']
  io_decl += ['  input ap_continue,']
  io_decl += ['  input ap_clk,']
  io_decl += ['  input ap_rst_n']
  return io_decl

def getPipeline(inner_connection, pipeline_level):
  pipeline = []
  for io, dir_width in inner_connection.items():  
    # assign the input wire equals the output wire
    if pipeline_level == 0:
      pipeline.append(f'  assign {io}_in = {io}_out;')
    else:
      # add the pipeline registers
      for i in range(pipeline_level):
        width = dir_width[1] if len(dir_width) == 2 else ''
        pipeline.append(f'  (* dont_touch = "yes" *) reg {width} {io}_q{i};')
    
      # connect the head and tail
      pipeline.append(f'  always @ (posedge ap_clk) begin')
      pipeline.append(f'    {io}_q0 <= {io}_out;')
      for i in range(1, pipeline_level):
        pipeline.append(f'    {io}_q{i} <= {io}_q{i-1};')
      pipeline.append(f'  end')
      pipeline.append(f'  assign {io}_in = {io}_q{pipeline_level-1};')

  return pipeline

def getInstance(slot_name : str, slot_io : dict, top_io : dict, inner_connection : dict):
  instance = []
  instance.append(f'  (* black_box *) {slot_name} {slot_name}_U0 (')
  for io, dir_width in slot_io.items():
    if io in top_io:
      instance.append(f'    .{io}({io}),')
    elif io in inner_connection:
      # handle ap signals
      if io.startswith('ap_'):
        # leave the output ap signals dangling as they are not used here
        if io in ['ap_done', 'ap_idle', 'ap_ready']:
          instance.append(f'    .{io}(),')
        else:
          instance.append(f'    .{io}({io}),')
      # data signals    
      else:
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

def CreateWrapperForSlotPair(hub, slot1_name, slot2_name, pipeline_level = 1):
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

  header = getHeader(slot1_name, slot2_name)
  io_decl = getIODecl(slot1_io, slot2_io, top_io)

  # pipelined connection between the two slots
  pipeline = getPipeline(inner_connection, pipeline_level)
  
  slot1_inst = getInstance(slot1_name, slot1_io, top_io, inner_connection)
  slot2_inst = getInstance(slot2_name, slot2_io, top_io, inner_connection)
  ending = ['endmodule\n']

  return header + io_decl + pipeline + slot1_inst + slot2_inst + ending

def CreateWrapperForAllSlotPairs(hub):
  pairs = hub['ComputeSlotPairs']
  for pair in pairs:
    pair_wrapper = CreateWrapperForSlotPair(hub, pair[0], pair[1])
    open(f'{"_AND_".join(pair)}.v', 'w').write('\n'.join(pair_wrapper))

if __name__ == '__main__':
  hub_addr = sys.argv[1]
  hub = json.loads(open(hub_addr, 'r').read())
  CreateWrapperForAllSlotPairs(hub)