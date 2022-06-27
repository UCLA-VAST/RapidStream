
STREAM_TYPES = (
  'fifo',
  'relay_station',
)

CTRL_SIGNALS = (
  'ap_clk',
  'ap_rst_n',
  'ap_start',
  'ap_done',
  'ap_idle',
  'ap_ready',
  'ap_local_deadlock',
)

PEEK_PORT_SUFFIX = (
  '_peek_read',
  '_peek_dout',
  '_peek_empty_n',
)

INBOUND_STREAM_PORTS = (
  'if_din',
  'if_full_n',
  'if_write',
)
OUTBOUND_STREAM_PORTS = (
  'if_dout',
  'if_empty_n',
  'if_read',
)
OTHER_STREAM_PORTS = (
  'clk',
  'reset',
  'if_read_ce',
  'if_write_ce',
)
STREAM_SUFFIX = (
  '_din',
  '_full_n',
  '_write',
  '_dout',
  '_empty_n',
  '_read',
)

C_S_AXI_DATA_WIDTH = 32
C_S_AXI_ADDR_WIDTH = 16

S_AXI_LITE_INTERFACE = {
  'AWADDR':  ('input', f'[{C_S_AXI_ADDR_WIDTH}-1:0]  '),
  'AWVALID': ('input', f'                          '),
  'AWREADY': ('output', f'                          '),
  'WDATA':   ('input', f'[{C_S_AXI_DATA_WIDTH}-1:0]  '),
  'WSTRB':   ('input', f'[{C_S_AXI_DATA_WIDTH}/8-1:0]'),
  'WVALID':  ('input', f'                          '),
  'WREADY':  ('output', f'                          '),
  'BRESP':   ('output', f'[1:0]                     '),
  'BVALID':  ('output', f'                          '),
  'BREADY':  ('input', f'                          '),
  'ARADDR':  ('input', f'[{C_S_AXI_ADDR_WIDTH}-1:0]  '),
  'ARVALID': ('input', f'                          '),
  'ARREADY': ('output', f'                          '),
  'RDATA':   ('output', f'[{C_S_AXI_DATA_WIDTH}-1:0]  '),
  'RRESP':   ('output', f'[1:0]                     '),
  'RVALID':  ('output', f'                          '),
  'RREADY':  ('input', f'                          '),
}

S_AXI_LITE_BASIC = (
  'ACLK',
  'ARESET',
  'ACLK_EN',
  'interrupt',
)

RESOURCE_TYPES = (
  'BRAM',
  'DSP',
  'FF',
  'LUT',
  'URAM',
)

M_AXI_INTERFACE = {
  "ARADDR"  : ("output", "[63:0]        "),
  "ARBURST" : ("output", "[1:0]         "),
  "ARCACHE" : ("output", "[3:0]         "),
  "ARID"    : ("output", "[0:0]         "),
  "ARLEN"   : ("output", "[7:0]         "),
  "ARLOCK"  : ("output", "              "),
  "ARPROT"  : ("output", "[2:0]         "),
  "ARQOS"   : ("output", "[3:0]         "),
  "ARREADY" : ("input", "              "),
  "ARSIZE"  : ("output", "[2:0]         "),
  "ARVALID" : ("output", "              "),
  "AWADDR"  : ("output", "[63:0]        "),
  "AWBURST" : ("output", "[1:0]         "),
  "AWCACHE" : ("output", "[3:0]         "),
  "AWID"    : ("output", "[0:0]         "),
  "AWLEN"   : ("output", "[7:0]         "),
  "AWLOCK"  : ("output", "              "),
  "AWPROT"  : ("output", "[2:0]         "),
  "AWQOS"   : ("output", "[3:0]         "),
  "AWREADY" : ("input", "              "),
  "AWSIZE"  : ("output", "[2:0]         "),
  "AWVALID" : ("output", "              "),
  "BID"     : ("input", "[0:0]         "),
  "BREADY"  : ("output", "              "),
  "BRESP"   : ("input", "[1:0]         "),
  "BVALID"  : ("input", "              "),
  "RDATA"   : ("input", "{data_width}  "),
  "RID"     : ("input", "[0:0]         "),
  "RLAST"   : ("input", "              "),
  "RREADY"  : ("output", "              "),
  "RRESP"   : ("input", "[1:0]         "),
  "RVALID"  : ("input", "              "),
  "WDATA"   : ("output", "{data_width}  "),
  "WLAST"   : ("output", "              "),
  "WREADY"  : ("input", "              "),
  "WSTRB"   : ("output", "[3:0]         "),
  "WVALID"  : ("output", "              "),
}


def get_axi_io_section(data_width: str, axi_port_name: str):
  """The data_width is in the format of f'[{width-1}:0]' """
  io = []
  for suffix, props in M_AXI_INTERFACE.items():
    direction = props[0]
    width = props[1].format(data_width=data_width)
    portname = f'm_axi_{axi_port_name}_{suffix}'

    io.append(f'{direction} {width} {portname},')

  return io
