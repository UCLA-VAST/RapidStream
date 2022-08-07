# Assume:
# 1. Use half-SLR islands
# 2. Use <4 HBM channels, from 28 to 31
# 3. Platform xilinx_u280_xdma_201920_3
set kernel_name "gaussian_kernel"

delete_pblocks kernel_pblock
delete_pblocks hmss_pblock
delete_pblocks CR*

# first constraint both user and hmss stuff to hmss_pblock
create_pblock hmss_pblock
resize_pblock hmss_pblock -add {
  URAM288_X4Y0:URAM288_X4Y15 URAM288_X0Y0:URAM288_X3Y3 RAMB36_X11Y0:RAMB36_X13Y11 RAMB36_X0Y0:RAMB36_X10Y2 RAMB18_X11Y0:RAMB18_X13Y23 RAMB18_X0Y0:RAMB18_X10Y5 PCIE4CE4_X1Y0:PCIE4CE4_X1Y0 LAGUNA_X26Y0:LAGUNA_X27Y479 DSP48E2_X30Y0:DSP48E2_X31Y17 DSP48E2_X29Y0:DSP48E2_X29Y281 DSP48E2_X28Y162:DSP48E2_X28Y209 DSP48E2_X28Y0:DSP48E2_X28Y113 DSP48E2_X25Y0:DSP48E2_X27Y17 BLI_HBM_AXI_INTF_X0Y0:BLI_HBM_AXI_INTF_X31Y0 BLI_HBM_APB_INTF_X0Y0:BLI_HBM_APB_INTF_X31Y0 SLICE_X206Y0:SLICE_X232Y59 SLICE_X201Y0:SLICE_X205Y719 SLICE_X199Y0:SLICE_X200Y539 SLICE_X195Y420:SLICE_X198Y539 SLICE_X195Y0:SLICE_X198Y299 SLICE_X194Y0:SLICE_X194Y179 SLICE_X192Y420:SLICE_X193Y539 SLICE_X192Y0:SLICE_X193Y299 SLICE_X176Y0:SLICE_X191Y59 SLICE_X0Y0:SLICE_X175Y14
}
resize_pblock hmss_pblock -remove [get_property DERIVED_RANGES [get_pblocks base_region]]
# a corner case, this column does not belong to pblock_dynamic_region
resize_pblock hmss_pblock -remove {SLICE_X232Y0:SLICE_X232Y59}

set_property IS_SOFT false [get_pblocks hmss_pblock]
set_property parent pblock_dynamic_region [get_pblocks hmss_pblock]
add_cells_to_pblock hmss_pblock [get_cells pfm_top_i/dynamic_region/hmss_0]

# kernel pblock, use (dynamic_region_pblock - hmss_pblock)
create_pblock kernel_pblock
resize_pblock kernel_pblock -add [get_property DERIVED_RANGES [get_pblocks pblock_dynamic_region]]
resize_pblock kernel_pblock -remove [get_property DERIVED_RANGES [get_pblocks hmss_pblock]]
resize_pblock kernel_pblock -remove [get_property DERIVED_RANGES [get_pblocks base_region]]
set_property EXCLUDE_PLACEMENT true [get_pblocks kernel_pblock]
set_property CONTAIN_ROUTING true [get_pblocks kernel_pblock]
set_property IS_SOFT false [get_pblocks kernel_pblock]
set_property parent pblock_dynamic_region [get_pblocks kernel_pblock]
add_cells_to_pblock kernel_pblock [get_cells pfm_top_i/dynamic_region/${kernel_name}/inst]
# remove some disconnected pblocks that fall into the static region
resize_pblock kernel_pblock -remove_rect {582 715 710 715}
resize_pblock kernel_pblock -remove_rect {692 125 703 185}
