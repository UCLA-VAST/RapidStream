import logging
from typing import Dict, List

_logger = logging.getLogger().getChild(__name__)

# each node should have the following property
# RTL
# port / wire mapping
# members

# when we create a new upper level instance
# the new instance will have direct wire connection with other instances
# because we have pushed some streams into the instance
# in this case, we should create new virtual edges and give them a speical type
# basically the three wires connecting to a stream inside the upper instance will form such a virtual edge
# we need to recode the pipline level for such a special stream
# we need to replace the innner stream by almost full FIFOs (not relay station)
# and the grace period of the almost-full FIFO should match the external pipeline level


INBOUND_PORTS = (
  'if_din',
  'if_full_n',
  'if_write',
)
OUTBOUND_PORTS = (
  'if_dout',
  'if_empty_n',
  'if_read',
)


def get_updated_decl(
  config: Dict,
  inbound_external_streams: List[str],
  outbound_external_streams: List[str],
):
  """Get the updated external wire decl, internal wire decl
     and the new partition pins on the wrapper
     TODO: add partition pins for ctrl signals
     TODO: add partition pins if any instance has top-level IO
  """
  io_decl = {}
  external_wire_decl = {}
  internal_wire_decl = {}

  def _update_decl(stream, port):
    wire_name = config['edges'][stream]['port_wire_map'][port]
    width = config['wire_decl'][wire_name]

    io_decl[f'{wire_name}_PARTITION_PIN'] = width
    external_wire_decl[f'{wire_name}_EXTERNAL'] = width
    internal_wire_decl[f'{wire_name}_INTERNAL'] = width

  for stream in inbound_external_streams:
    for port in INBOUND_PORTS:
      _update_decl(stream, port)

  for stream in outbound_external_streams:
    for port in OUTBOUND_PORTS:
      _update_decl(stream, port)

  return io_decl, external_wire_decl, internal_wire_decl


def get_internal_wires():
  """Get the wires between instances included into the wrapper"""

def update_external_wires():
  """Remove the wires included into the wrapper from the external wire list"""

def get_internal_instances():
  """Get the task/stream instances included into the wrapper"""

def update_external_instances():
  """Remove the task/stream instances included into the wrapper from the external list
     Add the newly created instance
  """


def create_wrapper(
  config: Dict,
  target_vertices: List[str],
  wrapper_name: str,
):
  """Create an upper node that includes the specified nodes"""

  # get all internal streams

  # get all internal wires and external wires

  # generate the ctrl signal inside the wrapper
