import logging
import re
from typing import Dict, List

from rapidstream.const import *

_logger = logging.getLogger().getChild(__name__)


def add_constant_input_io_dir(props: Dict) -> None:
  port_wire_map = props['port_wire_map']
  try:
    for const_io in port_wire_map['constant_ports']:
      const_width = props['port_width_map'][const_io]
      props['io_dir_to_name_to_width']['input'][const_io] = const_width
  except:
    import pdb; pdb.set_trace()

def add_m_axi_io_dir(props: Dict) -> None:
  port_wire_map = props['port_wire_map']
  for axi_entry in port_wire_map['axi_ports']:
    if axi_entry['axi_type'] == 'M_AXI':
      axi_data_width = axi_entry['data_width']
      axi_port_name = axi_entry['portname']

      for suffix, dir_and_width in get_m_axi_interface(axi_data_width).items():
        direction = dir_and_width[0]
        width = dir_and_width[1].format(data_width=axi_data_width)
        portname = f'm_axi_{axi_port_name}_{suffix}'

        props['io_dir_to_name_to_width'][direction][portname] = width


def add_stream_io_dir(props: Dict) -> None:
  port_wire_map = props['port_wire_map']

  for stream_name, _port_wire_map in port_wire_map['stream_ports'].items():
    if stream_name in props['inbound_streams']:
      _logger.debug('%s is an inbound stream', stream_name)
      stream_dir = 'INBOUND'
    elif stream_name in props['outbound_streams']:
      _logger.debug('%s is an outbound stream', stream_name)
      stream_dir = 'OUTBOUND'
    else:
      stream_dir = 'OUTBOUND'
      _logger.error('direction of stream %s is unknown', stream_name)
      exit(1)

    for port in _port_wire_map.keys():
      # for passing streams, the port may have suffix _q\d+
      port_sanitize = port
      match = re.search('(.+)_q\d+$', port)
      if match:
        port_sanitize = match.group(1)
        _logger.debug('port name is sanitized from %s to %s', port, port_sanitize)

      port_width = props['port_width_map'].get(port_sanitize, '')
      if '_din' in port_sanitize or '_dout' in port_sanitize:
        assert port_width

      # the direction of the ports are determined by if the FIFO is inside
      # or outside the wrapper
      if port_sanitize.endswith(('_din', '_write', '_full_n')):
        if stream_dir == 'OUTBOUND':
          if port_sanitize.endswith(('_din', '_write')):
            direction = 'output'
          else:
            direction = 'input'
        else:
          if port_sanitize.endswith(('_din', '_write')):
            direction = 'input'
          else:
            direction = 'output'

      elif port_sanitize.endswith(('_dout', '_read', '_empty_n')):
        if stream_dir == 'OUTBOUND':
          if port_sanitize.endswith(('_dout', '_empty_n')):
            direction = 'output'
          else:
            direction = 'input'
        else:
          if port_sanitize.endswith(('_dout', '_empty_n')):
            direction = 'input'
          else:
            direction = 'output'
      else:
        assert False

      props['io_dir_to_name_to_width'][direction][port] = port_width


def add_passing_stream_io_dir(props: Dict) -> None:
  port_wire_map = props['port_wire_map']
  passing_streams = port_wire_map.get('passing_streams', {})
  if not passing_streams:
    _logger.debug('no passing streams found for vertex %s', props['instance'])

  for stream_name, stream_props in passing_streams.items():
    s_in = stream_props['inbound_side_suffix']
    s_out = stream_props['outbound_side_suffix']
    for wire_name, width in stream_props['wire_to_width'].items():
      if wire_name.endswith(('_din', '_write')):
        props['io_dir_to_name_to_width']['input'][f'{wire_name}_{s_in}'] = width
        props['io_dir_to_name_to_width']['output'][f'{wire_name}_{s_out}'] = width
      elif wire_name.endswith('_full_n'):
        props['io_dir_to_name_to_width']['output'][f'{wire_name}_{s_in}'] = width
        props['io_dir_to_name_to_width']['input'][f'{wire_name}_{s_out}'] = width
      else:
        assert False


def add_slave_ctrl_signals_io_dir(props: Dict) -> None:
  props['io_dir_to_name_to_width']['input']['ap_start'] = ''
  props['io_dir_to_name_to_width']['output']['ap_done'] = ''
  props['io_dir_to_name_to_width']['output']['ap_idle'] = ''
  props['io_dir_to_name_to_width']['output']['ap_ready'] = ''


def add_basic_io_dir(props: Dict) -> None:
  props['io_dir_to_name_to_width']['input']['ap_clk'] = ''
  props['io_dir_to_name_to_width']['input']['ap_rst_n'] = ''


def add_master_ctrl_signals_io_dir(props: Dict) -> None:
  port_wire_map = props['port_wire_map']

  for ap_out in port_wire_map['ctrl_out']:
    props['io_dir_to_name_to_width']['output'][ap_out] = ''
  for ap_out in port_wire_map['reset_out']:
    props['io_dir_to_name_to_width']['output'][ap_out] = ''
  for ap_in in port_wire_map['ctrl_in']:
    props['io_dir_to_name_to_width']['input'][ap_in] = ''


def add_constant_output_io_dir(props: Dict) -> List[str]:
  port_wire_map = props['port_wire_map']
  for c_out in port_wire_map['constant_out'].keys():
    width = props['port_width_map'][c_out]
    props['io_dir_to_name_to_width']['output'][c_out] = width


def add_s_axi_lite_io_dir(props: Dict) -> List[str]:
  port_wire_map = props['port_wire_map']

  for axi_entry in port_wire_map['axi_ports']:
    if axi_entry['axi_type'] == 'S_AXI_LITE':
      for portname, dir_and_width in S_AXI_LITE_INTERFACE.items():
        io_dir = dir_and_width[0]
        width = dir_and_width[1]
        props['io_dir_to_name_to_width'][io_dir][f's_axi_control_{portname}'] = width


def generate_no_ctrl_vertex_io_list(props: Dict) -> None:
  """For vertex that does not include the ctrl unit"""
  props['io_dir_to_name_to_width'] = {
    'input': {},
    'output': {},
  }

  add_basic_io_dir(props)
  add_stream_io_dir(props)
  add_m_axi_io_dir(props)
  add_passing_stream_io_dir(props)

  add_constant_input_io_dir(props)
  add_slave_ctrl_signals_io_dir(props)


def generate_ctrl_vertex_io_list(props: Dict) -> None:
  """For vertex that includes the ctrl unit"""
  props['io_dir_to_name_to_width'] = {
    'input': {},
    'output': {},
  }

  add_basic_io_dir(props)
  add_stream_io_dir(props)
  add_m_axi_io_dir(props)
  add_passing_stream_io_dir(props)

  add_constant_output_io_dir(props)
  add_master_ctrl_signals_io_dir(props)
  add_s_axi_lite_io_dir(props)
