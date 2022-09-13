

#---------------------------
# Constant blocks
#---------------------------

#---------------------------
# Platform Parameters for xilinx_u280_xdma_201920_3
#---------------------------
set slr0_interconnect_axilite_user_slr0 [get_bd_cell /slr0/interconnect_axilite_user_slr0]
    
set_property -dict [ list \
  CONFIG.NUM_SI 1 \
  CONFIG.NUM_MI 2 \
  CONFIG.M01_HAS_REGSLICE 1 \
  ] $slr0_interconnect_axilite_user_slr0
set slr1_interconnect_axilite_user_slr1 [get_bd_cell /slr1/interconnect_axilite_user_slr1]
    
set_property -dict [ list \
  CONFIG.NUM_SI 1 \
  CONFIG.NUM_MI 3 \
  ] $slr1_interconnect_axilite_user_slr1
set slr2_interconnect_axilite_user_slr2 [get_bd_cell /slr2/interconnect_axilite_user_slr2]
    
set_property -dict [ list \
  CONFIG.NUM_SI 1 \
  CONFIG.NUM_MI 1 \
  ] $slr2_interconnect_axilite_user_slr2

#---------------------------
# Instantiating gaussian_kernel
#---------------------------
set gaussian_kernel [create_bd_cell -type ip -vlnv haoda:xrtl:gaussian_kernel:1.0 gaussian_kernel]
  

#---------------------------
# Connectivity Phase 1
#---------------------------
connect_bd_intf_net \
  [get_bd_intf_pins -auto_enable /slr0/interconnect_axilite_user_slr0/M01_AXI] \
  [get_bd_intf_pins -auto_enable /gaussian_kernel/s_axi_control] \

connect_bd_net  \
  [get_bd_pins -auto_enable /clkwiz_kernel_clk_out1] \
  [get_bd_pins -auto_enable /slr0/interconnect_axilite_user_slr0/M01_ACLK] \
  [get_bd_pins -auto_enable /gaussian_kernel/ap_clk] \

connect_bd_net  \
  [get_bd_pins -auto_enable /slr0/expanded_region_resets_slr0/psreset_gate_pr_kernel/interconnect_aresetn] \
  [get_bd_pins -auto_enable /slr0/interconnect_axilite_user_slr0/M01_ARESETN] \

connect_bd_net  \
  [get_bd_pins -auto_enable /slr0/expanded_region_resets_slr0/psreset_gate_pr_kernel/peripheral_aresetn] \
  [get_bd_pins -auto_enable /gaussian_kernel/ap_rst_n] \


#---------------------------
# Connectivity Phase 2
#---------------------------
hbm_memory_subsystem::map_memory_resource \
  [get_bd_intf_pins -auto_enable /gaussian_kernel/m_axi_bank_0_output] \
  [get_bd_cells /hmss_0] [list HBM_MEM29]

hbm_memory_subsystem::map_memory_resource \
  [get_bd_intf_pins -auto_enable /gaussian_kernel/m_axi_bank_1_output] \
  [get_bd_cells /hmss_0] [list HBM_MEM31]

hbm_memory_subsystem::map_memory_resource \
  [get_bd_intf_pins -auto_enable /gaussian_kernel/m_axi_bank_0_input] \
  [get_bd_cells /hmss_0] [list HBM_MEM28]

hbm_memory_subsystem::map_memory_resource \
  [get_bd_intf_pins -auto_enable /gaussian_kernel/m_axi_bank_1_input] \
  [get_bd_cells /hmss_0] [list HBM_MEM30]


#---------------------------
# Create Stream Map file
#---------------------------
set stream_subsystems [get_bd_cells * -hierarchical -quiet -filter {VLNV =~ "*:*:sdx_stream_subsystem:*"}]
if {[string length $stream_subsystems] > 0} {    
  set xmlFile $vpl_output_dir/qdma_stream_map.xml
  set fp [open ${xmlFile} w]
  puts $fp "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
  puts $fp "<xd:streamMap xmlns:xd=\"http://www.xilinx.com/xd\">"
  foreach streamSS [get_bd_cells * -hierarchical -quiet -filter {VLNV =~ "*:*:sdx_stream_subsystem:*"}] {
    set ssInstance [string trimleft $streamSS /]
    set ssRegion [get_property CONFIG.SLR_ASSIGNMENTS $streamSS]
    foreach ssIntf [get_bd_intf_pins $streamSS/* -quiet -filter {NAME=~"S??_AXIS"}] {
      set pinName [get_property NAME $ssIntf]
      set routeId [sdx_stream_subsystem::get_routeid $ssIntf]
      set flowId [sdx_stream_subsystem::get_flowid $ssIntf]
      puts $fp "  <xd:streamRoute xd:instanceRef=\"$ssInstance\" xd:portRef=\"$pinName\" xd:route=\"$routeId\" xd:flow=\"$flowId\" xd:region=\"$ssRegion\">"
      foreach connection [find_bd_objs -relation connected_to $ssIntf -thru_hier] {
        set connectedRegion [get_property CONFIG.SLR_ASSIGNMENTS [bd::utils::get_parent $connection]]
        set connectedPort [bd::utils::get_short_name $connection]
        set connectedInst [string trimleft [bd::utils::get_parent $connection] /]
        puts $fp "    <xd:connection xd:instanceRef=\"$connectedInst\" xd:portRef=\"$connectedPort\" xd:region=\"$connectedRegion\"/>"
      }
      puts $fp "  </xd:streamRoute>"
    }
    foreach ssIntf [get_bd_intf_pins $streamSS/* -quiet -filter {NAME=~"M??_AXIS"}] {
      set pinName [get_property NAME $ssIntf]
      set routeId [sdx_stream_subsystem::get_routeid $ssIntf]
      set flowId [sdx_stream_subsystem::get_flowid $ssIntf]
      puts $fp "  <xd:streamRoute xd:instanceRef=\"$ssInstance\" xd:portRef=\"$pinName\" xd:route=\"$routeId\" xd:flow=\"$flowId\" xd:region=\"$ssRegion\">"
      foreach connection [find_bd_objs -relation connected_to $ssIntf -thru_hier] {
        set connectedRegion [get_property CONFIG.SLR_ASSIGNMENTS [bd::utils::get_parent $connection]]
        set connectedPort [bd::utils::get_short_name $connection]
        set connectedInst [string trimleft [bd::utils::get_parent $connection] /]
        puts $fp "    <xd:connection xd:instanceRef=\"$connectedInst\" xd:portRef=\"$connectedPort\" xd:region=\"$connectedRegion\"/>"
      }
      puts $fp "  </xd:streamRoute>"
    }
  }
  puts $fp "</xd:streamMap>"
  close $fp
}

