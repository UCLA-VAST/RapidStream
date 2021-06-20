from collections import Counter
import sys
import json
import re
import os

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
    if io_name != 'ap_clk':
      io_decl.append(f'  {" ".join(dir_and_width)} {io_name},')
    else:
      io_decl.append(f'  {" ".join(dir_and_width)} ap_clk_port,')

  io_decl[-1] = io_decl[-1].replace(',', ');')

  io_decl.append(f'  wire ap_clk; ')
  io_decl.append(f'  (* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *) BUFGCE test_bufg ( ')
  io_decl.append(f'    .I(ap_clk_port), ')
  io_decl.append(f'    .CE(1\'b1),')
  io_decl.append(f'    .O(ap_clk));')
  io_decl.append(f'  );')

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

  pair_wrapper = header + io_decl + stitch_rtl
  for slot_inst in slot_instance_list:
    pair_wrapper += slot_inst
  pair_wrapper += ending
  
  for slot_def in slot_empty_def_list:
   pair_wrapper += slot_def

  return pair_wrapper, external_io_name_2_dir_and_width, inner_io_name_2_dir_and_width

###################### Utilities ##########################

def getSlotsInSLRIndex(hub, slr_index):
  """
  get all slots within a given SLR
  """
  all_slot_names = hub['SlotIO'].keys()
  slots_in_slr = []
  for name in all_slot_names:
    match = re.search(r'CR_X(\d+)Y(\d+)_To_CR_X(\d+)Y(\d+)', name)
    DL_y = int(match.group(2))
    UR_y = int(match.group(4))

    # assume that each SLR has 4 rows of clock regions
    if slr_index * 4 <= DL_y <= slr_index * 4 + 3:
      if slr_index * 4 <= UR_y <= slr_index * 4 + 3:
        slots_in_slr.append(name)

  return slots_in_slr

def getSLRLevelWrappers(hub, slr_num):
  """
  get a wrapper for all slots within an SLR
  """
  get_io_name_2_dir_and_width = lambda slot_io_list : {io[-1] : io[0:-1] for io in slot_io_list}

  for slr_index in range(slr_num):
    os.mkdir(f'{slr_stitch_dir}/slr_{slr_index}')
    slr_slots = getSlotsInSLRIndex(hub, slr_index)
      
    slr_slot_name_2_dir_and_width_and_io_name = {
      name : get_io_name_2_dir_and_width(hub['SlotIO'][name]) for name in slr_slots}

    slr_wrapper, _, __ = getWrapperOfSlots(f'slr_{slr_index}', slr_slot_name_2_dir_and_width_and_io_name, pipeline_level=1)

    open(f'{slr_stitch_dir}/slr_{slr_index}/slr_{slr_index}_wrapper.v', 'w').write('\n'.join(slr_wrapper))

def getSLRStitchScript(hub, slr_num):
  """
  get the vivado script to stitch all slots within an SLR
  """
  fpga_part_name = hub["FPGA_PART_NAME"]
  pair_list = hub['AllSlotPairs']

  for slr_index in range(slr_num):
    script = []

    script.append(f'set_part {fpga_part_name}')
    script.append(f'read_verilog "{slr_stitch_dir}/slr_{slr_index}/slr_{slr_index}_wrapper.v"')  
    script.append(f'read_xdc "{base_dir}/global_stitch/final_top_clk.xdc"')

    # synth
    script.append(f'synth_design -top "slr_{slr_index}" -part {fpga_part_name} -mode out_of_context')

    # read in the dcp of slots
    slot_names_in_slr = getSlotsInSLRIndex(hub, slr_index)
    for name in slot_names_in_slr:
      script.append(f'read_checkpoint -cell {name}_U0 {prune_dir}/{name}/{name}_after_pruning_anchors.dcp')

    # place the anchors
    for pair in pair_list:
      if pair[0] in slot_names_in_slr and pair[1] in slot_names_in_slr:
        script.append(f'source -notrace {anchor_placement_dir}/{"_AND_".join(pair)}/place_anchors.tcl')

    # add clock stem
    script.append(f'set_property ROUTE "" [get_nets ap_clk]')
    script.append(f'source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl')
    script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

    # SLR boundary should serve as a natural boundary
    script.append(f'delete_pblocks *')

    # theoretically there should be non conflict nets. But we do see the GND net may cause conflicts
    script.append(f'route_design -unroute -nets [get_nets -hierarchical -filter {{ ROUTE_STATUS == "CONFLICTS" }}]')
    script.append(f'write_checkpoint -force slr_{slr_index}_before_routed.dcp')
    script.append(f'route_design -preserve')
    script.append(f'write_checkpoint -force slr_{slr_index}_routed.dcp')

    open(f'{slr_stitch_dir}/slr_{slr_index}/stitch_slr_{slr_index}.tcl', 'w').write('\n'.join(script))

  parallel = [f'cd {slr_stitch_dir}/slr_{slr_index}/ && VIV_VER=2020.1 vivado -mode batch -source stitch_slr_{slr_index}.tcl' \
    for slr_index in range(slr_num)]
  open(f'{slr_stitch_dir}/parallel_slr_stitch.txt', 'w').write('\n'.join(parallel))

###################### TEST ##########################

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())
  prune_dir = f'{base_dir}/pruning_anchors'
  slr_stitch_dir = f'{base_dir}/SLR_level_stitch'
  anchor_placement_dir = f'{base_dir}/ILP_anchor_placement_iter0'
  os.mkdir(slr_stitch_dir)

  getSLRLevelWrappers(hub, slr_num=4)
  getSLRStitchScript(hub, slr_num=4)
