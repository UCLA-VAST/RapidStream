from typing import Dict, List

from rapidstream.rtl_gen.const import *
from rapidstream.rtl_gen.ctrl_wrapper import get_param_decl_section
from rapidstream.rtl_gen.top import (
  _get_wire_to_io_of_slot,
  get_selected_anchor_reg_decl,
  _get_slot_inst,
  set_unused_ports,
  get_ending,
  sort_rtl,
)


def get_impl_wrapper_io_section(config: Dict, top_name: str, connect_to_shell: bool) -> List[str]:
  """We will use fake abstract shells for island placement. If an island connects to the shell directly
     The IO section of the wrapper will include all ports to the shell
     If the island only connects to other islands, then the wrapper should only have the ap_clk port
  """
  io = []

  io.append('`timescale 1 ns / 1 ps')
  io.append('')
  io.append(f'(* dont_touch = "yes" *) module {top_name} (')

  # the ctrl island connects to hmss shell IOs
  if connect_to_shell:
    for name, width in config['input_decl'].items():
      io.append(f'input {width} {name},')
    for name, width in config['output_decl'].items():
      io.append(f'output {width} {name},')

  # in the dummy abstract shell, the black box only has an clock port
  else:
    io.append(f'  input ap_clk,')

  io[-1] = io[-1].strip(',')
  io.append(');')
  io.append('')

  io += get_param_decl_section(config)


  return io


def get_top_with_one_island(config: Dict, use_anchor_wrapper: bool) -> Dict[str, List[str]]:
  """for each island, generate a top that only instantiates one island in the top
     if a top-level output port is not connected to the given island, assign it to 0
  """
  wrapper_suffix = ANCHOR_WRAPPER_SUFFIX if use_anchor_wrapper else ''
  island_name_to_wrapper = {}
  for v_name, v_props in config['vertices'].items():
    wire_to_io = _get_wire_to_io_of_slot(v_props)
    top = []
    top += get_selected_anchor_reg_decl(config, wire_to_io) + ['']
    top += _get_slot_inst(v_props, wrapper_suffix) + ['']
    top += set_unused_ports(config, wire_to_io)
    top += get_ending() + ['']
    top_sorted = sort_rtl(top)

    # FIXME: hardcode island name here
    connect_to_shell = v_name == 'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3'
    top = get_impl_wrapper_io_section(config, f'{v_name}_backend_top', connect_to_shell) + [''] + top_sorted + ['']
    island_name_to_wrapper[v_name] = top

  return island_name_to_wrapper
