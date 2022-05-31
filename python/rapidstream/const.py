
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

S_AXI_LITE_SUFFIX = (
  'AWVALID',
  'AWREADY',
  'AWADDR',
  'WVALID',
  'WREADY',
  'WDATA',
  'WSTRB',
  'ARVALID',
  'ARREADY',
  'ARADDR',
  'RVALID',
  'RREADY',
  'RDATA',
  'RRESP',
  'BVALID',
  'BREADY',
  'BRESP',
)

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
