

`timescale 1 ns / 1 ps


module CR_X6Y4_To_CR_X7Y5_ctrl (
  input [63:0] cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1,
  output [63:0] cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_2,
  output fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_1,
  input fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_2,
  input cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_1,
  output cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_2,
  input [255:0] PE_wrapper165_U0_fifo_w_out_V_V_din_pass_1,
  output fifo_w_PE_1_4_V_V_full_n_pass_1,
  input PE_wrapper165_U0_fifo_w_out_V_V_write_pass_1,
  output [63:0] cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din_pass_0,
  input fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_pass_0,
  output cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write_pass_0,
  input [255:0] cin_IO_L2_in127_U0_fifo_cin_out_V_V_din_pass_1,
  output fifo_cin_cin_IO_L2_in_4_V_V_full_n_pass_1,
  input cin_IO_L2_in127_U0_fifo_cin_out_V_V_write_pass_1,
  output [255:0] PE_wrapper179_U0_fifo_w_out_V_V_din_pass_0,
  input fifo_w_PE_2_6_V_V_full_n_pass_0,
  output PE_wrapper179_U0_fifo_w_out_V_V_write_pass_0,
  output [255:0] cin_IO_L2_in128_U0_fifo_cin_out_V_V_din_pass_0,
  input fifo_cin_cin_IO_L2_in_5_V_V_full_n_pass_0,
  output cin_IO_L2_in128_U0_fifo_cin_out_V_V_write_pass_0,
  output [31:0] PE_wrapper179_U0_fifo_cout_drain_out_V_din_pass_0,
  input fifo_cout_drain_PE_2_5_V_full_n_pass_0,
  output PE_wrapper179_U0_fifo_cout_drain_out_V_write_pass_0,
  input [255:0] PE_wrapper177_U0_fifo_w_out_V_V_din_pass_1,
  output fifo_w_PE_2_4_V_V_full_n_pass_1,
  input PE_wrapper177_U0_fifo_w_out_V_V_write_pass_1,
  input [255:0] PE_wrapper153_U0_fifo_w_out_V_V_din_pass_1,
  output fifo_w_PE_0_4_V_V_full_n_pass_1,
  input PE_wrapper153_U0_fifo_w_out_V_V_write_pass_1,
  output [255:0] PE_wrapper190_U0_fifo_cin_out_V_V_din_pass_0,
  input fifo_cin_PE_4_4_V_V_full_n_pass_0,
  output PE_wrapper190_U0_fifo_cin_out_V_V_write_pass_0,
  output [255:0] PE_wrapper166_U0_fifo_w_out_V_V_din_pass_0,
  input fifo_w_PE_1_5_V_V_full_n_pass_0,
  output PE_wrapper166_U0_fifo_w_out_V_V_write_pass_0,
  output [255:0] PE_wrapper154_U0_fifo_w_out_V_V_din_pass_0,
  input fifo_w_PE_0_5_V_V_full_n_pass_0,
  output PE_wrapper154_U0_fifo_w_out_V_V_write_pass_0,
  input [63:0] cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din_pass_0,
  output fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n_pass_0,
  input cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write_pass_0,
  output [255:0] PE_wrapper190_U0_fifo_w_out_V_V_din_pass_0,
  input fifo_w_PE_3_5_V_V_full_n_pass_0,
  output PE_wrapper190_U0_fifo_w_out_V_V_write_pass_0,
  output [255:0] PE_wrapper179_U0_fifo_cin_out_V_V_din_pass_0,
  input fifo_cin_PE_3_5_V_V_full_n_pass_0,
  output PE_wrapper179_U0_fifo_cin_out_V_V_write_pass_0,
  input [31:0] PE_wrapper202_U0_fifo_cout_drain_out_V_din_pass_0,
  output fifo_cout_drain_PE_4_4_V_full_n_pass_0,
  input PE_wrapper202_U0_fifo_cout_drain_out_V_write_pass_0,
  input [255:0] PE_wrapper189_U0_fifo_w_out_V_V_din_pass_1,
  output fifo_w_PE_3_4_V_V_full_n_pass_1,
  input PE_wrapper189_U0_fifo_w_out_V_V_write_pass_1,
  input [255:0] PE_wrapper167_U0_fifo_cin_out_V_V_din_pass_0,
  output fifo_cin_PE_2_5_V_V_full_n_pass_0,
  input PE_wrapper167_U0_fifo_cin_out_V_V_write_pass_0,
  input [63:0] cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0,
  output fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n_pass_0,
  input cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write_pass_0,
  input ap_clk,
  input ap_start_Boundary_X6Y4_To_X8Y4,
  input ap_rst_n_Boundary_X6Y4_To_X8Y4,
  output ap_done_Boundary_X6Y4_To_X8Y4,
  output ap_start_Boundary_X6Y6_To_X8Y6,
  output ap_rst_n_Boundary_X6Y6_To_X8Y6,
  input ap_done_Boundary_X6Y6_To_X8Y6
);
wire ap_start;
wire ap_rst_n;
wire ap_done;
wire ap_idle;
wire ap_ready;
wire ap_continue = 1;
(* keep = "true" *) reg ap_start_Boundary_X6Y4_To_X8Y4_q;
always @ (posedge ap_clk) ap_start_Boundary_X6Y4_To_X8Y4_q <= ap_start_Boundary_X6Y4_To_X8Y4;
assign ap_start_Boundary_X6Y6_To_X8Y6 = ap_start_Boundary_X6Y4_To_X8Y4_q;
assign ap_start = ap_start_Boundary_X6Y4_To_X8Y4_q;
(* keep = "true" *) reg ap_rst_n_Boundary_X6Y4_To_X8Y4_q;
always @ (posedge ap_clk) ap_rst_n_Boundary_X6Y4_To_X8Y4_q <= ap_rst_n_Boundary_X6Y4_To_X8Y4;
assign ap_rst_n_Boundary_X6Y6_To_X8Y6 = ap_rst_n_Boundary_X6Y4_To_X8Y4_q;
assign ap_rst_n = ap_rst_n_Boundary_X6Y4_To_X8Y4_q;
(* keep = "true" *) reg ap_done_Boundary_X6Y6_To_X8Y6_q;
always @ (posedge ap_clk) begin
  if (!ap_rst_n) ap_done_Boundary_X6Y6_To_X8Y6_q <= 0;
  else ap_done_Boundary_X6Y6_To_X8Y6_q <= ap_done_Boundary_X6Y6_To_X8Y6_q | ap_done_Boundary_X6Y6_To_X8Y6;
end
assign ap_done_Boundary_X6Y4_To_X8Y4 = ap_done_Boundary_X6Y6_To_X8Y6_q & ap_done;


  (* dont_touch = "yes" *) CR_X6Y4_To_CR_X7Y5_routing CR_X6Y4_To_CR_X7Y5_routing_U0 (
    .cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1),
    .cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_2(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_2),
    .fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_1(fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_1),
    .fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_2(fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_2),
    .cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_1(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_1),
    .cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_2(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_2),
    .PE_wrapper165_U0_fifo_w_out_V_V_din_pass_1(PE_wrapper165_U0_fifo_w_out_V_V_din_pass_1),
    .fifo_w_PE_1_4_V_V_full_n_pass_1(fifo_w_PE_1_4_V_V_full_n_pass_1),
    .PE_wrapper165_U0_fifo_w_out_V_V_write_pass_1(PE_wrapper165_U0_fifo_w_out_V_V_write_pass_1),
    .cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din_pass_0(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din_pass_0),
    .fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_pass_0(fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_pass_0),
    .cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write_pass_0(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write_pass_0),
    .cin_IO_L2_in127_U0_fifo_cin_out_V_V_din_pass_1(cin_IO_L2_in127_U0_fifo_cin_out_V_V_din_pass_1),
    .fifo_cin_cin_IO_L2_in_4_V_V_full_n_pass_1(fifo_cin_cin_IO_L2_in_4_V_V_full_n_pass_1),
    .cin_IO_L2_in127_U0_fifo_cin_out_V_V_write_pass_1(cin_IO_L2_in127_U0_fifo_cin_out_V_V_write_pass_1),
    .PE_wrapper179_U0_fifo_w_out_V_V_din_pass_0(PE_wrapper179_U0_fifo_w_out_V_V_din_pass_0),
    .fifo_w_PE_2_6_V_V_full_n_pass_0(fifo_w_PE_2_6_V_V_full_n_pass_0),
    .PE_wrapper179_U0_fifo_w_out_V_V_write_pass_0(PE_wrapper179_U0_fifo_w_out_V_V_write_pass_0),
    .cin_IO_L2_in128_U0_fifo_cin_out_V_V_din_pass_0(cin_IO_L2_in128_U0_fifo_cin_out_V_V_din_pass_0),
    .fifo_cin_cin_IO_L2_in_5_V_V_full_n_pass_0(fifo_cin_cin_IO_L2_in_5_V_V_full_n_pass_0),
    .cin_IO_L2_in128_U0_fifo_cin_out_V_V_write_pass_0(cin_IO_L2_in128_U0_fifo_cin_out_V_V_write_pass_0),
    .PE_wrapper179_U0_fifo_cout_drain_out_V_din_pass_0(PE_wrapper179_U0_fifo_cout_drain_out_V_din_pass_0),
    .fifo_cout_drain_PE_2_5_V_full_n_pass_0(fifo_cout_drain_PE_2_5_V_full_n_pass_0),
    .PE_wrapper179_U0_fifo_cout_drain_out_V_write_pass_0(PE_wrapper179_U0_fifo_cout_drain_out_V_write_pass_0),
    .PE_wrapper177_U0_fifo_w_out_V_V_din_pass_1(PE_wrapper177_U0_fifo_w_out_V_V_din_pass_1),
    .fifo_w_PE_2_4_V_V_full_n_pass_1(fifo_w_PE_2_4_V_V_full_n_pass_1),
    .PE_wrapper177_U0_fifo_w_out_V_V_write_pass_1(PE_wrapper177_U0_fifo_w_out_V_V_write_pass_1),
    .PE_wrapper153_U0_fifo_w_out_V_V_din_pass_1(PE_wrapper153_U0_fifo_w_out_V_V_din_pass_1),
    .fifo_w_PE_0_4_V_V_full_n_pass_1(fifo_w_PE_0_4_V_V_full_n_pass_1),
    .PE_wrapper153_U0_fifo_w_out_V_V_write_pass_1(PE_wrapper153_U0_fifo_w_out_V_V_write_pass_1),
    .PE_wrapper190_U0_fifo_cin_out_V_V_din_pass_0(PE_wrapper190_U0_fifo_cin_out_V_V_din_pass_0),
    .fifo_cin_PE_4_4_V_V_full_n_pass_0(fifo_cin_PE_4_4_V_V_full_n_pass_0),
    .PE_wrapper190_U0_fifo_cin_out_V_V_write_pass_0(PE_wrapper190_U0_fifo_cin_out_V_V_write_pass_0),
    .PE_wrapper166_U0_fifo_w_out_V_V_din_pass_0(PE_wrapper166_U0_fifo_w_out_V_V_din_pass_0),
    .fifo_w_PE_1_5_V_V_full_n_pass_0(fifo_w_PE_1_5_V_V_full_n_pass_0),
    .PE_wrapper166_U0_fifo_w_out_V_V_write_pass_0(PE_wrapper166_U0_fifo_w_out_V_V_write_pass_0),
    .PE_wrapper154_U0_fifo_w_out_V_V_din_pass_0(PE_wrapper154_U0_fifo_w_out_V_V_din_pass_0),
    .fifo_w_PE_0_5_V_V_full_n_pass_0(fifo_w_PE_0_5_V_V_full_n_pass_0),
    .PE_wrapper154_U0_fifo_w_out_V_V_write_pass_0(PE_wrapper154_U0_fifo_w_out_V_V_write_pass_0),
    .cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din_pass_0(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din_pass_0),
    .fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n_pass_0(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n_pass_0),
    .cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write_pass_0(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write_pass_0),
    .PE_wrapper190_U0_fifo_w_out_V_V_din_pass_0(PE_wrapper190_U0_fifo_w_out_V_V_din_pass_0),
    .fifo_w_PE_3_5_V_V_full_n_pass_0(fifo_w_PE_3_5_V_V_full_n_pass_0),
    .PE_wrapper190_U0_fifo_w_out_V_V_write_pass_0(PE_wrapper190_U0_fifo_w_out_V_V_write_pass_0),
    .PE_wrapper179_U0_fifo_cin_out_V_V_din_pass_0(PE_wrapper179_U0_fifo_cin_out_V_V_din_pass_0),
    .fifo_cin_PE_3_5_V_V_full_n_pass_0(fifo_cin_PE_3_5_V_V_full_n_pass_0),
    .PE_wrapper179_U0_fifo_cin_out_V_V_write_pass_0(PE_wrapper179_U0_fifo_cin_out_V_V_write_pass_0),
    .PE_wrapper202_U0_fifo_cout_drain_out_V_din_pass_0(PE_wrapper202_U0_fifo_cout_drain_out_V_din_pass_0),
    .fifo_cout_drain_PE_4_4_V_full_n_pass_0(fifo_cout_drain_PE_4_4_V_full_n_pass_0),
    .PE_wrapper202_U0_fifo_cout_drain_out_V_write_pass_0(PE_wrapper202_U0_fifo_cout_drain_out_V_write_pass_0),
    .PE_wrapper189_U0_fifo_w_out_V_V_din_pass_1(PE_wrapper189_U0_fifo_w_out_V_V_din_pass_1),
    .fifo_w_PE_3_4_V_V_full_n_pass_1(fifo_w_PE_3_4_V_V_full_n_pass_1),
    .PE_wrapper189_U0_fifo_w_out_V_V_write_pass_1(PE_wrapper189_U0_fifo_w_out_V_V_write_pass_1),
    .PE_wrapper167_U0_fifo_cin_out_V_V_din_pass_0(PE_wrapper167_U0_fifo_cin_out_V_V_din_pass_0),
    .fifo_cin_PE_2_5_V_V_full_n_pass_0(fifo_cin_PE_2_5_V_V_full_n_pass_0),
    .PE_wrapper167_U0_fifo_cin_out_V_V_write_pass_0(PE_wrapper167_U0_fifo_cin_out_V_V_write_pass_0),
    .cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0),
    .fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n_pass_0(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n_pass_0),
    .cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write_pass_0(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write_pass_0),
    .ap_start(ap_start),
    .ap_done(ap_done),
    .ap_idle(ap_idle),
    .ap_ready(ap_ready),
    .ap_continue(ap_continue),
    .ap_clk(ap_clk),
    .ap_rst_n(ap_rst_n)
  );
endmodule


`timescale 1 ns / 1 ps


