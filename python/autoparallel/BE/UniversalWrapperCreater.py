from collections import Counter

"""
create a wrapper for the given sets of slots
Will replace CreatePairwiseWrapper.py
"""

def getHeader(wrapper_name):
  header = ['\n\n`timescale 1 ns / 1 ps',
            f'module {wrapper_name} (']
  return header

def getIODecl(external_io_name_2_dir_and_width):
  """
  the IO of the wrapper.
  Special treatment for ap_clk. Add a BUFGCE.
  """
  io_decl = []
  for io_name, dir_and_width in external_io_name_2_dir_and_width.items():
    io_decl.append(f'  {" ".join(dir_and_width)} {io_name},')

  io_decl[-1] = io_decl[-1].replace(',', ');')

  return io_decl


def getStitchLogicBetweenSlots(inner_io_name_2_dir_and_width, pipeline_level):
  """
  get the RTL to connect the slots
  data links will be pipelined in the specified pipeline_level
  @param stitch_rtl: the RTL section
  """
  stitch_rtl = []
  for io, dir_and_width in inner_io_name_2_dir_and_width.items():
    width = dir_and_width[1] if len(dir_and_width) == 2 else ''
    stitch_rtl.append(f'  wire {width} {io}_in;')
    stitch_rtl.append(f'  wire {width} {io}_out;')

    # assign the input wire equals the output wire
    if pipeline_level == 0:
      assert False
      stitch_rtl.append(f'  assign {io}_in = {io}_out;')
    else:
      # add the pipeline registers
      for i in range(pipeline_level):
        stitch_rtl.append(f'  (* dont_touch = "yes" *) reg {width} {io}_q{i};')
    
      # connect the head and tail
      stitch_rtl.append(f'  always @ (posedge ap_clk) begin')
      stitch_rtl.append(f'    {io}_q0 <= {io}_out;')
      for i in range(1, pipeline_level):
        stitch_rtl.append(f'    {io}_q{i} <= {io}_q{i-1};')
      stitch_rtl.append(f'  end')
      stitch_rtl.append(f'  assign {io}_in = {io}_q{pipeline_level-1};')

  return stitch_rtl

def getSlotInstance(
    slot_name, 
    slot_io_name_2_dir_and_width : dict, 
    external_io_name_2_dir_and_width : dict, 
    inner_io_name_2_dir_and_width : dict):
  """
  instantiate a slot in the wrapper
  """
  instance = []
  instance.append(f'  (* black_box *) {slot_name} {slot_name}_U0 (')
  for io, dir_width in slot_io_name_2_dir_and_width.items():
    if io in external_io_name_2_dir_and_width:
      instance.append(f'    .{io}({io}),')
    elif io in inner_io_name_2_dir_and_width:
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


def getEmptySlotDefinition(slot_name, slot_io_name_2_dir_and_width):
  """ in order for black_box modules to be recognized by vivado """
  empty_wrapper = []
  empty_wrapper.append(f'\n\nmodule {slot_name} (')
  empty_wrapper += [' '.join(dir_width) + ' ' + io + ',' for io, dir_width in slot_io_name_2_dir_and_width.items()]
  empty_wrapper[-1] = empty_wrapper[-1].replace(',', '')
  empty_wrapper.append(f');')
  empty_wrapper.append(f'endmodule')
  return empty_wrapper


def getExternalAndInnerIOToDirAndWidth(slot_name_2_io_name_2_dir_and_width):
  """
  when we wrap up multiple slots, some slot io become internal connection
  other IOs remain to be the IO of the wrapper
  """

  # io name -> dir + width (in string)
  list_of_io_name_2_dir_width_pair = slot_name_2_io_name_2_dir_and_width.values()
  
  # get the internal IO names and the external IO names
  list_of_io_names = [io_name_2_dir_width_pair.keys() for io_name_2_dir_width_pair in \
                        list_of_io_name_2_dir_width_pair]
  flatten_all_io_names = [n for io_names in list_of_io_names for n in io_names ]
  name_2_freq = Counter(flatten_all_io_names)
  assert any(freq == 1 or freq == 2 or 'ap_clk' in name for name, freq in name_2_freq.items())
  inner_io_names = [name for name, freq in name_2_freq.items() if freq == 2 and 'ap_clk' not in name]
  external_io_names = [name for name, freq in name_2_freq.items() if freq == 1 or 'ap_clk' in name]
  assert len(inner_io_names) + len(external_io_names) == len(name_2_freq) 

  # get the dir and width of each type of IO
  io_name_2_dir_width_pair = {io_name : dir_width_pair \
                    for slot_dict in list_of_io_name_2_dir_width_pair \
                      for io_name, dir_width_pair in slot_dict.items() }
  inner_io_name_2_dir_and_width = {io_name : io_name_2_dir_width_pair[io_name] for io_name in inner_io_names}
  external_io_name_2_dir_and_width = {io_name : io_name_2_dir_width_pair[io_name] for io_name in external_io_names}

  return external_io_name_2_dir_and_width, inner_io_name_2_dir_and_width


