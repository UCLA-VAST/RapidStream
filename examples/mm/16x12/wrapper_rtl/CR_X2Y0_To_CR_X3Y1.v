

`timescale 1 ns / 1 ps
module CR_X2Y0_To_CR_X3Y1 (
  w_IO_L2_in140_U0_fifo_w_out_V_V_din,
  fifo_w_w_IO_L2_in_6_V_V_full_n,
  w_IO_L2_in140_U0_fifo_w_out_V_V_write,
  PE_wrapper260_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_10_2_V_V_full_n,
  PE_wrapper260_U0_fifo_cin_out_V_V_write,
  PE_wrapper224_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_7_2_V_V_full_n,
  PE_wrapper224_U0_fifo_cin_out_V_V_write,
  PE_wrapper261_U0_fifo_w_out_V_V_din,
  fifo_w_PE_9_4_V_V_full_n,
  PE_wrapper261_U0_fifo_w_out_V_V_write,
  PE_wrapper235_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_7_1_V_full_n,
  PE_wrapper235_U0_fifo_cout_drain_out_V_write,
  PE_wrapper225_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_6_3_V_full_n,
  PE_wrapper225_U0_fifo_cout_drain_out_V_write,
  w_IO_L2_in141_U0_fifo_w_out_V_V_din,
  fifo_w_w_IO_L2_in_7_V_V_full_n,
  w_IO_L2_in141_U0_fifo_w_out_V_V_write,
  PE_wrapper222_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_6_0_V_full_n,
  PE_wrapper222_U0_fifo_cout_drain_out_V_write,
  PE_wrapper247_U0_fifo_w_out_V_V_din,
  fifo_w_PE_8_2_V_V_full_n,
  PE_wrapper247_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_3_6_V_V_full_n,
  cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper211_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_6_1_V_V_full_n,
  PE_wrapper211_U0_fifo_cin_out_V_V_write,
  cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_full_n,
  cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_write,
  w_IO_L2_in141_U0_fifo_w_local_out_V_V_din,
  fifo_w_PE_6_0_V_V_full_n,
  w_IO_L2_in141_U0_fifo_w_local_out_V_V_write,
  PE_wrapper261_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_9_3_V_full_n,
  PE_wrapper261_U0_fifo_cout_drain_out_V_write,
  PE_wrapper222_U0_fifo_w_out_V_V_din,
  fifo_w_PE_6_1_V_V_full_n,
  PE_wrapper222_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_0_6_V_V_full_n,
  cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper236_U0_fifo_w_out_V_V_din,
  fifo_w_PE_7_3_V_V_full_n,
  PE_wrapper236_U0_fifo_w_out_V_V_write,
  PE_wrapper223_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_7_1_V_V_full_n,
  PE_wrapper223_U0_fifo_cin_out_V_V_write,
  cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_full_n,
  cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper249_U0_fifo_w_out_V_V_din,
  fifo_w_PE_8_4_V_V_full_n,
  PE_wrapper249_U0_fifo_w_out_V_V_write,
  PE_wrapper223_U0_fifo_w_out_V_V_din,
  fifo_w_PE_6_2_V_V_full_n,
  PE_wrapper223_U0_fifo_w_out_V_V_write,
  PE_wrapper259_U0_fifo_w_out_V_V_din,
  fifo_w_PE_9_2_V_V_full_n,
  PE_wrapper259_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_full_n,
  cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper237_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_8_3_V_V_full_n,
  PE_wrapper237_U0_fifo_cin_out_V_V_write,
  cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_2_6_V_V_full_n,
  cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper224_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_6_2_V_full_n,
  PE_wrapper224_U0_fifo_cout_drain_out_V_write,
  PE_wrapper235_U0_fifo_w_out_V_V_din,
  fifo_w_PE_7_2_V_V_full_n,
  PE_wrapper235_U0_fifo_w_out_V_V_write,
  PE_wrapper261_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_10_3_V_V_full_n,
  PE_wrapper261_U0_fifo_cin_out_V_V_write,
  cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_full_n,
  cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_write,
  cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_1_6_V_V_full_n,
  cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper237_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_7_3_V_full_n,
  PE_wrapper237_U0_fifo_cout_drain_out_V_write,
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
wire w_IO_L2_in141_U0_ap_start;
wire w_IO_L2_in141_U0_ap_done;
wire w_IO_L2_in141_U0_ap_continue;
wire w_IO_L2_in141_U0_ap_idle;
wire w_IO_L2_in141_U0_ap_ready;
wire w_IO_L2_in141_U0_fifo_w_in_V_V_read;
wire PE_wrapper223_U0_ap_start;
wire PE_wrapper223_U0_ap_done;
wire PE_wrapper223_U0_ap_continue;
wire PE_wrapper223_U0_ap_idle;
wire PE_wrapper223_U0_ap_ready;
wire PE_wrapper223_U0_fifo_cin_in_V_V_read;
wire [31:0] PE_wrapper223_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper223_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper223_U0_fifo_w_in_V_V_read;
wire PE_wrapper236_U0_ap_start;
wire PE_wrapper236_U0_ap_done;
wire PE_wrapper236_U0_ap_continue;
wire PE_wrapper236_U0_ap_idle;
wire PE_wrapper236_U0_ap_ready;
wire PE_wrapper236_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper236_U0_fifo_cin_out_V_V_din;
wire PE_wrapper236_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper236_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper236_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper236_U0_fifo_w_in_V_V_read;
wire PE_wrapper248_U0_ap_start;
wire PE_wrapper248_U0_ap_done;
wire PE_wrapper248_U0_ap_continue;
wire PE_wrapper248_U0_ap_idle;
wire PE_wrapper248_U0_ap_ready;
wire PE_wrapper248_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper248_U0_fifo_cin_out_V_V_din;
wire PE_wrapper248_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper248_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper248_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper248_U0_fifo_w_in_V_V_read;
wire [255:0] PE_wrapper248_U0_fifo_w_out_V_V_din;
wire PE_wrapper248_U0_fifo_w_out_V_V_write;
wire PE_wrapper249_U0_ap_start;
wire PE_wrapper249_U0_ap_done;
wire PE_wrapper249_U0_ap_continue;
wire PE_wrapper249_U0_ap_idle;
wire PE_wrapper249_U0_ap_ready;
wire PE_wrapper249_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper249_U0_fifo_cin_out_V_V_din;
wire PE_wrapper249_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper249_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper249_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper249_U0_fifo_w_in_V_V_read;
wire PE_wrapper260_U0_ap_start;
wire PE_wrapper260_U0_ap_done;
wire PE_wrapper260_U0_ap_continue;
wire PE_wrapper260_U0_ap_idle;
wire PE_wrapper260_U0_ap_ready;
wire PE_wrapper260_U0_fifo_cin_in_V_V_read;
wire [31:0] PE_wrapper260_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper260_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper260_U0_fifo_w_in_V_V_read;
wire [255:0] PE_wrapper260_U0_fifo_w_out_V_V_din;
wire PE_wrapper260_U0_fifo_w_out_V_V_write;
wire PE_wrapper261_U0_ap_start;
wire PE_wrapper261_U0_ap_done;
wire PE_wrapper261_U0_ap_continue;
wire PE_wrapper261_U0_ap_idle;
wire PE_wrapper261_U0_ap_ready;
wire PE_wrapper261_U0_fifo_cin_in_V_V_read;
wire PE_wrapper261_U0_fifo_w_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper376_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper376_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper376_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper376_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper376_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper391_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper391_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper391_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper391_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper391_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper392_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper392_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper392_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper392_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper392_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper405_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper405_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper405_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper405_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper405_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper406_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper406_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper406_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper406_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper406_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper407_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper407_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper407_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper407_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper407_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper408_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper408_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper408_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper408_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper408_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper422_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper422_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper422_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper422_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper422_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper423_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper423_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper423_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper423_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper423_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper424_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper424_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper424_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper424_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper424_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_local_in_V_read;
wire [255:0] fifo_w_w_IO_L2_in_6_V_V_dout;
wire fifo_w_w_IO_L2_in_6_V_V_empty_n;
wire [255:0] fifo_cin_PE_6_1_V_V_dout;
wire fifo_cin_PE_6_1_V_V_empty_n;
wire [31:0] fifo_cout_drain_PE_6_0_V_dout;
wire fifo_cout_drain_PE_6_0_V_empty_n;
wire [255:0] fifo_w_PE_6_1_V_V_dout;
wire fifo_w_PE_6_1_V_V_empty_n;
wire fifo_cout_drain_PE_6_1_V_full_n;
wire [31:0] fifo_cout_drain_PE_6_1_V_dout;
wire fifo_cout_drain_PE_6_1_V_empty_n;
wire [255:0] fifo_cin_PE_7_2_V_V_dout;
wire fifo_cin_PE_7_2_V_V_empty_n;
wire [31:0] fifo_cout_drain_PE_6_2_V_dout;
wire fifo_cout_drain_PE_6_2_V_empty_n;
wire [31:0] fifo_cout_drain_PE_6_3_V_dout;
wire fifo_cout_drain_PE_6_3_V_empty_n;
wire [31:0] fifo_cout_drain_PE_7_1_V_dout;
wire fifo_cout_drain_PE_7_1_V_empty_n;
wire [255:0] fifo_w_PE_7_2_V_V_dout;
wire fifo_w_PE_7_2_V_V_empty_n;
wire fifo_cin_PE_8_2_V_V_full_n;
wire [255:0] fifo_cin_PE_8_2_V_V_dout;
wire fifo_cin_PE_8_2_V_V_empty_n;
wire fifo_cout_drain_PE_7_2_V_full_n;
wire [31:0] fifo_cout_drain_PE_7_2_V_dout;
wire fifo_cout_drain_PE_7_2_V_empty_n;
wire [255:0] fifo_cin_PE_8_3_V_V_dout;
wire fifo_cin_PE_8_3_V_V_empty_n;
wire [31:0] fifo_cout_drain_PE_7_3_V_dout;
wire fifo_cout_drain_PE_7_3_V_empty_n;
wire [255:0] fifo_w_PE_8_2_V_V_dout;
wire fifo_w_PE_8_2_V_V_empty_n;
wire fifo_cin_PE_9_2_V_V_full_n;
wire [255:0] fifo_cin_PE_9_2_V_V_dout;
wire fifo_cin_PE_9_2_V_V_empty_n;
wire fifo_cout_drain_PE_8_2_V_full_n;
wire [31:0] fifo_cout_drain_PE_8_2_V_dout;
wire fifo_cout_drain_PE_8_2_V_empty_n;
wire fifo_w_PE_8_3_V_V_full_n;
wire [255:0] fifo_w_PE_8_3_V_V_dout;
wire fifo_w_PE_8_3_V_V_empty_n;
wire fifo_cin_PE_9_3_V_V_full_n;
wire [255:0] fifo_cin_PE_9_3_V_V_dout;
wire fifo_cin_PE_9_3_V_V_empty_n;
wire fifo_cout_drain_PE_8_3_V_full_n;
wire [31:0] fifo_cout_drain_PE_8_3_V_dout;
wire fifo_cout_drain_PE_8_3_V_empty_n;
wire [255:0] fifo_w_PE_9_2_V_V_dout;
wire fifo_w_PE_9_2_V_V_empty_n;
wire fifo_cout_drain_PE_9_2_V_full_n;
wire [31:0] fifo_cout_drain_PE_9_2_V_dout;
wire fifo_cout_drain_PE_9_2_V_empty_n;
wire fifo_w_PE_9_3_V_V_full_n;
wire [255:0] fifo_w_PE_9_3_V_V_dout;
wire fifo_w_PE_9_3_V_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_empty_n;
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
input [255:0] w_IO_L2_in140_U0_fifo_w_out_V_V_din;
output  fifo_w_w_IO_L2_in_6_V_V_full_n;
input  w_IO_L2_in140_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper260_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_10_2_V_V_full_n;
output  PE_wrapper260_U0_fifo_cin_out_V_V_write;
input [255:0] PE_wrapper224_U0_fifo_cin_out_V_V_din;
output  fifo_cin_PE_7_2_V_V_full_n;
input  PE_wrapper224_U0_fifo_cin_out_V_V_write;
output [255:0] PE_wrapper261_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_9_4_V_V_full_n;
output  PE_wrapper261_U0_fifo_w_out_V_V_write;
input [31:0] PE_wrapper235_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_7_1_V_full_n;
input  PE_wrapper235_U0_fifo_cout_drain_out_V_write;
input [31:0] PE_wrapper225_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_6_3_V_full_n;
input  PE_wrapper225_U0_fifo_cout_drain_out_V_write;
output [255:0] w_IO_L2_in141_U0_fifo_w_out_V_V_din;
input  fifo_w_w_IO_L2_in_7_V_V_full_n;
output  w_IO_L2_in141_U0_fifo_w_out_V_V_write;
input [31:0] PE_wrapper222_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_6_0_V_full_n;
input  PE_wrapper222_U0_fifo_cout_drain_out_V_write;
input [255:0] PE_wrapper247_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_8_2_V_V_full_n;
input  PE_wrapper247_U0_fifo_w_out_V_V_write;
output [63:0] cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L1_out_3_6_V_V_full_n;
output  cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_write;
input [255:0] PE_wrapper211_U0_fifo_cin_out_V_V_din;
output  fifo_cin_PE_6_1_V_V_full_n;
input  PE_wrapper211_U0_fifo_cin_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_write;
output [255:0] w_IO_L2_in141_U0_fifo_w_local_out_V_V_din;
input  fifo_w_PE_6_0_V_V_full_n;
output  w_IO_L2_in141_U0_fifo_w_local_out_V_V_write;
output [31:0] PE_wrapper261_U0_fifo_cout_drain_out_V_din;
input  fifo_cout_drain_PE_9_3_V_full_n;
output  PE_wrapper261_U0_fifo_cout_drain_out_V_write;
input [255:0] PE_wrapper222_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_6_1_V_V_full_n;
input  PE_wrapper222_U0_fifo_w_out_V_V_write;
output [63:0] cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L1_out_0_6_V_V_full_n;
output  cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_write;
output [255:0] PE_wrapper236_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_7_3_V_V_full_n;
output  PE_wrapper236_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper223_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_7_1_V_V_full_n;
output  PE_wrapper223_U0_fifo_cin_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_write;
output [255:0] PE_wrapper249_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_8_4_V_V_full_n;
output  PE_wrapper249_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper223_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_6_2_V_V_full_n;
output  PE_wrapper223_U0_fifo_w_out_V_V_write;
input [255:0] PE_wrapper259_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_9_2_V_V_full_n;
input  PE_wrapper259_U0_fifo_w_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_write;
input [255:0] PE_wrapper237_U0_fifo_cin_out_V_V_din;
output  fifo_cin_PE_8_3_V_V_full_n;
input  PE_wrapper237_U0_fifo_cin_out_V_V_write;
output [63:0] cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L1_out_2_6_V_V_full_n;
output  cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_write;
input [31:0] PE_wrapper224_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_6_2_V_full_n;
input  PE_wrapper224_U0_fifo_cout_drain_out_V_write;
input [255:0] PE_wrapper235_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_7_2_V_V_full_n;
input  PE_wrapper235_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper261_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_10_3_V_V_full_n;
output  PE_wrapper261_U0_fifo_cin_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_write;
output [63:0] cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L1_out_1_6_V_V_full_n;
output  cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_write;
input [31:0] PE_wrapper237_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_7_3_V_full_n;
input  PE_wrapper237_U0_fifo_cout_drain_out_V_write;
input  ap_start;
output ap_done;
output ap_idle;
output ap_ready;
input  ap_continue;
input ap_clk;
input ap_rst_n;
(* keep_hierarchy = "yes" *)
kernel0_w_IO_L2_in141
w_IO_L2_in141_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(w_IO_L2_in141_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(w_IO_L2_in141_U0_ap_idle),
  .ap_ready(w_IO_L2_in141_U0_ap_ready),
  .fifo_w_in_V_V_dout(fifo_w_w_IO_L2_in_6_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_w_IO_L2_in_6_V_V_empty_n),
  .fifo_w_in_V_V_read(w_IO_L2_in141_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(w_IO_L2_in141_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_w_IO_L2_in_7_V_V_full_n),
  .fifo_w_out_V_V_write(w_IO_L2_in141_U0_fifo_w_out_V_V_write),
  .fifo_w_local_out_V_V_din(w_IO_L2_in141_U0_fifo_w_local_out_V_V_din),
  .fifo_w_local_out_V_V_full_n(fifo_w_PE_6_0_V_V_full_n),
  .fifo_w_local_out_V_V_write(w_IO_L2_in141_U0_fifo_w_local_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper223
PE_wrapper223_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper223_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper223_U0_ap_idle),
  .ap_ready(PE_wrapper223_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_6_1_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_6_1_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper223_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper223_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_7_1_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper223_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper223_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_6_1_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper223_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_6_1_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_6_1_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper223_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper223_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_6_2_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper223_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper236
PE_wrapper236_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper236_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper236_U0_ap_idle),
  .ap_ready(PE_wrapper236_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_7_2_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_7_2_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper236_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper236_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_8_2_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper236_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper236_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_7_2_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper236_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_7_2_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_7_2_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper236_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper236_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_7_3_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper236_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper248
PE_wrapper248_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper248_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper248_U0_ap_idle),
  .ap_ready(PE_wrapper248_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_8_2_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_8_2_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper248_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper248_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_9_2_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper248_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper248_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_8_2_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper248_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_8_2_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_8_2_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper248_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper248_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_8_3_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper248_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper249
PE_wrapper249_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper249_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper249_U0_ap_idle),
  .ap_ready(PE_wrapper249_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_8_3_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_8_3_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper249_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper249_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_9_3_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper249_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper249_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_8_3_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper249_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_8_3_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_8_3_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper249_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper249_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_8_4_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper249_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper260
PE_wrapper260_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper260_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper260_U0_ap_idle),
  .ap_ready(PE_wrapper260_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_9_2_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_9_2_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper260_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper260_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_10_2_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper260_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper260_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_9_2_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper260_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_9_2_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_9_2_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper260_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper260_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_9_3_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper260_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper261
PE_wrapper261_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper261_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper261_U0_ap_idle),
  .ap_ready(PE_wrapper261_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_9_3_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_9_3_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper261_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper261_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_10_3_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper261_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper261_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_9_3_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper261_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_9_3_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_9_3_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper261_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper261_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_9_4_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper261_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper376
cout_drain_IO_L1_out_wrapper376_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper376_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper376_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper376_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_0_6_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_6_0_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_6_0_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper391
cout_drain_IO_L1_out_wrapper391_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper391_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper391_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper391_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_7_1_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_7_1_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper392
cout_drain_IO_L1_out_wrapper392_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper392_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper392_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper392_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_1_6_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_6_1_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_6_1_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper405
cout_drain_IO_L1_out_wrapper405_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper405_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper405_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper405_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_9_2_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_9_2_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper406
cout_drain_IO_L1_out_wrapper406_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper406_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper406_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper406_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_8_2_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_8_2_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper407
cout_drain_IO_L1_out_wrapper407_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper407_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper407_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper407_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_7_2_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_7_2_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper408
cout_drain_IO_L1_out_wrapper408_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper408_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper408_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper408_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_6_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_6_2_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_6_2_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper422
cout_drain_IO_L1_out_wrapper422_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper422_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper422_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper422_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_8_3_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_8_3_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper423
cout_drain_IO_L1_out_wrapper423_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper423_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper423_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper423_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_7_3_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_7_3_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper424
cout_drain_IO_L1_out_wrapper424_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper424_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper424_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper424_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_6_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_6_3_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_6_3_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_9_3_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper249_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_9_3_V_V_full_n),
  .if_write(PE_wrapper249_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_9_3_V_V_dout),
  .if_empty_n(fifo_cin_PE_9_3_V_V_empty_n),
  .if_read(PE_wrapper261_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_9_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(37),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_7_2_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper236_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_7_2_V_full_n),
  .if_write(PE_wrapper236_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_7_2_V_dout),
  .if_empty_n(fifo_cout_drain_PE_7_2_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_7_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_8_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper407_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_8_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_1_7_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(35),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_8_3_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper249_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_8_3_V_full_n),
  .if_write(PE_wrapper249_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_8_3_V_dout),
  .if_empty_n(fifo_cout_drain_PE_8_3_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(31),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_9_2_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper260_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_9_2_V_full_n),
  .if_write(PE_wrapper260_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_9_2_V_dout),
  .if_empty_n(fifo_cout_drain_PE_9_2_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(33),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_8_2_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper248_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_8_2_V_full_n),
  .if_write(PE_wrapper248_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_8_2_V_dout),
  .if_empty_n(fifo_cout_drain_PE_8_2_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper406_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_9_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper248_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_9_2_V_V_full_n),
  .if_write(PE_wrapper248_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_9_2_V_V_dout),
  .if_empty_n(fifo_cin_PE_9_2_V_V_empty_n),
  .if_read(PE_wrapper260_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_w_PE_8_3_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper248_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_8_3_V_V_full_n),
  .if_write(PE_wrapper248_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_8_3_V_V_dout),
  .if_empty_n(fifo_w_PE_8_3_V_V_empty_n),
  .if_read(PE_wrapper249_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(37),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_6_1_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper223_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_6_1_V_full_n),
  .if_write(PE_wrapper223_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_6_1_V_dout),
  .if_empty_n(fifo_cout_drain_PE_6_1_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper392_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_7_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_8_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper236_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_8_2_V_V_full_n),
  .if_write(PE_wrapper236_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_8_2_V_V_dout),
  .if_empty_n(fifo_cin_PE_8_2_V_V_empty_n),
  .if_read(PE_wrapper248_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_w_PE_9_3_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper260_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_9_3_V_V_full_n),
  .if_write(PE_wrapper260_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_9_3_V_V_dout),
  .if_empty_n(fifo_w_PE_9_3_V_V_empty_n),
  .if_read(PE_wrapper261_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(6),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(7)
)
fifo_w_w_IO_L2_in_6_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(w_IO_L2_in140_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_w_IO_L2_in_6_V_V_full_n),
  .if_write(w_IO_L2_in140_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_w_IO_L2_in_6_V_V_dout),
  .if_empty_n(fifo_w_w_IO_L2_in_6_V_V_empty_n),
  .if_read(w_IO_L2_in141_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_cin_PE_7_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper224_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_7_2_V_V_full_n),
  .if_write(PE_wrapper224_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_7_2_V_V_dout),
  .if_empty_n(fifo_cin_PE_7_2_V_V_empty_n),
  .if_read(PE_wrapper236_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(34),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_7_1_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper235_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_7_1_V_full_n),
  .if_write(PE_wrapper235_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_7_1_V_dout),
  .if_empty_n(fifo_cout_drain_PE_7_1_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(42),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_6_3_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper225_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_6_3_V_full_n),
  .if_write(PE_wrapper225_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_6_3_V_dout),
  .if_empty_n(fifo_cout_drain_PE_6_3_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper424_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(38),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_6_0_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper222_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_6_0_V_full_n),
  .if_write(PE_wrapper222_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_6_0_V_dout),
  .if_empty_n(fifo_cout_drain_PE_6_0_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_w_PE_8_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper247_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_8_2_V_V_full_n),
  .if_write(PE_wrapper247_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_8_2_V_V_dout),
  .if_empty_n(fifo_w_PE_8_2_V_V_empty_n),
  .if_read(PE_wrapper248_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_cin_PE_6_1_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper211_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_6_1_V_V_full_n),
  .if_write(PE_wrapper211_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_6_1_V_V_dout),
  .if_empty_n(fifo_cin_PE_6_1_V_V_empty_n),
  .if_read(PE_wrapper223_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(4),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper421_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_3_9_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper422_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_w_PE_6_1_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper222_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_6_1_V_V_full_n),
  .if_write(PE_wrapper222_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_6_1_V_V_dout),
  .if_empty_n(fifo_w_PE_6_1_V_V_empty_n),
  .if_read(PE_wrapper223_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(5),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(5)
)
fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper404_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_2_10_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper405_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_w_PE_9_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper259_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_9_2_V_V_full_n),
  .if_write(PE_wrapper259_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_9_2_V_V_dout),
  .if_empty_n(fifo_w_PE_9_2_V_V_empty_n),
  .if_read(PE_wrapper260_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(5),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(5)
)
fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper390_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_1_8_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper391_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(6),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_cin_PE_8_3_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper237_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_8_3_V_V_full_n),
  .if_write(PE_wrapper237_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_8_3_V_V_dout),
  .if_empty_n(fifo_cin_PE_8_3_V_V_empty_n),
  .if_read(PE_wrapper249_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(40),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_6_2_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper224_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_6_2_V_full_n),
  .if_write(PE_wrapper224_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_6_2_V_dout),
  .if_empty_n(fifo_cout_drain_PE_6_2_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper408_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_w_PE_7_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper235_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_7_2_V_V_full_n),
  .if_write(PE_wrapper235_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_7_2_V_V_dout),
  .if_empty_n(fifo_w_PE_7_2_V_V_empty_n),
  .if_read(PE_wrapper236_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(4),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper375_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_0_7_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper376_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(40),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_7_3_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper237_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_7_3_V_full_n),
  .if_write(PE_wrapper237_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_7_3_V_dout),
  .if_empty_n(fifo_cout_drain_PE_7_3_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper423_U0_fifo_cout_drain_local_in_V_read)
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