module CR_X6Y4_To_CR_X7Y5_routing (
input [63:0] cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1,
output [63:0] cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_2,
output  fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_1,
input  fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_2,
input  cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_1,
output  cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_2,
input [255:0] PE_wrapper165_U0_fifo_w_out_V_V_din_pass_1,
output  fifo_w_PE_1_4_V_V_full_n_pass_1,
input  PE_wrapper165_U0_fifo_w_out_V_V_write_pass_1,
output [63:0] cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din_pass_0,
input  fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_pass_0,
output  cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write_pass_0,
input [255:0] cin_IO_L2_in127_U0_fifo_cin_out_V_V_din_pass_1,
output  fifo_cin_cin_IO_L2_in_4_V_V_full_n_pass_1,
input  cin_IO_L2_in127_U0_fifo_cin_out_V_V_write_pass_1,
output [255:0] PE_wrapper179_U0_fifo_w_out_V_V_din_pass_0,
input  fifo_w_PE_2_6_V_V_full_n_pass_0,
output  PE_wrapper179_U0_fifo_w_out_V_V_write_pass_0,
output [255:0] cin_IO_L2_in128_U0_fifo_cin_out_V_V_din_pass_0,
input  fifo_cin_cin_IO_L2_in_5_V_V_full_n_pass_0,
output  cin_IO_L2_in128_U0_fifo_cin_out_V_V_write_pass_0,
output [31:0] PE_wrapper179_U0_fifo_cout_drain_out_V_din_pass_0,
input  fifo_cout_drain_PE_2_5_V_full_n_pass_0,
output  PE_wrapper179_U0_fifo_cout_drain_out_V_write_pass_0,
input [255:0] PE_wrapper177_U0_fifo_w_out_V_V_din_pass_1,
output  fifo_w_PE_2_4_V_V_full_n_pass_1,
input  PE_wrapper177_U0_fifo_w_out_V_V_write_pass_1,
input [255:0] PE_wrapper153_U0_fifo_w_out_V_V_din_pass_1,
output  fifo_w_PE_0_4_V_V_full_n_pass_1,
input  PE_wrapper153_U0_fifo_w_out_V_V_write_pass_1,
output [255:0] PE_wrapper190_U0_fifo_cin_out_V_V_din_pass_0,
input  fifo_cin_PE_4_4_V_V_full_n_pass_0,
output  PE_wrapper190_U0_fifo_cin_out_V_V_write_pass_0,
output [255:0] PE_wrapper166_U0_fifo_w_out_V_V_din_pass_0,
input  fifo_w_PE_1_5_V_V_full_n_pass_0,
output  PE_wrapper166_U0_fifo_w_out_V_V_write_pass_0,
output [255:0] PE_wrapper154_U0_fifo_w_out_V_V_din_pass_0,
input  fifo_w_PE_0_5_V_V_full_n_pass_0,
output  PE_wrapper154_U0_fifo_w_out_V_V_write_pass_0,
input [63:0] cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din_pass_0,
output  fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n_pass_0,
input  cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write_pass_0,
output [255:0] PE_wrapper190_U0_fifo_w_out_V_V_din_pass_0,
input  fifo_w_PE_3_5_V_V_full_n_pass_0,
output  PE_wrapper190_U0_fifo_w_out_V_V_write_pass_0,
output [255:0] PE_wrapper179_U0_fifo_cin_out_V_V_din_pass_0,
input  fifo_cin_PE_3_5_V_V_full_n_pass_0,
output  PE_wrapper179_U0_fifo_cin_out_V_V_write_pass_0,
input [31:0] PE_wrapper202_U0_fifo_cout_drain_out_V_din_pass_0,
output  fifo_cout_drain_PE_4_4_V_full_n_pass_0,
input  PE_wrapper202_U0_fifo_cout_drain_out_V_write_pass_0,
input [255:0] PE_wrapper189_U0_fifo_w_out_V_V_din_pass_1,
output  fifo_w_PE_3_4_V_V_full_n_pass_1,
input  PE_wrapper189_U0_fifo_w_out_V_V_write_pass_1,
input [255:0] PE_wrapper167_U0_fifo_cin_out_V_V_din_pass_0,
output  fifo_cin_PE_2_5_V_V_full_n_pass_0,
input  PE_wrapper167_U0_fifo_cin_out_V_V_write_pass_0,
input [63:0] cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0,
output  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n_pass_0,
input  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write_pass_0,
input ap_start,
output ap_done,
output ap_idle,
output ap_ready,
input ap_continue,
input ap_clk,
input ap_rst_n
);
  wire [63:0] cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0;
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_0_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[0]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[0]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_1_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[1]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[1]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_2_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[2]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[2]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_3_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[3]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[3]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_4_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[4]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[4]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_5_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[5]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[5]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_6_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[6]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[6]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_7_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[7]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[7]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_8_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[8]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[8]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_9_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[9]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[9]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_10_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[10]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[10]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_11_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[11]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[11]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_12_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[12]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[12]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_13_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[13]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[13]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_14_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[14]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[14]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_15_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[15]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[15]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_16_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[16]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[16]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_17_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[17]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[17]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_18_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[18]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[18]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_19_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[19]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[19]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_20_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[20]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[20]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_21_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[21]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[21]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_22_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[22]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[22]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_23_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[23]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[23]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_24_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[24]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[24]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_25_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[25]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[25]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_26_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[26]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[26]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_27_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[27]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[27]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_28_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[28]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[28]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_29_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[29]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[29]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_30_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[30]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[30]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_31_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[31]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[31]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_32_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[32]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[32]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_33_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[33]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[33]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_34_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[34]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[34]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_35_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[35]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[35]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_36_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[36]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[36]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_37_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[37]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[37]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_38_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[38]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[38]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_39_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[39]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[39]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_40_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[40]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[40]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_41_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[41]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[41]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_42_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[42]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[42]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_43_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[43]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[43]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_44_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[44]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[44]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_45_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[45]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[45]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_46_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[46]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[46]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_47_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[47]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[47]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_48_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[48]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[48]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_49_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[49]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[49]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_50_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[50]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[50]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_51_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[51]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[51]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_52_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[52]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[52]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_53_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[53]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[53]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_54_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[54]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[54]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_55_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[55]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[55]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_56_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[56]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[56]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_57_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[57]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[57]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_58_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[58]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[58]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_59_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[59]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[59]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_60_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[60]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[60]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_61_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[61]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[61]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_62_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[62]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[62]) );
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0_63_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0[63]), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_1[63]) );
  assign cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_pass_2 = cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_din_q0;
  wire  fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_q0;
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_q0_lut ( .O(fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_q0), .I0(fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_2) );
  assign fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_pass_1 = fifo_cout_drain_cout_drain_IO_L2_out_0_V_V_full_n_q0;
  wire  cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_q0;
