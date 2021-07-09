

`timescale 1 ns / 1 ps
module CR_X4Y4_To_CR_X5Y5 (
  PE_wrapper190_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_4_4_V_V_full_n,
  PE_wrapper190_U0_fifo_cin_out_V_V_write,
  PE_wrapper201_U0_fifo_w_out_V_V_din,
  fifo_w_PE_4_4_V_V_full_n,
  PE_wrapper201_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_full_n,
  cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper213_U0_fifo_w_out_V_V_din,
  fifo_w_PE_5_4_V_V_full_n,
  PE_wrapper213_U0_fifo_w_out_V_V_write,
  PE_wrapper214_U0_fifo_w_out_V_V_din,
  fifo_w_PE_5_5_V_V_full_n,
  PE_wrapper214_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n,
  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write,
  w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_din,
  fifo_w_w_IO_L3_in_serialize_V_V_full_n,
  w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_write,
  PE_wrapper214_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_6_4_V_V_full_n,
  PE_wrapper214_U0_fifo_cin_out_V_V_write,
  PE_wrapper202_U0_fifo_w_out_V_V_din,
  fifo_w_PE_4_5_V_V_full_n,
  PE_wrapper202_U0_fifo_w_out_V_V_write,
  PE_wrapper202_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_4_4_V_full_n,
  PE_wrapper202_U0_fifo_cout_drain_out_V_write,
  kernel0_entry12_U0_w_V_out_din,
  w_V_c_full_n,
  kernel0_entry12_U0_w_V_out_write,
  m_axi_gmem_w_AWVALID,
  m_axi_gmem_w_AWREADY,
  m_axi_gmem_w_AWADDR,
  m_axi_gmem_w_AWID,
  m_axi_gmem_w_AWLEN,
  m_axi_gmem_w_AWSIZE,
  m_axi_gmem_w_AWBURST,
  m_axi_gmem_w_AWLOCK,
  m_axi_gmem_w_AWCACHE,
  m_axi_gmem_w_AWPROT,
  m_axi_gmem_w_AWQOS,
  m_axi_gmem_w_AWREGION,
  m_axi_gmem_w_AWUSER,
  m_axi_gmem_w_WVALID,
  m_axi_gmem_w_WREADY,
  m_axi_gmem_w_WDATA,
  m_axi_gmem_w_WSTRB,
  m_axi_gmem_w_WLAST,
  m_axi_gmem_w_WID,
  m_axi_gmem_w_WUSER,
  m_axi_gmem_w_ARVALID,
  m_axi_gmem_w_ARREADY,
  m_axi_gmem_w_ARADDR,
  m_axi_gmem_w_ARID,
  m_axi_gmem_w_ARLEN,
  m_axi_gmem_w_ARSIZE,
  m_axi_gmem_w_ARBURST,
  m_axi_gmem_w_ARLOCK,
  m_axi_gmem_w_ARCACHE,
  m_axi_gmem_w_ARPROT,
  m_axi_gmem_w_ARQOS,
  m_axi_gmem_w_ARREGION,
  m_axi_gmem_w_ARUSER,
  m_axi_gmem_w_RVALID,
  m_axi_gmem_w_RREADY,
  m_axi_gmem_w_RDATA,
  m_axi_gmem_w_RLAST,
  m_axi_gmem_w_RID,
  m_axi_gmem_w_RUSER,
  m_axi_gmem_w_RRESP,
  m_axi_gmem_w_BVALID,
  m_axi_gmem_w_BREADY,
  m_axi_gmem_w_BRESP,
  m_axi_gmem_w_BID,
  m_axi_gmem_w_BUSER,
  ap_start,
  ap_done,
  ap_idle,
  ap_ready,
  ap_continue,
  ap_clk,
  ap_rst_n
);
parameter C_S_AXI_CONTROL_DATA_WIDTH = 32;
parameter C_S_AXI_CONTROL_ADDR_WIDTH = 6;
parameter C_S_AXI_DATA_WIDTH = 32;
parameter C_S_AXI_ADDR_WIDTH = 32;
parameter C_M_AXI_GMEM_CIN_ID_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_ADDR_WIDTH = 64;
parameter C_M_AXI_GMEM_CIN_DATA_WIDTH = 512;
parameter C_M_AXI_GMEM_CIN_AWUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_ARUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_WUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_RUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_BUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_CIN_USER_VALUE = 0;
parameter C_M_AXI_GMEM_CIN_PROT_VALUE = 0;
parameter C_M_AXI_GMEM_CIN_CACHE_VALUE = 3;
parameter C_M_AXI_ID_WIDTH = 1;
parameter C_M_AXI_ADDR_WIDTH = 64;
parameter C_M_AXI_DATA_WIDTH = 32;
parameter C_M_AXI_AWUSER_WIDTH = 1;
parameter C_M_AXI_ARUSER_WIDTH = 1;
parameter C_M_AXI_WUSER_WIDTH = 1;
parameter C_M_AXI_RUSER_WIDTH = 1;
parameter C_M_AXI_BUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_ID_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_ADDR_WIDTH = 64;
parameter C_M_AXI_GMEM_COUT_DATA_WIDTH = 512;
parameter C_M_AXI_GMEM_COUT_AWUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_ARUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_WUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_RUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_BUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_COUT_USER_VALUE = 0;
parameter C_M_AXI_GMEM_COUT_PROT_VALUE = 0;
parameter C_M_AXI_GMEM_COUT_CACHE_VALUE = 3;
parameter C_M_AXI_GMEM_W_ID_WIDTH = 1;
parameter C_M_AXI_GMEM_W_ADDR_WIDTH = 64;
parameter C_M_AXI_GMEM_W_DATA_WIDTH = 512;
parameter C_M_AXI_GMEM_W_AWUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_W_ARUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_W_WUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_W_RUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_W_BUSER_WIDTH = 1;
parameter C_M_AXI_GMEM_W_USER_VALUE = 0;
parameter C_M_AXI_GMEM_W_PROT_VALUE = 0;
parameter C_M_AXI_GMEM_W_CACHE_VALUE = 3;
parameter C_S_AXI_CONTROL_WSTRB_WIDTH = 32 / 8;
parameter C_S_AXI_WSTRB_WIDTH = 32 / 8;
parameter C_M_AXI_GMEM_CIN_WSTRB_WIDTH = 512 / 8;
parameter C_M_AXI_WSTRB_WIDTH = 32 / 8;
parameter C_M_AXI_GMEM_COUT_WSTRB_WIDTH = 512 / 8;
parameter C_M_AXI_GMEM_W_WSTRB_WIDTH = 512 / 8;
reg ap_rst_n_inv;
wire gmem_w_AWREADY;
wire gmem_w_WREADY;
wire gmem_w_ARREADY;
wire gmem_w_RVALID;
wire [511:0] gmem_w_RDATA;
wire gmem_w_RLAST;
wire [0:0] gmem_w_RID;
wire [0:0] gmem_w_RUSER;
wire [1:0] gmem_w_RRESP;
wire gmem_w_BVALID;
wire [1:0] gmem_w_BRESP;
wire [0:0] gmem_w_BID;
wire [0:0] gmem_w_BUSER;
wire w_IO_L3_in_serialize_U0_ap_start;
wire w_IO_L3_in_serialize_U0_ap_done;
wire w_IO_L3_in_serialize_U0_ap_continue;
wire w_IO_L3_in_serialize_U0_ap_idle;
wire w_IO_L3_in_serialize_U0_ap_ready;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_AWVALID;
wire [63:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWADDR;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWID;
wire [31:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWLEN;
wire [2:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWSIZE;
wire [1:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWBURST;
wire [1:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWLOCK;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWCACHE;
wire [2:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWPROT;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWQOS;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWREGION;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_AWUSER;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_WVALID;
wire [511:0] w_IO_L3_in_serialize_U0_m_axi_w_V_WDATA;
wire [63:0] w_IO_L3_in_serialize_U0_m_axi_w_V_WSTRB;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_WLAST;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_WID;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_WUSER;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_ARVALID;
wire [63:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARADDR;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARID;
wire [31:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARLEN;
wire [2:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARSIZE;
wire [1:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARBURST;
wire [1:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARLOCK;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARCACHE;
wire [2:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARPROT;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARQOS;
wire [3:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARREGION;
wire [0:0] w_IO_L3_in_serialize_U0_m_axi_w_V_ARUSER;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_RREADY;
wire w_IO_L3_in_serialize_U0_m_axi_w_V_BREADY;
wire w_IO_L3_in_serialize_U0_w_V_offset_read;
wire PE_wrapper202_U0_ap_start;
wire PE_wrapper202_U0_ap_done;
wire PE_wrapper202_U0_ap_continue;
wire PE_wrapper202_U0_ap_idle;
wire PE_wrapper202_U0_ap_ready;
wire PE_wrapper202_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper202_U0_fifo_cin_out_V_V_din;
wire PE_wrapper202_U0_fifo_cin_out_V_V_write;
wire PE_wrapper202_U0_fifo_w_in_V_V_read;
wire PE_wrapper214_U0_ap_start;
wire PE_wrapper214_U0_ap_done;
wire PE_wrapper214_U0_ap_continue;
wire PE_wrapper214_U0_ap_idle;
wire PE_wrapper214_U0_ap_ready;
wire PE_wrapper214_U0_fifo_cin_in_V_V_read;
wire [31:0] PE_wrapper214_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper214_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper214_U0_fifo_w_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper441_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper441_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper441_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper441_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper441_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_local_in_V_read;
wire [63:0] w_V_c_dout;
wire w_V_c_empty_n;
wire [255:0] fifo_cin_PE_4_4_V_V_dout;
wire fifo_cin_PE_4_4_V_V_empty_n;
wire [255:0] fifo_w_PE_4_4_V_V_dout;
wire fifo_w_PE_4_4_V_V_empty_n;
wire fifo_cin_PE_5_4_V_V_full_n;
wire [255:0] fifo_cin_PE_5_4_V_V_dout;
wire fifo_cin_PE_5_4_V_V_empty_n;
wire [255:0] fifo_w_PE_5_4_V_V_dout;
wire fifo_w_PE_5_4_V_V_empty_n;
wire fifo_cout_drain_PE_5_4_V_full_n;
wire [31:0] fifo_cout_drain_PE_5_4_V_dout;
wire fifo_cout_drain_PE_5_4_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_empty_n;
// pipeline ap_start
(* shreg_extract = "no" *) reg ap_start_p1;
(* shreg_extract = "no" *) reg ap_start_p2;
(* shreg_extract = "no" *) reg ap_start_pipe;
// pipeline ap_rst_n
(* shreg_extract = "no" *) reg ap_rst_p1;
(* shreg_extract = "no" *) reg ap_rst_p2;
(* shreg_extract = "no" *) reg ap_rst_pipe;
(* shreg_extract = "no" *) reg ap_rst_n_p1;
(* shreg_extract = "no" *) reg ap_rst_n_p2;
(* shreg_extract = "no" *) reg ap_rst_n_pipe;
input [255:0] PE_wrapper190_U0_fifo_cin_out_V_V_din;
output  fifo_cin_PE_4_4_V_V_full_n;
input  PE_wrapper190_U0_fifo_cin_out_V_V_write;
input [255:0] PE_wrapper201_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_4_4_V_V_full_n;
input  PE_wrapper201_U0_fifo_w_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_write;
input [255:0] PE_wrapper213_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_5_4_V_V_full_n;
input  PE_wrapper213_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper214_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_5_5_V_V_full_n;
output  PE_wrapper214_U0_fifo_w_out_V_V_write;
output [63:0] cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n;
output  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write;
output [255:0] w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_din;
input  fifo_w_w_IO_L3_in_serialize_V_V_full_n;
output  w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_write;
output [255:0] PE_wrapper214_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_6_4_V_V_full_n;
output  PE_wrapper214_U0_fifo_cin_out_V_V_write;
output [255:0] PE_wrapper202_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_4_5_V_V_full_n;
output  PE_wrapper202_U0_fifo_w_out_V_V_write;
output [31:0] PE_wrapper202_U0_fifo_cout_drain_out_V_din;
input  fifo_cout_drain_PE_4_4_V_full_n;
output  PE_wrapper202_U0_fifo_cout_drain_out_V_write;
input [63:0] kernel0_entry12_U0_w_V_out_din;
output  w_V_c_full_n;
input  kernel0_entry12_U0_w_V_out_write;
output  m_axi_gmem_w_AWVALID;
input  m_axi_gmem_w_AWREADY;
output [64-1:0] m_axi_gmem_w_AWADDR;
output [1-1:0] m_axi_gmem_w_AWID;
output [7:0] m_axi_gmem_w_AWLEN;
output [2:0] m_axi_gmem_w_AWSIZE;
output [1:0] m_axi_gmem_w_AWBURST;
output [1:0] m_axi_gmem_w_AWLOCK;
output [3:0] m_axi_gmem_w_AWCACHE;
output [2:0] m_axi_gmem_w_AWPROT;
output [3:0] m_axi_gmem_w_AWQOS;
output [3:0] m_axi_gmem_w_AWREGION;
output [1-1:0] m_axi_gmem_w_AWUSER;
output  m_axi_gmem_w_WVALID;
input  m_axi_gmem_w_WREADY;
output [512-1:0] m_axi_gmem_w_WDATA;
output [512/8-1:0] m_axi_gmem_w_WSTRB;
output  m_axi_gmem_w_WLAST;
output [1-1:0] m_axi_gmem_w_WID;
output [1-1:0] m_axi_gmem_w_WUSER;
output  m_axi_gmem_w_ARVALID;
input  m_axi_gmem_w_ARREADY;
output [64-1:0] m_axi_gmem_w_ARADDR;
output [1-1:0] m_axi_gmem_w_ARID;
output [7:0] m_axi_gmem_w_ARLEN;
output [2:0] m_axi_gmem_w_ARSIZE;
output [1:0] m_axi_gmem_w_ARBURST;
output [1:0] m_axi_gmem_w_ARLOCK;
output [3:0] m_axi_gmem_w_ARCACHE;
output [2:0] m_axi_gmem_w_ARPROT;
output [3:0] m_axi_gmem_w_ARQOS;
output [3:0] m_axi_gmem_w_ARREGION;
output [1-1:0] m_axi_gmem_w_ARUSER;
input  m_axi_gmem_w_RVALID;
output  m_axi_gmem_w_RREADY;
input [512-1:0] m_axi_gmem_w_RDATA;
input  m_axi_gmem_w_RLAST;
input [1-1:0] m_axi_gmem_w_RID;
input [1-1:0] m_axi_gmem_w_RUSER;
input [1:0] m_axi_gmem_w_RRESP;
input  m_axi_gmem_w_BVALID;
output  m_axi_gmem_w_BREADY;
input [1:0] m_axi_gmem_w_BRESP;
input [1-1:0] m_axi_gmem_w_BID;
input [1-1:0] m_axi_gmem_w_BUSER;
input  ap_start;
output ap_done;
output ap_idle;
output ap_ready;
input  ap_continue;
input ap_clk;
input ap_rst_n;
(* keep_hierarchy = "yes" *)
kernel0_kernel0_gmem_w_m_axi
#(
  .CONSERVATIVE(1),
  .USER_DW(512),
  .USER_AW(64),
  .USER_MAXREQS(5),
  .NUM_READ_OUTSTANDING(16),
  .NUM_WRITE_OUTSTANDING(16),
  .MAX_READ_BURST_LENGTH(16),
  .MAX_WRITE_BURST_LENGTH(16),
  .C_M_AXI_ID_WIDTH(C_M_AXI_GMEM_W_ID_WIDTH),
  .C_M_AXI_ADDR_WIDTH(C_M_AXI_GMEM_W_ADDR_WIDTH),
  .C_M_AXI_DATA_WIDTH(C_M_AXI_GMEM_W_DATA_WIDTH),
  .C_M_AXI_AWUSER_WIDTH(C_M_AXI_GMEM_W_AWUSER_WIDTH),
  .C_M_AXI_ARUSER_WIDTH(C_M_AXI_GMEM_W_ARUSER_WIDTH),
  .C_M_AXI_WUSER_WIDTH(C_M_AXI_GMEM_W_WUSER_WIDTH),
  .C_M_AXI_RUSER_WIDTH(C_M_AXI_GMEM_W_RUSER_WIDTH),
  .C_M_AXI_BUSER_WIDTH(C_M_AXI_GMEM_W_BUSER_WIDTH),
  .C_USER_VALUE(C_M_AXI_GMEM_W_USER_VALUE),
  .C_PROT_VALUE(C_M_AXI_GMEM_W_PROT_VALUE),
  .C_CACHE_VALUE(C_M_AXI_GMEM_W_CACHE_VALUE)
)
kernel0_gmem_w_m_axi_U
(
  .AWVALID(m_axi_gmem_w_AWVALID),
  .AWREADY(m_axi_gmem_w_AWREADY),
  .AWADDR(m_axi_gmem_w_AWADDR),
  .AWID(m_axi_gmem_w_AWID),
  .AWLEN(m_axi_gmem_w_AWLEN),
  .AWSIZE(m_axi_gmem_w_AWSIZE),
  .AWBURST(m_axi_gmem_w_AWBURST),
  .AWLOCK(m_axi_gmem_w_AWLOCK),
  .AWCACHE(m_axi_gmem_w_AWCACHE),
  .AWPROT(m_axi_gmem_w_AWPROT),
  .AWQOS(m_axi_gmem_w_AWQOS),
  .AWREGION(m_axi_gmem_w_AWREGION),
  .AWUSER(m_axi_gmem_w_AWUSER),
  .WVALID(m_axi_gmem_w_WVALID),
  .WREADY(m_axi_gmem_w_WREADY),
  .WDATA(m_axi_gmem_w_WDATA),
  .WSTRB(m_axi_gmem_w_WSTRB),
  .WLAST(m_axi_gmem_w_WLAST),
  .WID(m_axi_gmem_w_WID),
  .WUSER(m_axi_gmem_w_WUSER),
  .ARVALID(m_axi_gmem_w_ARVALID),
  .ARREADY(m_axi_gmem_w_ARREADY),
  .ARADDR(m_axi_gmem_w_ARADDR),
  .ARID(m_axi_gmem_w_ARID),
  .ARLEN(m_axi_gmem_w_ARLEN),
  .ARSIZE(m_axi_gmem_w_ARSIZE),
  .ARBURST(m_axi_gmem_w_ARBURST),
  .ARLOCK(m_axi_gmem_w_ARLOCK),
  .ARCACHE(m_axi_gmem_w_ARCACHE),
  .ARPROT(m_axi_gmem_w_ARPROT),
  .ARQOS(m_axi_gmem_w_ARQOS),
  .ARREGION(m_axi_gmem_w_ARREGION),
  .ARUSER(m_axi_gmem_w_ARUSER),
  .RVALID(m_axi_gmem_w_RVALID),
  .RREADY(m_axi_gmem_w_RREADY),
  .RDATA(m_axi_gmem_w_RDATA),
  .RLAST(m_axi_gmem_w_RLAST),
  .RID(m_axi_gmem_w_RID),
  .RUSER(m_axi_gmem_w_RUSER),
  .RRESP(m_axi_gmem_w_RRESP),
  .BVALID(m_axi_gmem_w_BVALID),
  .BREADY(m_axi_gmem_w_BREADY),
  .BRESP(m_axi_gmem_w_BRESP),
  .BID(m_axi_gmem_w_BID),
  .BUSER(m_axi_gmem_w_BUSER),
  .ACLK(ap_clk),
  .ARESET(ap_rst_pipe),
  .ACLK_EN(1'b1),
  .I_ARVALID(w_IO_L3_in_serialize_U0_m_axi_w_V_ARVALID),
  .I_ARREADY(gmem_w_ARREADY),
  .I_ARADDR(w_IO_L3_in_serialize_U0_m_axi_w_V_ARADDR),
  .I_ARID(w_IO_L3_in_serialize_U0_m_axi_w_V_ARID),
  .I_ARLEN(w_IO_L3_in_serialize_U0_m_axi_w_V_ARLEN),
  .I_ARSIZE(w_IO_L3_in_serialize_U0_m_axi_w_V_ARSIZE),
  .I_ARLOCK(w_IO_L3_in_serialize_U0_m_axi_w_V_ARLOCK),
  .I_ARCACHE(w_IO_L3_in_serialize_U0_m_axi_w_V_ARCACHE),
  .I_ARQOS(w_IO_L3_in_serialize_U0_m_axi_w_V_ARQOS),
  .I_ARPROT(w_IO_L3_in_serialize_U0_m_axi_w_V_ARPROT),
  .I_ARUSER(w_IO_L3_in_serialize_U0_m_axi_w_V_ARUSER),
  .I_ARBURST(w_IO_L3_in_serialize_U0_m_axi_w_V_ARBURST),
  .I_ARREGION(w_IO_L3_in_serialize_U0_m_axi_w_V_ARREGION),
  .I_RVALID(gmem_w_RVALID),
  .I_RREADY(w_IO_L3_in_serialize_U0_m_axi_w_V_RREADY),
  .I_RDATA(gmem_w_RDATA),
  .I_RID(gmem_w_RID),
  .I_RUSER(gmem_w_RUSER),
  .I_RRESP(gmem_w_RRESP),
  .I_RLAST(gmem_w_RLAST),
  .I_AWVALID(1'b0),
  .I_AWREADY(gmem_w_AWREADY),
  .I_AWADDR(64'd0),
  .I_AWID(1'd0),
  .I_AWLEN(32'd0),
  .I_AWSIZE(3'd0),
  .I_AWLOCK(2'd0),
  .I_AWCACHE(4'd0),
  .I_AWQOS(4'd0),
  .I_AWPROT(3'd0),
  .I_AWUSER(1'd0),
  .I_AWBURST(2'd0),
  .I_AWREGION(4'd0),
  .I_WVALID(1'b0),
  .I_WREADY(gmem_w_WREADY),
  .I_WDATA(512'd0),
  .I_WID(1'd0),
  .I_WUSER(1'd0),
  .I_WLAST(1'b0),
  .I_WSTRB(64'd0),
  .I_BVALID(gmem_w_BVALID),
  .I_BREADY(1'b0),
  .I_BRESP(gmem_w_BRESP),
  .I_BID(gmem_w_BID),
  .I_BUSER(gmem_w_BUSER)
);

(* keep_hierarchy = "yes" *)
kernel0_w_IO_L3_in_serialize
w_IO_L3_in_serialize_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(w_IO_L3_in_serialize_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(w_IO_L3_in_serialize_U0_ap_idle),
  .ap_ready(w_IO_L3_in_serialize_U0_ap_ready),
  .m_axi_w_V_AWVALID(w_IO_L3_in_serialize_U0_m_axi_w_V_AWVALID),
  .m_axi_w_V_AWREADY(1'b0),
  .m_axi_w_V_AWADDR(w_IO_L3_in_serialize_U0_m_axi_w_V_AWADDR),
  .m_axi_w_V_AWID(w_IO_L3_in_serialize_U0_m_axi_w_V_AWID),
  .m_axi_w_V_AWLEN(w_IO_L3_in_serialize_U0_m_axi_w_V_AWLEN),
  .m_axi_w_V_AWSIZE(w_IO_L3_in_serialize_U0_m_axi_w_V_AWSIZE),
  .m_axi_w_V_AWBURST(w_IO_L3_in_serialize_U0_m_axi_w_V_AWBURST),
  .m_axi_w_V_AWLOCK(w_IO_L3_in_serialize_U0_m_axi_w_V_AWLOCK),
  .m_axi_w_V_AWCACHE(w_IO_L3_in_serialize_U0_m_axi_w_V_AWCACHE),
  .m_axi_w_V_AWPROT(w_IO_L3_in_serialize_U0_m_axi_w_V_AWPROT),
  .m_axi_w_V_AWQOS(w_IO_L3_in_serialize_U0_m_axi_w_V_AWQOS),
  .m_axi_w_V_AWREGION(w_IO_L3_in_serialize_U0_m_axi_w_V_AWREGION),
  .m_axi_w_V_AWUSER(w_IO_L3_in_serialize_U0_m_axi_w_V_AWUSER),
  .m_axi_w_V_WVALID(w_IO_L3_in_serialize_U0_m_axi_w_V_WVALID),
  .m_axi_w_V_WREADY(1'b0),
  .m_axi_w_V_WDATA(w_IO_L3_in_serialize_U0_m_axi_w_V_WDATA),
  .m_axi_w_V_WSTRB(w_IO_L3_in_serialize_U0_m_axi_w_V_WSTRB),
  .m_axi_w_V_WLAST(w_IO_L3_in_serialize_U0_m_axi_w_V_WLAST),
  .m_axi_w_V_WID(w_IO_L3_in_serialize_U0_m_axi_w_V_WID),
  .m_axi_w_V_WUSER(w_IO_L3_in_serialize_U0_m_axi_w_V_WUSER),
  .m_axi_w_V_ARVALID(w_IO_L3_in_serialize_U0_m_axi_w_V_ARVALID),
  .m_axi_w_V_ARREADY(gmem_w_ARREADY),
  .m_axi_w_V_ARADDR(w_IO_L3_in_serialize_U0_m_axi_w_V_ARADDR),
  .m_axi_w_V_ARID(w_IO_L3_in_serialize_U0_m_axi_w_V_ARID),
  .m_axi_w_V_ARLEN(w_IO_L3_in_serialize_U0_m_axi_w_V_ARLEN),
  .m_axi_w_V_ARSIZE(w_IO_L3_in_serialize_U0_m_axi_w_V_ARSIZE),
  .m_axi_w_V_ARBURST(w_IO_L3_in_serialize_U0_m_axi_w_V_ARBURST),
  .m_axi_w_V_ARLOCK(w_IO_L3_in_serialize_U0_m_axi_w_V_ARLOCK),
  .m_axi_w_V_ARCACHE(w_IO_L3_in_serialize_U0_m_axi_w_V_ARCACHE),
  .m_axi_w_V_ARPROT(w_IO_L3_in_serialize_U0_m_axi_w_V_ARPROT),
  .m_axi_w_V_ARQOS(w_IO_L3_in_serialize_U0_m_axi_w_V_ARQOS),
  .m_axi_w_V_ARREGION(w_IO_L3_in_serialize_U0_m_axi_w_V_ARREGION),
  .m_axi_w_V_ARUSER(w_IO_L3_in_serialize_U0_m_axi_w_V_ARUSER),
  .m_axi_w_V_RVALID(gmem_w_RVALID),
  .m_axi_w_V_RREADY(w_IO_L3_in_serialize_U0_m_axi_w_V_RREADY),
  .m_axi_w_V_RDATA(gmem_w_RDATA),
  .m_axi_w_V_RLAST(gmem_w_RLAST),
  .m_axi_w_V_RID(gmem_w_RID),
  .m_axi_w_V_RUSER(gmem_w_RUSER),
  .m_axi_w_V_RRESP(gmem_w_RRESP),
  .m_axi_w_V_BVALID(1'b0),
  .m_axi_w_V_BREADY(w_IO_L3_in_serialize_U0_m_axi_w_V_BREADY),
  .m_axi_w_V_BRESP(2'd0),
  .m_axi_w_V_BID(1'd0),
  .m_axi_w_V_BUSER(1'd0),
  .w_V_offset_dout(w_V_c_dout),
  .w_V_offset_empty_n(w_V_c_empty_n),
  .w_V_offset_read(w_IO_L3_in_serialize_U0_w_V_offset_read),
  .fifo_w_local_out_V_V_din(w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_din),
  .fifo_w_local_out_V_V_full_n(fifo_w_w_IO_L3_in_serialize_V_V_full_n),
  .fifo_w_local_out_V_V_write(w_IO_L3_in_serialize_U0_fifo_w_local_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper202
PE_wrapper202_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper202_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper202_U0_ap_idle),
  .ap_ready(PE_wrapper202_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_4_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_4_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper202_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper202_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_5_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper202_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper202_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_4_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper202_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_4_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_4_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper202_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper202_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_4_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper202_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper214
PE_wrapper214_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper214_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper214_U0_ap_idle),
  .ap_ready(PE_wrapper214_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_5_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_5_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper214_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper214_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_6_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper214_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper214_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_5_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper214_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_5_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_5_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper214_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper214_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_5_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper214_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper441
cout_drain_IO_L1_out_wrapper441_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper441_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper441_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper441_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_5_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_5_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(45),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_5_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper214_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_5_4_V_full_n),
  .if_write(PE_wrapper214_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_5_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_5_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_5_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper202_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_5_4_V_V_full_n),
  .if_write(PE_wrapper202_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_5_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_5_4_V_V_empty_n),
  .if_read(PE_wrapper214_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(6),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_cin_PE_4_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper190_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_4_4_V_V_full_n),
  .if_write(PE_wrapper190_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_4_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_4_4_V_V_empty_n),
  .if_read(PE_wrapper202_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(7),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_w_PE_4_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper201_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_4_4_V_V_full_n),
  .if_write(PE_wrapper201_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_4_4_V_V_dout),
  .if_empty_n(fifo_w_PE_4_4_V_V_empty_n),
  .if_read(PE_wrapper202_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(5),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(5)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper440_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_6_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(6),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(7)
)
fifo_w_PE_5_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper213_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_5_4_V_V_full_n),
  .if_write(PE_wrapper213_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_5_4_V_V_dout),
  .if_empty_n(fifo_w_PE_5_4_V_V_empty_n),
  .if_read(PE_wrapper214_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(5),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(5)
)
w_V_c_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(kernel0_entry12_U0_w_V_out_din),
  .if_full_n(w_V_c_full_n),
  .if_write(kernel0_entry12_U0_w_V_out_write),
  .if_dout(w_V_c_dout),
  .if_empty_n(w_V_c_empty_n),
  .if_read(w_IO_L3_in_serialize_U0_w_V_offset_read)
);

// pipeline ap_start
initial begin
  ap_start_p1 = 1'b0;
  ap_start_p2 = 1'b0;
  ap_start_pipe = 1'b0;
end
always @ (posedge ap_clk) begin
  ap_start_p1 <= ap_start;
  ap_start_p2 <= ap_start_p1;
  ap_start_pipe <= ap_start_p2;
end
assign ap_done = 1'b1;
assign ap_ready = ap_done;
assign ap_idle = ap_done;
// pipeline ap_start
initial begin
  ap_rst_p1 = 1'b0;
  ap_rst_p2 = 1'b0;
  ap_rst_pipe = 1'b0;
  ap_rst_n_p1 = 1'b0;
  ap_rst_n_p2 = 1'b0;
  ap_rst_n_pipe = 1'b0;
end
always @ (posedge ap_clk) begin
  ap_rst_p1 <= ~ap_rst_n;
  ap_rst_p2 <= ap_rst_p1;
  ap_rst_pipe <= ap_rst_p2;
  ap_rst_n_p1 <= ap_rst_n;
  ap_rst_n_p2 <= ap_rst_n_p1;
  ap_rst_n_pipe <= ap_rst_n_p2;
end
endmodule

// first-word fall-through (FWFT) FIFO
// if its capacity > THRESHOLD bits, it uses block RAM, otherwise it will uses
// shift register LUT
module fifo_almost_full #(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 5,
  parameter DEPTH      = 32,
  parameter THRESHOLD  = 18432,
  parameter GRACE_PERIOD = 2
) (
  input wire clk,
  input wire reset,
  // write
  output wire                  if_full_n,
  input  wire                  if_write_ce,
  input  wire                  if_write,
  input  wire [DATA_WIDTH-1:0] if_din,
  // read
  output wire                  if_empty_n,
  input  wire                  if_read_ce,
  input  wire                  if_read,
  output wire [DATA_WIDTH-1:0] if_dout
);
  parameter REAL_DEPTH = GRACE_PERIOD + DEPTH + 4;
  parameter REAL_ADDR_WIDTH  = $clog2(REAL_DEPTH);
generate
  if (DATA_WIDTH * DEPTH > THRESHOLD) begin : bram
    fifo_bram_almost_full #(
      .DATA_WIDTH(DATA_WIDTH),
      .ADDR_WIDTH(REAL_ADDR_WIDTH),
      .DEPTH     (REAL_DEPTH),
      .GRACE_PERIOD(GRACE_PERIOD) /*********/
    ) unit (
      .clk  (clk),
      .reset(reset),
      .if_full_n  (if_full_n),
      .if_write_ce(if_write_ce),
      .if_write   (if_write),
      .if_din     (if_din),
      .if_empty_n(if_empty_n),
      .if_read_ce(if_read_ce),
      .if_read   (if_read),
      .if_dout   (if_dout)
    );
  end else begin : srl
    fifo_srl_almost_full #(
      .DATA_WIDTH(DATA_WIDTH),
      .ADDR_WIDTH(REAL_ADDR_WIDTH),
      .DEPTH     (REAL_DEPTH),
      .GRACE_PERIOD(GRACE_PERIOD) /*********/
    ) unit (
      .clk  (clk),
      .reset(reset),
      .if_full_n  (if_full_n),
      .if_write_ce(if_write_ce),
      .if_write   (if_write),
      .if_din     (if_din),
      .if_empty_n(if_empty_n),
      .if_read_ce(if_read_ce),
      .if_read   (if_read),
      .if_dout   (if_dout)
    );
  end
endgenerate
endmodule  // fifo
/////////////////////////////////////////////////////////////////
module fifo_srl_almost_full (
    clk,
    reset,
    if_empty_n,
    if_read_ce,
    if_read,
    if_dout,
    if_full_n,
    if_write_ce,
    if_write,
    if_din);
parameter MEM_STYLE   = "shiftreg";
parameter DATA_WIDTH  = 32'd32;
parameter ADDR_WIDTH  = 32'd4;
parameter DEPTH       = 5'd16;
/*******************************************/
parameter GRACE_PERIOD = 2;
/*******************************************/
input clk;
input reset;
output if_empty_n;
input if_read_ce;
input if_read;
output[DATA_WIDTH - 1:0] if_dout;
output if_full_n;
input if_write_ce;
input if_write;
input[DATA_WIDTH - 1:0] if_din;
wire[ADDR_WIDTH - 1:0] shiftReg_addr ;
wire[DATA_WIDTH - 1:0] shiftReg_data, shiftReg_q;
wire                     shiftReg_ce;
reg[ADDR_WIDTH:0] mOutPtr = ~{(ADDR_WIDTH+1){1'b0}};
reg internal_empty_n = 0, internal_full_n = 1;
assign if_empty_n = internal_empty_n;
/*******************************************/
// assign if_full_n = internal_full_n;
wire almost_full = mOutPtr >= DEPTH - 1 - GRACE_PERIOD && mOutPtr != ~{ADDR_WIDTH+1{1'b0}};
assign if_full_n = ~almost_full;
/*******************************************/
assign shiftReg_data = if_din;
assign if_dout = shiftReg_q;
always @ (posedge clk) begin
    if (reset == 1'b1)
    begin
        mOutPtr <= ~{ADDR_WIDTH+1{1'b0}};
        internal_empty_n <= 1'b0;
        internal_full_n <= 1'b1;
    end
    else begin
        if (((if_read & if_read_ce) == 1 & internal_empty_n == 1) && 
            ((if_write & if_write_ce) == 0 | internal_full_n == 0))
        begin
            mOutPtr <= mOutPtr - 5'd1;
            if (mOutPtr == 0)
                internal_empty_n <= 1'b0;
            internal_full_n <= 1'b1;
        end 
        else if (((if_read & if_read_ce) == 0 | internal_empty_n == 0) && 
            ((if_write & if_write_ce) == 1 & internal_full_n == 1))
        begin
            mOutPtr <= mOutPtr + 5'd1;
            internal_empty_n <= 1'b1;
            if (mOutPtr == DEPTH - 5'd2)
                internal_full_n <= 1'b0;
        end 
    end
end
assign shiftReg_addr = mOutPtr[ADDR_WIDTH] == 1'b0 ? mOutPtr[ADDR_WIDTH-1:0]:{ADDR_WIDTH{1'b0}};
assign shiftReg_ce = (if_write & if_write_ce) & internal_full_n;
fifo_srl_almost_full_internal 
#(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH),
    .DEPTH(DEPTH))
U_fifo_w32_d16_A_ram (
    .clk(clk),
    .data(shiftReg_data),
    .ce(shiftReg_ce),
    .a(shiftReg_addr),
    .q(shiftReg_q));
endmodule  
module fifo_srl_almost_full_internal (
    clk,
    data,
    ce,
    a,
    q);
parameter DATA_WIDTH = 32'd32;
parameter ADDR_WIDTH = 32'd4;
parameter DEPTH = 5'd16;
input clk;
input [DATA_WIDTH-1:0] data;
input ce;
input [ADDR_WIDTH-1:0] a;
output [DATA_WIDTH-1:0] q;
reg[DATA_WIDTH-1:0] SRL_SIG [0:DEPTH-1];
integer i;
always @ (posedge clk)
    begin
        if (ce)
        begin
            for (i=0;i<DEPTH-1;i=i+1)
                SRL_SIG[i+1] <= SRL_SIG[i];
            SRL_SIG[0] <= data;
        end
    end
assign q = SRL_SIG[a];
endmodule
///////////////////////////////////////////////////////////
// first-word fall-through (FWFT) FIFO using block RAM or URAM (let Vivado choose)
// based on HLS generated code
module fifo_bram_almost_full #(
  parameter MEM_STYLE  = "auto",
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 5,
  parameter DEPTH      = 32,
  parameter GRACE_PERIOD = 2
) (
  input wire clk,
  input wire reset,
  // write
  output wire                  if_full_n,
  input  wire                  if_write_ce,
  input  wire                  if_write,
  input  wire [DATA_WIDTH-1:0] if_din,
  // read
  output wire                  if_empty_n,
  input  wire                  if_read_ce,
  input  wire                  if_read,
  output wire [DATA_WIDTH-1:0] if_dout
);
(* ram_style = MEM_STYLE *)
reg  [DATA_WIDTH-1:0] mem[0:DEPTH-1];
reg  [DATA_WIDTH-1:0] q_buf;
reg  [ADDR_WIDTH-1:0] waddr;
reg  [ADDR_WIDTH-1:0] raddr;
wire [ADDR_WIDTH-1:0] wnext;
wire [ADDR_WIDTH-1:0] rnext;
wire                  push;
wire                  pop;
reg  [ADDR_WIDTH-1:0] used;
reg                   full_n;
reg                   empty_n;
reg  [DATA_WIDTH-1:0] q_tmp;
reg                   show_ahead;
reg  [DATA_WIDTH-1:0] dout_buf;
reg                   dout_valid;
localparam DepthM1 = DEPTH[ADDR_WIDTH-1:0] - 1'd1;
/**************************************/
wire almost_full = (used >= DEPTH - 1 - GRACE_PERIOD);
//assign if_full_n  = full_n;
assign if_full_n  = ~almost_full;
/**************************************/
assign if_empty_n = dout_valid;
assign if_dout    = dout_buf;
assign push       = full_n & if_write_ce & if_write;
assign pop        = empty_n & if_read_ce & (~dout_valid | if_read);
assign wnext      = !push              ? waddr              :
                    (waddr == DepthM1) ? {ADDR_WIDTH{1'b0}} : waddr + 1'd1;
assign rnext      = !pop               ? raddr              :
                    (raddr == DepthM1) ? {ADDR_WIDTH{1'b0}} : raddr + 1'd1;
// waddr
always @(posedge clk) begin
  if (reset)
    waddr <= {ADDR_WIDTH{1'b0}};
  else
    waddr <= wnext;
end
// raddr
always @(posedge clk) begin
  if (reset)
    raddr <= {ADDR_WIDTH{1'b0}};
  else
    raddr <= rnext;
end
// used
always @(posedge clk) begin
  if (reset)
    used <= {ADDR_WIDTH{1'b0}};
  else if (push && !pop)
    used <= used + 1'b1;
  else if (!push && pop)
    used <= used - 1'b1;
end
// full_n
always @(posedge clk) begin
  if (reset)
    full_n <= 1'b1;
  else if (push && !pop)
    full_n <= (used != DepthM1);
  else if (!push && pop)
    full_n <= 1'b1;
end
// empty_n
always @(posedge clk) begin
  if (reset)
    empty_n <= 1'b0;
  else if (push && !pop)
    empty_n <= 1'b1;
  else if (!push && pop)
    empty_n <= (used != {{(ADDR_WIDTH-1){1'b0}},1'b1});
end
// mem
always @(posedge clk) begin
  if (push)
    mem[waddr] <= if_din;
end
// q_buf
always @(posedge clk) begin
  q_buf <= mem[rnext];
end
// q_tmp
always @(posedge clk) begin
  if (reset)
    q_tmp <= {DATA_WIDTH{1'b0}};
  else if (push)
    q_tmp <= if_din;
end
// show_ahead
always @(posedge clk) begin
  if (reset)
    show_ahead <= 1'b0;
  else if (push && used == {{(ADDR_WIDTH-1){1'b0}},pop})
    show_ahead <= 1'b1;
  else
    show_ahead <= 1'b0;
end
// dout_buf
always @(posedge clk) begin
  if (reset)
    dout_buf <= {DATA_WIDTH{1'b0}};
  else if (pop)
    dout_buf <= show_ahead? q_tmp : q_buf;
end
// dout_valid
always @(posedge clk) begin
  if (reset)
    dout_valid <= 1'b0;
  else if (pop)
    dout_valid <= 1'b1;
  else if (if_read_ce & if_read)
    dout_valid <= 1'b0;
end
endmodule  // fifo_bram

