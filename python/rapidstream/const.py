
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

def get_axi_io_section(data_width: str):
  """The data_width is in the format of f'[{width-1}:0]' """
  AXI_IO = f'''output [63:0] m_axi_a_ARADDR,
output [1:0] m_axi_a_ARBURST,
output [3:0] m_axi_a_ARCACHE,
output [0:0] m_axi_a_ARID,
output [7:0] m_axi_a_ARLEN,
output m_axi_a_ARLOCK,
output [2:0] m_axi_a_ARPROT,
output [3:0] m_axi_a_ARQOS,
input m_axi_a_ARREADY,
output [2:0] m_axi_a_ARSIZE,
output m_axi_a_ARVALID,
output [63:0] m_axi_a_AWADDR,
output [1:0] m_axi_a_AWBURST,
output [3:0] m_axi_a_AWCACHE,
output [0:0] m_axi_a_AWID,
output [7:0] m_axi_a_AWLEN,
output m_axi_a_AWLOCK,
output [2:0] m_axi_a_AWPROT,
output [3:0] m_axi_a_AWQOS,
input m_axi_a_AWREADY,
output [2:0] m_axi_a_AWSIZE,
output m_axi_a_AWVALID,
input [0:0] m_axi_a_BID,
output m_axi_a_BREADY,
input [1:0] m_axi_a_BRESP,
input m_axi_a_BVALID,
input {data_width} m_axi_a_RDATA,
input [0:0] m_axi_a_RID,
input m_axi_a_RLAST,
output m_axi_a_RREADY,
input {data_width} m_axi_a_RRESP,
input m_axi_a_RVALID,
output [31:0] m_axi_a_WDATA,
output m_axi_a_WLAST,
input m_axi_a_WREADY,
output [3:0] m_axi_a_WSTRB,
output m_axi_a_WVALID,'''
  return AXI_IO.split('\n')