(* dont_touch = "yes" *) LUT1 #(.INIT(2'b10)) cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_q0_lut ( .O(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_q0), .I0(cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_1) );
  assign cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_pass_2 = cout_drain_IO_L2_out568_U0_fifo_cout_drain_out_V_V_write_q0;
wire [255:0] PE_wrapper165_U0_fifo_w_out_V_V_din;
assign PE_wrapper165_U0_fifo_w_out_V_V_din = PE_wrapper165_U0_fifo_w_out_V_V_din_pass_1;
wire  fifo_w_PE_1_4_V_V_full_n;
assign fifo_w_PE_1_4_V_V_full_n_pass_1 = fifo_w_PE_1_4_V_V_full_n;
wire  PE_wrapper165_U0_fifo_w_out_V_V_write;
assign PE_wrapper165_U0_fifo_w_out_V_V_write = PE_wrapper165_U0_fifo_w_out_V_V_write_pass_1;
wire [63:0] cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din;
assign cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din_pass_0 = cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din;
wire  fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n;
reg  fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_q_for_broadcast <= fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_pass_0;
assign fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n = fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n_q_for_broadcast;
wire  cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write;
assign cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write_pass_0 = cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write;
wire [255:0] cin_IO_L2_in127_U0_fifo_cin_out_V_V_din;
assign cin_IO_L2_in127_U0_fifo_cin_out_V_V_din = cin_IO_L2_in127_U0_fifo_cin_out_V_V_din_pass_1;
wire  fifo_cin_cin_IO_L2_in_4_V_V_full_n;
assign fifo_cin_cin_IO_L2_in_4_V_V_full_n_pass_1 = fifo_cin_cin_IO_L2_in_4_V_V_full_n;
wire  cin_IO_L2_in127_U0_fifo_cin_out_V_V_write;
assign cin_IO_L2_in127_U0_fifo_cin_out_V_V_write = cin_IO_L2_in127_U0_fifo_cin_out_V_V_write_pass_1;
wire [255:0] PE_wrapper179_U0_fifo_w_out_V_V_din;
assign PE_wrapper179_U0_fifo_w_out_V_V_din_pass_0 = PE_wrapper179_U0_fifo_w_out_V_V_din;
wire  fifo_w_PE_2_6_V_V_full_n;
reg  fifo_w_PE_2_6_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_w_PE_2_6_V_V_full_n_q_for_broadcast <= fifo_w_PE_2_6_V_V_full_n_pass_0;
assign fifo_w_PE_2_6_V_V_full_n = fifo_w_PE_2_6_V_V_full_n_q_for_broadcast;
wire  PE_wrapper179_U0_fifo_w_out_V_V_write;
assign PE_wrapper179_U0_fifo_w_out_V_V_write_pass_0 = PE_wrapper179_U0_fifo_w_out_V_V_write;
wire [255:0] cin_IO_L2_in128_U0_fifo_cin_out_V_V_din;
assign cin_IO_L2_in128_U0_fifo_cin_out_V_V_din_pass_0 = cin_IO_L2_in128_U0_fifo_cin_out_V_V_din;
wire  fifo_cin_cin_IO_L2_in_5_V_V_full_n;
reg  fifo_cin_cin_IO_L2_in_5_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_cin_cin_IO_L2_in_5_V_V_full_n_q_for_broadcast <= fifo_cin_cin_IO_L2_in_5_V_V_full_n_pass_0;
assign fifo_cin_cin_IO_L2_in_5_V_V_full_n = fifo_cin_cin_IO_L2_in_5_V_V_full_n_q_for_broadcast;
wire  cin_IO_L2_in128_U0_fifo_cin_out_V_V_write;
assign cin_IO_L2_in128_U0_fifo_cin_out_V_V_write_pass_0 = cin_IO_L2_in128_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper179_U0_fifo_cout_drain_out_V_din;
assign PE_wrapper179_U0_fifo_cout_drain_out_V_din_pass_0 = PE_wrapper179_U0_fifo_cout_drain_out_V_din;
wire  fifo_cout_drain_PE_2_5_V_full_n;
reg  fifo_cout_drain_PE_2_5_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_cout_drain_PE_2_5_V_full_n_q_for_broadcast <= fifo_cout_drain_PE_2_5_V_full_n_pass_0;
assign fifo_cout_drain_PE_2_5_V_full_n = fifo_cout_drain_PE_2_5_V_full_n_q_for_broadcast;
wire  PE_wrapper179_U0_fifo_cout_drain_out_V_write;
assign PE_wrapper179_U0_fifo_cout_drain_out_V_write_pass_0 = PE_wrapper179_U0_fifo_cout_drain_out_V_write;
wire [255:0] PE_wrapper177_U0_fifo_w_out_V_V_din;
assign PE_wrapper177_U0_fifo_w_out_V_V_din = PE_wrapper177_U0_fifo_w_out_V_V_din_pass_1;
wire  fifo_w_PE_2_4_V_V_full_n;
assign fifo_w_PE_2_4_V_V_full_n_pass_1 = fifo_w_PE_2_4_V_V_full_n;
wire  PE_wrapper177_U0_fifo_w_out_V_V_write;
assign PE_wrapper177_U0_fifo_w_out_V_V_write = PE_wrapper177_U0_fifo_w_out_V_V_write_pass_1;
wire [255:0] PE_wrapper153_U0_fifo_w_out_V_V_din;
assign PE_wrapper153_U0_fifo_w_out_V_V_din = PE_wrapper153_U0_fifo_w_out_V_V_din_pass_1;
wire  fifo_w_PE_0_4_V_V_full_n;
assign fifo_w_PE_0_4_V_V_full_n_pass_1 = fifo_w_PE_0_4_V_V_full_n;
wire  PE_wrapper153_U0_fifo_w_out_V_V_write;
assign PE_wrapper153_U0_fifo_w_out_V_V_write = PE_wrapper153_U0_fifo_w_out_V_V_write_pass_1;
wire [255:0] PE_wrapper190_U0_fifo_cin_out_V_V_din;
assign PE_wrapper190_U0_fifo_cin_out_V_V_din_pass_0 = PE_wrapper190_U0_fifo_cin_out_V_V_din;
wire  fifo_cin_PE_4_4_V_V_full_n;
reg  fifo_cin_PE_4_4_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_cin_PE_4_4_V_V_full_n_q_for_broadcast <= fifo_cin_PE_4_4_V_V_full_n_pass_0;
assign fifo_cin_PE_4_4_V_V_full_n = fifo_cin_PE_4_4_V_V_full_n_q_for_broadcast;
wire  PE_wrapper190_U0_fifo_cin_out_V_V_write;
assign PE_wrapper190_U0_fifo_cin_out_V_V_write_pass_0 = PE_wrapper190_U0_fifo_cin_out_V_V_write;
wire [255:0] PE_wrapper166_U0_fifo_w_out_V_V_din;
assign PE_wrapper166_U0_fifo_w_out_V_V_din_pass_0 = PE_wrapper166_U0_fifo_w_out_V_V_din;
wire  fifo_w_PE_1_5_V_V_full_n;
reg  fifo_w_PE_1_5_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_w_PE_1_5_V_V_full_n_q_for_broadcast <= fifo_w_PE_1_5_V_V_full_n_pass_0;
assign fifo_w_PE_1_5_V_V_full_n = fifo_w_PE_1_5_V_V_full_n_q_for_broadcast;
wire  PE_wrapper166_U0_fifo_w_out_V_V_write;
assign PE_wrapper166_U0_fifo_w_out_V_V_write_pass_0 = PE_wrapper166_U0_fifo_w_out_V_V_write;
wire [255:0] PE_wrapper154_U0_fifo_w_out_V_V_din;
assign PE_wrapper154_U0_fifo_w_out_V_V_din_pass_0 = PE_wrapper154_U0_fifo_w_out_V_V_din;
wire  fifo_w_PE_0_5_V_V_full_n;
reg  fifo_w_PE_0_5_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_w_PE_0_5_V_V_full_n_q_for_broadcast <= fifo_w_PE_0_5_V_V_full_n_pass_0;
assign fifo_w_PE_0_5_V_V_full_n = fifo_w_PE_0_5_V_V_full_n_q_for_broadcast;
wire  PE_wrapper154_U0_fifo_w_out_V_V_write;
assign PE_wrapper154_U0_fifo_w_out_V_V_write_pass_0 = PE_wrapper154_U0_fifo_w_out_V_V_write;
wire [63:0] cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din;
assign cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din = cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din_pass_0;
wire  fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n;
assign fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n_pass_0 = fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n;
wire  cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write;
assign cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write = cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write_pass_0;
wire [255:0] PE_wrapper190_U0_fifo_w_out_V_V_din;
assign PE_wrapper190_U0_fifo_w_out_V_V_din_pass_0 = PE_wrapper190_U0_fifo_w_out_V_V_din;
wire  fifo_w_PE_3_5_V_V_full_n;
reg  fifo_w_PE_3_5_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_w_PE_3_5_V_V_full_n_q_for_broadcast <= fifo_w_PE_3_5_V_V_full_n_pass_0;
assign fifo_w_PE_3_5_V_V_full_n = fifo_w_PE_3_5_V_V_full_n_q_for_broadcast;
wire  PE_wrapper190_U0_fifo_w_out_V_V_write;
assign PE_wrapper190_U0_fifo_w_out_V_V_write_pass_0 = PE_wrapper190_U0_fifo_w_out_V_V_write;
wire [255:0] PE_wrapper179_U0_fifo_cin_out_V_V_din;
assign PE_wrapper179_U0_fifo_cin_out_V_V_din_pass_0 = PE_wrapper179_U0_fifo_cin_out_V_V_din;
wire  fifo_cin_PE_3_5_V_V_full_n;
reg  fifo_cin_PE_3_5_V_V_full_n_q_for_broadcast;
always @ (posedge ap_clk) fifo_cin_PE_3_5_V_V_full_n_q_for_broadcast <= fifo_cin_PE_3_5_V_V_full_n_pass_0;
assign fifo_cin_PE_3_5_V_V_full_n = fifo_cin_PE_3_5_V_V_full_n_q_for_broadcast;
wire  PE_wrapper179_U0_fifo_cin_out_V_V_write;
assign PE_wrapper179_U0_fifo_cin_out_V_V_write_pass_0 = PE_wrapper179_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper202_U0_fifo_cout_drain_out_V_din;
assign PE_wrapper202_U0_fifo_cout_drain_out_V_din = PE_wrapper202_U0_fifo_cout_drain_out_V_din_pass_0;
wire  fifo_cout_drain_PE_4_4_V_full_n;
assign fifo_cout_drain_PE_4_4_V_full_n_pass_0 = fifo_cout_drain_PE_4_4_V_full_n;
wire  PE_wrapper202_U0_fifo_cout_drain_out_V_write;
assign PE_wrapper202_U0_fifo_cout_drain_out_V_write = PE_wrapper202_U0_fifo_cout_drain_out_V_write_pass_0;
wire [255:0] PE_wrapper189_U0_fifo_w_out_V_V_din;
assign PE_wrapper189_U0_fifo_w_out_V_V_din = PE_wrapper189_U0_fifo_w_out_V_V_din_pass_1;
wire  fifo_w_PE_3_4_V_V_full_n;
assign fifo_w_PE_3_4_V_V_full_n_pass_1 = fifo_w_PE_3_4_V_V_full_n;
wire  PE_wrapper189_U0_fifo_w_out_V_V_write;
assign PE_wrapper189_U0_fifo_w_out_V_V_write = PE_wrapper189_U0_fifo_w_out_V_V_write_pass_1;
wire [255:0] PE_wrapper167_U0_fifo_cin_out_V_V_din;
assign PE_wrapper167_U0_fifo_cin_out_V_V_din = PE_wrapper167_U0_fifo_cin_out_V_V_din_pass_0;
wire  fifo_cin_PE_2_5_V_V_full_n;
assign fifo_cin_PE_2_5_V_V_full_n_pass_0 = fifo_cin_PE_2_5_V_V_full_n;
wire  PE_wrapper167_U0_fifo_cin_out_V_V_write;
assign PE_wrapper167_U0_fifo_cin_out_V_V_write = PE_wrapper167_U0_fifo_cin_out_V_V_write_pass_0;
wire [63:0] cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din;
assign cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din = cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0;
wire  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n;
assign fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n_pass_0 = fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n;
wire  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write;
assign cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write = cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write_pass_0;


  (* dont_touch = "yes" *) CR_X6Y4_To_CR_X7Y5 CR_X6Y4_To_CR_X7Y5_U0 (
    .PE_wrapper165_U0_fifo_w_out_V_V_din(PE_wrapper165_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_1_4_V_V_full_n(fifo_w_PE_1_4_V_V_full_n),
    .PE_wrapper165_U0_fifo_w_out_V_V_write(PE_wrapper165_U0_fifo_w_out_V_V_write),
    .cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din),
    .fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n(fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n),
    .cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write),
    .cin_IO_L2_in127_U0_fifo_cin_out_V_V_din(cin_IO_L2_in127_U0_fifo_cin_out_V_V_din),
    .fifo_cin_cin_IO_L2_in_4_V_V_full_n(fifo_cin_cin_IO_L2_in_4_V_V_full_n),
    .cin_IO_L2_in127_U0_fifo_cin_out_V_V_write(cin_IO_L2_in127_U0_fifo_cin_out_V_V_write),
    .PE_wrapper179_U0_fifo_w_out_V_V_din(PE_wrapper179_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_2_6_V_V_full_n(fifo_w_PE_2_6_V_V_full_n),
    .PE_wrapper179_U0_fifo_w_out_V_V_write(PE_wrapper179_U0_fifo_w_out_V_V_write),
    .cin_IO_L2_in128_U0_fifo_cin_out_V_V_din(cin_IO_L2_in128_U0_fifo_cin_out_V_V_din),
    .fifo_cin_cin_IO_L2_in_5_V_V_full_n(fifo_cin_cin_IO_L2_in_5_V_V_full_n),
    .cin_IO_L2_in128_U0_fifo_cin_out_V_V_write(cin_IO_L2_in128_U0_fifo_cin_out_V_V_write),
    .PE_wrapper179_U0_fifo_cout_drain_out_V_din(PE_wrapper179_U0_fifo_cout_drain_out_V_din),
    .fifo_cout_drain_PE_2_5_V_full_n(fifo_cout_drain_PE_2_5_V_full_n),
    .PE_wrapper179_U0_fifo_cout_drain_out_V_write(PE_wrapper179_U0_fifo_cout_drain_out_V_write),
    .PE_wrapper177_U0_fifo_w_out_V_V_din(PE_wrapper177_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_2_4_V_V_full_n(fifo_w_PE_2_4_V_V_full_n),
    .PE_wrapper177_U0_fifo_w_out_V_V_write(PE_wrapper177_U0_fifo_w_out_V_V_write),
    .PE_wrapper153_U0_fifo_w_out_V_V_din(PE_wrapper153_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_0_4_V_V_full_n(fifo_w_PE_0_4_V_V_full_n),
    .PE_wrapper153_U0_fifo_w_out_V_V_write(PE_wrapper153_U0_fifo_w_out_V_V_write),
    .PE_wrapper190_U0_fifo_cin_out_V_V_din(PE_wrapper190_U0_fifo_cin_out_V_V_din),
    .fifo_cin_PE_4_4_V_V_full_n(fifo_cin_PE_4_4_V_V_full_n),
    .PE_wrapper190_U0_fifo_cin_out_V_V_write(PE_wrapper190_U0_fifo_cin_out_V_V_write),
    .PE_wrapper166_U0_fifo_w_out_V_V_din(PE_wrapper166_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_1_5_V_V_full_n(fifo_w_PE_1_5_V_V_full_n),
    .PE_wrapper166_U0_fifo_w_out_V_V_write(PE_wrapper166_U0_fifo_w_out_V_V_write),
    .PE_wrapper154_U0_fifo_w_out_V_V_din(PE_wrapper154_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_0_5_V_V_full_n(fifo_w_PE_0_5_V_V_full_n),
    .PE_wrapper154_U0_fifo_w_out_V_V_write(PE_wrapper154_U0_fifo_w_out_V_V_write),
    .cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din),
    .fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n),
    .cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write),
    .PE_wrapper190_U0_fifo_w_out_V_V_din(PE_wrapper190_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_3_5_V_V_full_n(fifo_w_PE_3_5_V_V_full_n),
    .PE_wrapper190_U0_fifo_w_out_V_V_write(PE_wrapper190_U0_fifo_w_out_V_V_write),
    .PE_wrapper179_U0_fifo_cin_out_V_V_din(PE_wrapper179_U0_fifo_cin_out_V_V_din),
    .fifo_cin_PE_3_5_V_V_full_n(fifo_cin_PE_3_5_V_V_full_n),
    .PE_wrapper179_U0_fifo_cin_out_V_V_write(PE_wrapper179_U0_fifo_cin_out_V_V_write),
    .PE_wrapper202_U0_fifo_cout_drain_out_V_din(PE_wrapper202_U0_fifo_cout_drain_out_V_din),
    .fifo_cout_drain_PE_4_4_V_full_n(fifo_cout_drain_PE_4_4_V_full_n),
    .PE_wrapper202_U0_fifo_cout_drain_out_V_write(PE_wrapper202_U0_fifo_cout_drain_out_V_write),
    .PE_wrapper189_U0_fifo_w_out_V_V_din(PE_wrapper189_U0_fifo_w_out_V_V_din),
    .fifo_w_PE_3_4_V_V_full_n(fifo_w_PE_3_4_V_V_full_n),
    .PE_wrapper189_U0_fifo_w_out_V_V_write(PE_wrapper189_U0_fifo_w_out_V_V_write),
    .PE_wrapper167_U0_fifo_cin_out_V_V_din(PE_wrapper167_U0_fifo_cin_out_V_V_din),
    .fifo_cin_PE_2_5_V_V_full_n(fifo_cin_PE_2_5_V_V_full_n),
    .PE_wrapper167_U0_fifo_cin_out_V_V_write(PE_wrapper167_U0_fifo_cin_out_V_V_write),
    .cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din),
    .fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n),
    .cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write),
    .ap_start(ap_start),
    .ap_done(ap_done),
    .ap_idle(ap_idle),
    .ap_ready(ap_ready),
    .ap_continue(ap_continue),
    .ap_clk(ap_clk),
    .ap_rst_n(ap_rst_n)
  );
