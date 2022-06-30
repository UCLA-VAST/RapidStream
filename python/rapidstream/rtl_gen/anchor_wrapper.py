import logging
from typing import Dict, List

from rapidstream.const import *
from rapidstream.rtl_gen.const import *
from rapidstream.rtl_gen.group_wrapper import get_io_section, get_ending

_logger = logging.getLogger().getChild(__name__)


def is_skip_port(name: str) -> bool:
  # do not anchor the clock signal
  if name == 'ap_clk' or name == 'ap_rst_n':
    return True
  # do not anchor the top_level_IO
  elif 'm_axi_' in name or 's_axi_control_' in name:
    return True
  else:
    return False


def get_anchor_section(v_props: Dict) -> List[str]:
  rtl = []
  for io_dir, name_to_width in v_props['io_dir_to_name_to_width'].items():
    for name, width in name_to_width.items():
      if is_skip_port(name):
        continue

      rtl.append(f'(* dont_touch = "yes" *) reg {width} {name}_anchor;')
      rtl.append(f'wire {width} {name}_anchor_in;')
      rtl.append(f'wire {width} {name}_anchor_out;')
      rtl.append(f'wire {width} {name}_inst;')
      rtl.append(f'always @ (posedge ap_clk) {name}_anchor <= {name}_anchor_in;')
      rtl.append(f'assign {name}_anchor_out = {name}_anchor;')

      if io_dir == 'input':
        rtl.append(f'assign {name}_anchor_in = {name};')
        rtl.append(f'assign {name}_inst = {name}_anchor_out;')
      elif io_dir == 'output':
        rtl.append(f'assign {name}_anchor_in = {name}_inst;')
        rtl.append(f'assign {name} = {name}_anchor_out;')
      else:
        assert False

      rtl.append('')

  return rtl


def get_inner_vertex_instance(v_props: Dict) -> List[str]:
  rtl = []

  rtl.append(f'{v_props["module"]} {v_props["instance"]} (')

  for io_dir, name_to_width in v_props['io_dir_to_name_to_width'].items():
    for name, width in name_to_width.items():
      if is_skip_port(name):
        rtl.append(f'  .{name}({name}),')
      else:
        rtl.append(f'  .{name}({name}_inst),')

  rtl[-1] = rtl[-1].replace(',', ');')

  return rtl


def get_anchor_wrapper(
  group_vertex_props: Dict,
) -> List[str]:
  """Register each IO port except the clock"""
  wrapper = []
  wrapper += get_io_section(group_vertex_props, suffix = ANCHOR_WRAPPER_SUFFIX)
  wrapper += get_anchor_section(group_vertex_props)
  wrapper += get_inner_vertex_instance(group_vertex_props)
  wrapper += get_ending()

  return wrapper


def get_empty_island(group_vertex_props: Dict) -> List[str]:
  """Create a dummy module that only includes a register for each IO"""
  wrapper = []
  wrapper += get_io_section(group_vertex_props, suffix = '_empty')
  wrapper += get_anchor_section(group_vertex_props)
  wrapper += get_ending()

  return wrapper