def getWrapperOfSlots(wrapper_name, slot_name_2_io_name_2_dir_and_width, pipeline_level):
  """ 
  group together two neighbor slots 
  Wires of passing edges should not be pipelined
  Also create the script to extract the placement of pipeline registers
  """

  external_io_name_2_dir_and_width, inner_io_name_2_dir_and_width = \
    getExternalAndInnerIOToDirAndWidth(slot_name_2_io_name_2_dir_and_width)

  header = getHeader(wrapper_name)
  io_decl = getIODecl(external_io_name_2_dir_and_width)

  # pipelined connection between the two slots
  stitch_rtl = getStitchLogicBetweenSlots(inner_io_name_2_dir_and_width, pipeline_level)

  slot_instance_list = [ 
    getSlotInstance(slot_name, 
    io_name_2_dir_and_width, 
    external_io_name_2_dir_and_width, 
    inner_io_name_2_dir_and_width) for slot_name, io_name_2_dir_and_width in slot_name_2_io_name_2_dir_and_width.items()]

  ending = ['endmodule\n']

  slot_empty_def_list = [getEmptySlotDefinition(slot_name, io_name_2_dir_and_width) \
    for slot_name, io_name_2_dir_and_width in slot_name_2_io_name_2_dir_and_width.items()]

  wrapper = header + io_decl + stitch_rtl
  for slot_inst in slot_instance_list:
    wrapper += slot_inst
  wrapper += ending
  
  for slot_def in slot_empty_def_list:
   wrapper += slot_def

  return wrapper, external_io_name_2_dir_and_width, inner_io_name_2_dir_and_width


def addAnchorToNonTopIOs(hub, inner_module_name, io_list):
  """
  abstract the part to be reused for adding anchors to other wrappers
  """
  # first get the non-top IOs.
  all_top_io = hub['TopIO']
  top_io_names = set(io[-1] for io in all_top_io)
  anchor_io_list = [io for io in io_list if io[-1] not in top_io_names] # not in top_io

  wrapper = []
  
  # header
  wrapper.append(r'`timescale 1 ns / 1 ps')
  wrapper.append(f'module {inner_module_name}_anchored (')
  for io in io_list[:-1]:
    wrapper.append('    ' + ' '.join(io) + ',')
  wrapper.append('    ' + ' '.join(io_list[-1]) + ');')

  # TEST: replace the top port of ap_clk
  wrapper = [line.replace('ap_clk', 'ap_clk_port') for line in wrapper]
  wrapper.append(f'wire ap_clk; ')
  wrapper.append(f'(* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg ( ')
  wrapper.append(f'  .I(ap_clk_port), ')
  wrapper.append(f'  .CE(1\'b1),')
  wrapper.append(f'  .O(ap_clk) );')

  # anchor registers
  for io in anchor_io_list:
    wrapper.append('  ' + '(* dont_touch = "yes" *) reg ' + ' '.join(io[1:]) + '_q0' + ';')

  # wire connection to inst
  # note that the "_in" and "_out" are refered to the IO direction of the module
  # the wire connect to the output pin of a module is suffixed with "_out"
  # in this situation, we regard the input port as the output pin of some external modules
  for io in anchor_io_list:
    wrapper.append('  ' + 'wire ' + ' '.join(io[1:]) + '_in' + ';')
    wrapper.append('  ' + 'wire ' + ' '.join(io[1:]) + '_out' + ';')

    # may seem strange here. 
    # the 'output' port of this wrapper is the 'input' pin of another module
    # thus we name the wire with "_in"
    # this is consistent with the getStitchLogicBetweenSlots()
    if io[0] == 'output':
      wrapper.append(f'  assign {io[-1]} = {io[-1]}_in;')
    elif io[0] == 'input':
      wrapper.append(f'  assign {io[-1]}_out = {io[-1]};')
    else:
      assert False

  # connect anchors
  wrapper.append('  ' + 'always @ (posedge ap_clk) begin')
  for io in anchor_io_list:
    wrapper.append('    ' + f'{io[-1]}_q0 <= {io[-1]}_out;')
  wrapper.append('  ' + 'end')

  for io in anchor_io_list:
    wrapper.append('  assign ' + f'{io[-1]}_in = {io[-1]}_q0;')  

  # instantiate slot wrapper. DO NOT change the suffix '_U0'
  wrapper.append('  ' + f'(* dont_touch = "yes" *) {inner_module_name} {inner_module_name}_U0 (' )
  for io in io_list: # try to preserve order
    if io in anchor_io_list:
      # for an input port, the output of the anchor register will connect to the instance
      if io[0] == 'input':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_in),')
      elif io[0] == 'output':
        wrapper.append('    ' + f'.{io[-1]}({io[-1]}_out),')
    else:
      wrapper.append('    ' + f'.{io[-1]}({io[-1]}),') # direct connection to interface
  wrapper[-1] = wrapper[-1].replace(',', ');')

  # ending
  wrapper.append('endmodule')

  return wrapper