endmodule


`timescale 1 ns / 1 ps
module CR_X6Y4_To_CR_X7Y5 (
  PE_wrapper165_U0_fifo_w_out_V_V_din,
  fifo_w_PE_1_4_V_V_full_n,
  PE_wrapper165_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n,
  cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write,
  cin_IO_L2_in127_U0_fifo_cin_out_V_V_din,
  fifo_cin_cin_IO_L2_in_4_V_V_full_n,
  cin_IO_L2_in127_U0_fifo_cin_out_V_V_write,
  PE_wrapper179_U0_fifo_w_out_V_V_din,
  fifo_w_PE_2_6_V_V_full_n,
  PE_wrapper179_U0_fifo_w_out_V_V_write,
  cin_IO_L2_in128_U0_fifo_cin_out_V_V_din,
  fifo_cin_cin_IO_L2_in_5_V_V_full_n,
  cin_IO_L2_in128_U0_fifo_cin_out_V_V_write,
  PE_wrapper179_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_2_5_V_full_n,
  PE_wrapper179_U0_fifo_cout_drain_out_V_write,
  PE_wrapper177_U0_fifo_w_out_V_V_din,
  fifo_w_PE_2_4_V_V_full_n,
  PE_wrapper177_U0_fifo_w_out_V_V_write,
  PE_wrapper153_U0_fifo_w_out_V_V_din,
  fifo_w_PE_0_4_V_V_full_n,
  PE_wrapper153_U0_fifo_w_out_V_V_write,
  PE_wrapper190_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_4_4_V_V_full_n,
  PE_wrapper190_U0_fifo_cin_out_V_V_write,
  PE_wrapper166_U0_fifo_w_out_V_V_din,
  fifo_w_PE_1_5_V_V_full_n,
  PE_wrapper166_U0_fifo_w_out_V_V_write,
  PE_wrapper154_U0_fifo_w_out_V_V_din,
  fifo_w_PE_0_5_V_V_full_n,
  PE_wrapper154_U0_fifo_w_out_V_V_write,
  cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n,
  cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write,
  PE_wrapper190_U0_fifo_w_out_V_V_din,
  fifo_w_PE_3_5_V_V_full_n,
  PE_wrapper190_U0_fifo_w_out_V_V_write,
  PE_wrapper179_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_3_5_V_V_full_n,
  PE_wrapper179_U0_fifo_cin_out_V_V_write,
  PE_wrapper202_U0_fifo_cout_drain_out_V_din,
  fifo_cout_drain_PE_4_4_V_full_n,
  PE_wrapper202_U0_fifo_cout_drain_out_V_write,
  PE_wrapper189_U0_fifo_w_out_V_V_din,
  fifo_w_PE_3_4_V_V_full_n,
  PE_wrapper189_U0_fifo_w_out_V_V_write,
  PE_wrapper167_U0_fifo_cin_out_V_V_din,
  fifo_cin_PE_2_5_V_V_full_n,
  PE_wrapper167_U0_fifo_cin_out_V_V_write,
  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din,
  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n,
  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write,
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
wire cin_IO_L2_in128_U0_ap_start;
wire cin_IO_L2_in128_U0_ap_done;
wire cin_IO_L2_in128_U0_ap_continue;
wire cin_IO_L2_in128_U0_ap_idle;
wire cin_IO_L2_in128_U0_ap_ready;
wire cin_IO_L2_in128_U0_fifo_cin_in_V_V_read;
wire [255:0] cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_din;
wire cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_write;
wire PE_wrapper154_U0_ap_start;
wire PE_wrapper154_U0_ap_done;
wire PE_wrapper154_U0_ap_continue;
wire PE_wrapper154_U0_ap_idle;
wire PE_wrapper154_U0_ap_ready;
wire PE_wrapper154_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper154_U0_fifo_cin_out_V_V_din;
wire PE_wrapper154_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper154_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper154_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper154_U0_fifo_w_in_V_V_read;
wire PE_wrapper166_U0_ap_start;
wire PE_wrapper166_U0_ap_done;
wire PE_wrapper166_U0_ap_continue;
wire PE_wrapper166_U0_ap_idle;
wire PE_wrapper166_U0_ap_ready;
wire PE_wrapper166_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper166_U0_fifo_cin_out_V_V_din;
wire PE_wrapper166_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper166_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper166_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper166_U0_fifo_w_in_V_V_read;
wire PE_wrapper178_U0_ap_start;
wire PE_wrapper178_U0_ap_done;
wire PE_wrapper178_U0_ap_continue;
wire PE_wrapper178_U0_ap_idle;
wire PE_wrapper178_U0_ap_ready;
wire PE_wrapper178_U0_fifo_cin_in_V_V_read;
wire [255:0] PE_wrapper178_U0_fifo_cin_out_V_V_din;
wire PE_wrapper178_U0_fifo_cin_out_V_V_write;
wire [31:0] PE_wrapper178_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper178_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper178_U0_fifo_w_in_V_V_read;
wire [255:0] PE_wrapper178_U0_fifo_w_out_V_V_din;
wire PE_wrapper178_U0_fifo_w_out_V_V_write;
wire PE_wrapper179_U0_ap_start;
wire PE_wrapper179_U0_ap_done;
wire PE_wrapper179_U0_ap_continue;
wire PE_wrapper179_U0_ap_idle;
wire PE_wrapper179_U0_ap_ready;
wire PE_wrapper179_U0_fifo_cin_in_V_V_read;
wire PE_wrapper179_U0_fifo_w_in_V_V_read;
wire PE_wrapper190_U0_ap_start;
wire PE_wrapper190_U0_ap_done;
wire PE_wrapper190_U0_ap_continue;
wire PE_wrapper190_U0_ap_idle;
wire PE_wrapper190_U0_ap_ready;
wire PE_wrapper190_U0_fifo_cin_in_V_V_read;
wire [31:0] PE_wrapper190_U0_fifo_cout_drain_out_V_din;
wire PE_wrapper190_U0_fifo_cout_drain_out_V_write;
wire PE_wrapper190_U0_fifo_w_in_V_V_read;
wire cout_drain_IO_L1_out_wrapper442_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper442_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper442_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper442_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper442_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper443_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper443_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper443_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper443_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper443_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper444_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper444_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper444_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper444_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper444_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper445_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper445_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper445_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper445_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper445_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L1_out_wrapper446_U0_ap_start;
wire cout_drain_IO_L1_out_wrapper446_U0_ap_done;
wire cout_drain_IO_L1_out_wrapper446_U0_ap_continue;
wire cout_drain_IO_L1_out_wrapper446_U0_ap_idle;
wire cout_drain_IO_L1_out_wrapper446_U0_ap_ready;
wire cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_in_V_V_read;
wire [63:0] cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_din;
wire cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_write;
wire cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_local_in_V_read;
wire cout_drain_IO_L2_out564_U0_ap_start;
wire cout_drain_IO_L2_out564_U0_ap_done;
wire cout_drain_IO_L2_out564_U0_ap_continue;
wire cout_drain_IO_L2_out564_U0_ap_idle;
wire cout_drain_IO_L2_out564_U0_ap_ready;
wire cout_drain_IO_L2_out564_U0_fifo_cout_drain_in_V_V_read;
wire cout_drain_IO_L2_out564_U0_fifo_cout_drain_local_in_V_V_read;
wire [255:0] fifo_cin_cin_IO_L2_in_4_V_V_dout;
wire fifo_cin_cin_IO_L2_in_4_V_V_empty_n;
wire fifo_cin_PE_0_4_V_V_full_n;
wire [255:0] fifo_cin_PE_0_4_V_V_dout;
wire fifo_cin_PE_0_4_V_V_empty_n;
wire [255:0] fifo_w_PE_0_4_V_V_dout;
wire fifo_w_PE_0_4_V_V_empty_n;
wire fifo_cin_PE_1_4_V_V_full_n;
wire [255:0] fifo_cin_PE_1_4_V_V_dout;
wire fifo_cin_PE_1_4_V_V_empty_n;
wire fifo_cout_drain_PE_0_4_V_full_n;
wire [31:0] fifo_cout_drain_PE_0_4_V_dout;
wire fifo_cout_drain_PE_0_4_V_empty_n;
wire [255:0] fifo_w_PE_1_4_V_V_dout;
wire fifo_w_PE_1_4_V_V_empty_n;
wire fifo_cin_PE_2_4_V_V_full_n;
wire [255:0] fifo_cin_PE_2_4_V_V_dout;
wire fifo_cin_PE_2_4_V_V_empty_n;
wire fifo_cout_drain_PE_1_4_V_full_n;
wire [31:0] fifo_cout_drain_PE_1_4_V_dout;
wire fifo_cout_drain_PE_1_4_V_empty_n;
wire [255:0] fifo_cin_PE_2_5_V_V_dout;
wire fifo_cin_PE_2_5_V_V_empty_n;
wire [255:0] fifo_w_PE_2_4_V_V_dout;
wire fifo_w_PE_2_4_V_V_empty_n;
wire fifo_cin_PE_3_4_V_V_full_n;
wire [255:0] fifo_cin_PE_3_4_V_V_dout;
wire fifo_cin_PE_3_4_V_V_empty_n;
wire fifo_cout_drain_PE_2_4_V_full_n;
wire [31:0] fifo_cout_drain_PE_2_4_V_dout;
wire fifo_cout_drain_PE_2_4_V_empty_n;
wire fifo_w_PE_2_5_V_V_full_n;
wire [255:0] fifo_w_PE_2_5_V_V_dout;
wire fifo_w_PE_2_5_V_V_empty_n;
wire [255:0] fifo_w_PE_3_4_V_V_dout;
wire fifo_w_PE_3_4_V_V_empty_n;
wire fifo_cout_drain_PE_3_4_V_full_n;
wire [31:0] fifo_cout_drain_PE_3_4_V_dout;
wire fifo_cout_drain_PE_3_4_V_empty_n;
wire [31:0] fifo_cout_drain_PE_4_4_V_dout;
wire fifo_cout_drain_PE_4_4_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_empty_n;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_full_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_empty_n;
wire [63:0] fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_dout;
wire fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_empty_n;
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
input [255:0] PE_wrapper165_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_1_4_V_V_full_n;
input  PE_wrapper165_U0_fifo_w_out_V_V_write;
output [63:0] cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din;
input  fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n;
output  cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write;
input [255:0] cin_IO_L2_in127_U0_fifo_cin_out_V_V_din;
output  fifo_cin_cin_IO_L2_in_4_V_V_full_n;
input  cin_IO_L2_in127_U0_fifo_cin_out_V_V_write;
output [255:0] PE_wrapper179_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_2_6_V_V_full_n;
output  PE_wrapper179_U0_fifo_w_out_V_V_write;
output [255:0] cin_IO_L2_in128_U0_fifo_cin_out_V_V_din;
input  fifo_cin_cin_IO_L2_in_5_V_V_full_n;
output  cin_IO_L2_in128_U0_fifo_cin_out_V_V_write;
output [31:0] PE_wrapper179_U0_fifo_cout_drain_out_V_din;
input  fifo_cout_drain_PE_2_5_V_full_n;
output  PE_wrapper179_U0_fifo_cout_drain_out_V_write;
input [255:0] PE_wrapper177_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_2_4_V_V_full_n;
input  PE_wrapper177_U0_fifo_w_out_V_V_write;
input [255:0] PE_wrapper153_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_0_4_V_V_full_n;
input  PE_wrapper153_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper190_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_4_4_V_V_full_n;
output  PE_wrapper190_U0_fifo_cin_out_V_V_write;
output [255:0] PE_wrapper166_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_1_5_V_V_full_n;
output  PE_wrapper166_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper154_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_0_5_V_V_full_n;
output  PE_wrapper154_U0_fifo_w_out_V_V_write;
input [63:0] cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n;
input  cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write;
output [255:0] PE_wrapper190_U0_fifo_w_out_V_V_din;
input  fifo_w_PE_3_5_V_V_full_n;
output  PE_wrapper190_U0_fifo_w_out_V_V_write;
output [255:0] PE_wrapper179_U0_fifo_cin_out_V_V_din;
input  fifo_cin_PE_3_5_V_V_full_n;
output  PE_wrapper179_U0_fifo_cin_out_V_V_write;
input [31:0] PE_wrapper202_U0_fifo_cout_drain_out_V_din;
output  fifo_cout_drain_PE_4_4_V_full_n;
input  PE_wrapper202_U0_fifo_cout_drain_out_V_write;
input [255:0] PE_wrapper189_U0_fifo_w_out_V_V_din;
output  fifo_w_PE_3_4_V_V_full_n;
input  PE_wrapper189_U0_fifo_w_out_V_V_write;
input [255:0] PE_wrapper167_U0_fifo_cin_out_V_V_din;
output  fifo_cin_PE_2_5_V_V_full_n;
input  PE_wrapper167_U0_fifo_cin_out_V_V_write;
input [63:0] cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din;
output  fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n;
input  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write;
input  ap_start;
output ap_done;
output ap_idle;
output ap_ready;
input  ap_continue;
input ap_clk;
input ap_rst_n;
(* keep_hierarchy = "yes" *)
kernel0_cin_IO_L2_in128
cin_IO_L2_in128_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cin_IO_L2_in128_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cin_IO_L2_in128_U0_ap_idle),
  .ap_ready(cin_IO_L2_in128_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_cin_IO_L2_in_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_cin_IO_L2_in_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(cin_IO_L2_in128_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(cin_IO_L2_in128_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_cin_IO_L2_in_5_V_V_full_n),
  .fifo_cin_out_V_V_write(cin_IO_L2_in128_U0_fifo_cin_out_V_V_write),
  .fifo_cin_local_out_V_V_din(cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_din),
  .fifo_cin_local_out_V_V_full_n(fifo_cin_PE_0_4_V_V_full_n),
  .fifo_cin_local_out_V_V_write(cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper154
PE_wrapper154_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper154_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper154_U0_ap_idle),
  .ap_ready(PE_wrapper154_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_0_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_0_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper154_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper154_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_1_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper154_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper154_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_0_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper154_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_0_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_0_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper154_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper154_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_0_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper154_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper166
PE_wrapper166_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper166_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper166_U0_ap_idle),
  .ap_ready(PE_wrapper166_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_1_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_1_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper166_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper166_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_2_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper166_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper166_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_1_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper166_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_1_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_1_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper166_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper166_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_1_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper166_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper178
PE_wrapper178_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper178_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper178_U0_ap_idle),
  .ap_ready(PE_wrapper178_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_2_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_2_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper178_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper178_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_3_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper178_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper178_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_2_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper178_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_2_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_2_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper178_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper178_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_2_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper178_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper179
PE_wrapper179_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper179_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper179_U0_ap_idle),
  .ap_ready(PE_wrapper179_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_2_5_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_2_5_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper179_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper179_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_3_5_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper179_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper179_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_2_5_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper179_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_2_5_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_2_5_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper179_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper179_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_2_6_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper179_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_PE_wrapper190
PE_wrapper190_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(PE_wrapper190_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(PE_wrapper190_U0_ap_idle),
  .ap_ready(PE_wrapper190_U0_ap_ready),
  .fifo_cin_in_V_V_dout(fifo_cin_PE_3_4_V_V_dout),
  .fifo_cin_in_V_V_empty_n(fifo_cin_PE_3_4_V_V_empty_n),
  .fifo_cin_in_V_V_read(PE_wrapper190_U0_fifo_cin_in_V_V_read),
  .fifo_cin_out_V_V_din(PE_wrapper190_U0_fifo_cin_out_V_V_din),
  .fifo_cin_out_V_V_full_n(fifo_cin_PE_4_4_V_V_full_n),
  .fifo_cin_out_V_V_write(PE_wrapper190_U0_fifo_cin_out_V_V_write),
  .fifo_cout_drain_out_V_din(PE_wrapper190_U0_fifo_cout_drain_out_V_din),
  .fifo_cout_drain_out_V_full_n(fifo_cout_drain_PE_3_4_V_full_n),
  .fifo_cout_drain_out_V_write(PE_wrapper190_U0_fifo_cout_drain_out_V_write),
  .fifo_w_in_V_V_dout(fifo_w_PE_3_4_V_V_dout),
  .fifo_w_in_V_V_empty_n(fifo_w_PE_3_4_V_V_empty_n),
  .fifo_w_in_V_V_read(PE_wrapper190_U0_fifo_w_in_V_V_read),
  .fifo_w_out_V_V_din(PE_wrapper190_U0_fifo_w_out_V_V_din),
  .fifo_w_out_V_V_full_n(fifo_w_PE_3_5_V_V_full_n),
  .fifo_w_out_V_V_write(PE_wrapper190_U0_fifo_w_out_V_V_write)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper442
cout_drain_IO_L1_out_wrapper442_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper442_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper442_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper442_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_4_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_4_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper443
cout_drain_IO_L1_out_wrapper443_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper443_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper443_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper443_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_3_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_3_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper444
cout_drain_IO_L1_out_wrapper444_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper444_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper444_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper444_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_2_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_2_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper445
cout_drain_IO_L1_out_wrapper445_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper445_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper445_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper445_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_1_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_1_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L1_out_wrapper446
cout_drain_IO_L1_out_wrapper446_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L1_out_wrapper446_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L1_out_wrapper446_U0_ap_idle),
  .ap_ready(cout_drain_IO_L1_out_wrapper446_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_dout(fifo_cout_drain_PE_0_4_V_dout),
  .fifo_cout_drain_local_in_V_empty_n(fifo_cout_drain_PE_0_4_V_empty_n),
  .fifo_cout_drain_local_in_V_read(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
kernel0_cout_drain_IO_L2_out564
cout_drain_IO_L2_out564_U0
(
  .ap_clk(ap_clk),
  .ap_rst(ap_rst_pipe),
  .ap_start(ap_start_pipe),
  .ap_done(cout_drain_IO_L2_out564_U0_ap_done),
  .ap_continue(1'b1),
  .ap_idle(cout_drain_IO_L2_out564_U0_ap_idle),
  .ap_ready(cout_drain_IO_L2_out564_U0_ap_ready),
  .fifo_cout_drain_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_dout),
  .fifo_cout_drain_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_empty_n),
  .fifo_cout_drain_in_V_V_read(cout_drain_IO_L2_out564_U0_fifo_cout_drain_in_V_V_read),
  .fifo_cout_drain_out_V_V_din(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_din),
  .fifo_cout_drain_out_V_V_full_n(fifo_cout_drain_cout_drain_IO_L2_out_4_V_V_full_n),
  .fifo_cout_drain_out_V_V_write(cout_drain_IO_L2_out564_U0_fifo_cout_drain_out_V_V_write),
  .fifo_cout_drain_local_in_V_V_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_dout),
  .fifo_cout_drain_local_in_V_V_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_empty_n),
  .fifo_cout_drain_local_in_V_V_read(cout_drain_IO_L2_out564_U0_fifo_cout_drain_local_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_w_PE_2_5_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper178_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_2_5_V_V_full_n),
  .if_write(PE_wrapper178_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_2_5_V_V_dout),
  .if_empty_n(fifo_w_PE_2_5_V_V_empty_n),
  .if_read(PE_wrapper179_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_4_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(59),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_1_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper166_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_1_4_V_full_n),
  .if_write(PE_wrapper166_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_1_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_1_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_1_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper154_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_1_4_V_V_full_n),
  .if_write(PE_wrapper154_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_1_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_1_4_V_V_empty_n),
  .if_read(PE_wrapper166_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(55),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_2_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper178_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_2_4_V_full_n),
  .if_write(PE_wrapper178_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_2_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_2_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(37),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_0_V_V_empty_n),
  .if_read(cout_drain_IO_L2_out564_U0_fifo_cout_drain_local_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(53),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_3_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper190_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_3_4_V_full_n),
  .if_write(PE_wrapper190_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_3_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_3_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_3_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper178_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_3_4_V_V_full_n),
  .if_write(PE_wrapper178_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_3_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_3_4_V_V_empty_n),
  .if_read(PE_wrapper190_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(61),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_PE_0_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper154_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_0_4_V_full_n),
  .if_write(PE_wrapper154_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_0_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_0_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(3),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_0_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_din),
  .if_full_n(fifo_cin_PE_0_4_V_V_full_n),
  .if_write(cin_IO_L2_in128_U0_fifo_cin_local_out_V_V_write),
  .if_dout(fifo_cin_PE_0_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_0_4_V_V_empty_n),
  .if_read(PE_wrapper154_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper443_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_3_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(1)
)
fifo_cin_PE_2_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper166_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_2_4_V_V_full_n),
  .if_write(PE_wrapper166_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_2_4_V_V_dout),
  .if_empty_n(fifo_cin_PE_2_4_V_V_empty_n),
  .if_read(PE_wrapper178_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper444_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_2_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(3),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(1)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper445_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_1_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper446_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_w_PE_1_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper165_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_1_4_V_V_full_n),
  .if_write(PE_wrapper165_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_1_4_V_V_dout),
  .if_empty_n(fifo_w_PE_1_4_V_V_empty_n),
  .if_read(PE_wrapper166_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_cin_cin_IO_L2_in_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cin_IO_L2_in127_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_cin_IO_L2_in_4_V_V_full_n),
  .if_write(cin_IO_L2_in127_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_cin_IO_L2_in_4_V_V_dout),
  .if_empty_n(fifo_cin_cin_IO_L2_in_4_V_V_empty_n),
  .if_read(cin_IO_L2_in128_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_w_PE_2_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper177_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_2_4_V_V_full_n),
  .if_write(PE_wrapper177_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_2_4_V_V_dout),
  .if_empty_n(fifo_w_PE_2_4_V_V_empty_n),
  .if_read(PE_wrapper178_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_w_PE_0_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper153_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_0_4_V_V_full_n),
  .if_write(PE_wrapper153_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_0_4_V_V_dout),
  .if_empty_n(fifo_w_PE_0_4_V_V_empty_n),
  .if_read(PE_wrapper154_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(4),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_full_n),
  .if_write(cout_drain_IO_L2_out563_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L2_out_5_V_V_empty_n),
  .if_read(cout_drain_IO_L2_out564_U0_fifo_cout_drain_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(32),
  .DEPTH(48),
  .ADDR_WIDTH(6),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_PE_4_4_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper202_U0_fifo_cout_drain_out_V_din),
  .if_full_n(fifo_cout_drain_PE_4_4_V_full_n),
  .if_write(PE_wrapper202_U0_fifo_cout_drain_out_V_write),
  .if_dout(fifo_cout_drain_PE_4_4_V_dout),
  .if_empty_n(fifo_cout_drain_PE_4_4_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_local_in_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(5),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(5)
)
fifo_w_PE_3_4_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper189_U0_fifo_w_out_V_V_din),
  .if_full_n(fifo_w_PE_3_4_V_V_full_n),
  .if_write(PE_wrapper189_U0_fifo_w_out_V_V_write),
  .if_dout(fifo_w_PE_3_4_V_V_dout),
  .if_empty_n(fifo_w_PE_3_4_V_V_empty_n),
  .if_read(PE_wrapper190_U0_fifo_w_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(256),
  .DEPTH(4),
  .ADDR_WIDTH(9),
  .GRACE_PERIOD(3)
)
fifo_cin_PE_2_5_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(PE_wrapper167_U0_fifo_cin_out_V_V_din),
  .if_full_n(fifo_cin_PE_2_5_V_V_full_n),
  .if_write(PE_wrapper167_U0_fifo_cin_out_V_V_write),
  .if_dout(fifo_cin_PE_2_5_V_V_dout),
  .if_empty_n(fifo_cin_PE_2_5_V_V_empty_n),
  .if_read(PE_wrapper179_U0_fifo_cin_in_V_V_read)
);

(* keep_hierarchy = "yes" *)
fifo_almost_full
#(
  .DATA_WIDTH(64),
  .DEPTH(4),
  .ADDR_WIDTH(7),
  .GRACE_PERIOD(3)
)
fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_U
(
  .clk(ap_clk),
  .reset(ap_rst_n_inv),
  .if_read_ce(1'b1),
  .if_write_ce(1'b1),
  .if_din(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din),
  .if_full_n(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_full_n),
  .if_write(cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_write),
  .if_dout(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_dout),
  .if_empty_n(fifo_cout_drain_cout_drain_IO_L1_out_4_5_V_V_empty_n),
  .if_read(cout_drain_IO_L1_out_wrapper442_U0_fifo_cout_drain_in_V_V_read)
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

