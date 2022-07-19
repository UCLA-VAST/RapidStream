# Assume:
# 1. Use half-SLR islands
# 2. Use <4 HBM channels, from 28 to 31
# 3. Platform xilinx_u280_xdma_201920_3
set kernel_name "gaussian_kernel"
delete_pblocks anchor_region
delete_pblocks CR*

# anchor region
create_pblock anchor_region
resize_pblock anchor_region -add { SLICE_X115Y0:SLICE_X119Y719 }
resize_pblock anchor_region -add { LAGUNA_X0Y0:LAGUNA_X25Y479}
# include the SLICE right next to the laguna columns
resize_pblock anchor_region -add {
  SLICE_X9Y180:SLICE_X9Y299 SLICE_X9Y420:SLICE_X9Y539
  SLICE_X20Y180:SLICE_X20Y299 SLICE_X20Y420:SLICE_X20Y539
  SLICE_X38Y180:SLICE_X38Y299 SLICE_X38Y420:SLICE_X38Y539
  SLICE_X51Y180:SLICE_X51Y299 SLICE_X51Y420:SLICE_X51Y539
  SLICE_X64Y180:SLICE_X64Y299 SLICE_X64Y420:SLICE_X64Y539
  SLICE_X86Y180:SLICE_X86Y299 SLICE_X86Y420:SLICE_X86Y539
  SLICE_X98Y180:SLICE_X98Y299 SLICE_X98Y420:SLICE_X98Y539
  SLICE_X112Y180:SLICE_X112Y299 SLICE_X112Y420:SLICE_X112Y539
  SLICE_X125Y180:SLICE_X125Y299 SLICE_X125Y420:SLICE_X125Y539
  SLICE_X140Y180:SLICE_X140Y299 SLICE_X140Y420:SLICE_X140Y539
  SLICE_X153Y180:SLICE_X153Y299 SLICE_X153Y420:SLICE_X153Y539
  SLICE_X165Y180:SLICE_X165Y299 SLICE_X165Y420:SLICE_X165Y539
  SLICE_X183Y180:SLICE_X183Y299 SLICE_X183Y420:SLICE_X183Y539
}
# some SLICE nearby the IO columns are not included in the dynamic region
resize_pblock anchor_region -remove {SLICE_X117Y600:SLICE_X117Y719 SLICE_X117Y480:SLICE_X117Y539 SLICE_X117Y180:SLICE_X117Y239}
set_property parent pblock_dynamic_region [get_pblocks anchor_region]
set_property EXCLUDE_PLACEMENT 1 [get_pblocks anchor_region]

# define the island pblocks
create_pblock CR_X0Y8_To_CR_X3Y11
resize_pblock CR_X0Y8_To_CR_X3Y11 -add {CLOCKREGION_X0Y8:CLOCKREGION_X3Y11}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y8_To_CR_X3Y11]

create_pblock CR_X0Y4_To_CR_X3Y7
resize_pblock CR_X0Y4_To_CR_X3Y7 -add {CLOCKREGION_X0Y4:CLOCKREGION_X3Y7}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y4_To_CR_X3Y7]

create_pblock CR_X0Y0_To_CR_X3Y3
resize_pblock CR_X0Y0_To_CR_X3Y3 -add {CLOCKREGION_X0Y0:CLOCKREGION_X3Y3}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y0_To_CR_X3Y3]

# leave a 1-CR column gap for hmss
create_pblock CR_X4Y0_To_CR_X7Y3
resize_pblock CR_X4Y0_To_CR_X7Y3 -add {CLOCKREGION_X4Y0:CLOCKREGION_X5Y3}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y0_To_CR_X7Y3]

create_pblock CR_X4Y4_To_CR_X7Y7
resize_pblock CR_X4Y4_To_CR_X7Y7 -add {CLOCKREGION_X4Y4:CLOCKREGION_X5Y7}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y4_To_CR_X7Y7]

create_pblock CR_X4Y8_To_CR_X7Y11
resize_pblock CR_X4Y8_To_CR_X7Y11 -add {CLOCKREGION_X4Y8:CLOCKREGION_X5Y11}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y8_To_CR_X7Y11]

set island_pblocks {
  CR_X0Y8_To_CR_X3Y11
  CR_X0Y4_To_CR_X3Y7
  CR_X0Y0_To_CR_X3Y3
  CR_X4Y0_To_CR_X7Y3
  CR_X4Y4_To_CR_X7Y7
  CR_X4Y8_To_CR_X7Y11
}

foreach island $island_pblocks {
  # exclude the anchor regions from the island pblocks
  resize_pblock ${island} -remove [get_property DERIVED_RANGES [get_pblocks anchor_region]]
  resize_pblock ${island} -remove [get_property DERIVED_RANGES [get_pblocks base_region]]

  # reserve the the bottom row of CR for HMSS
  resize_pblock ${island} -remove {CLOCKREGION_X0Y0:CLOCKREGION_X7Y0}
}

# somehow these speical blocks will be left out of the island pblock
# as a result, the adjacent SLICE columns are also left out if we do not add them back
resize_pblock CR_X0Y0_To_CR_X3Y3 -add {CMACE4_X0Y0:CMACE4_X0Y1 PCIE4CE4_X0Y1:PCIE4CE4_X0Y1}
resize_pblock CR_X0Y4_To_CR_X3Y7 -add {CMACE4_X0Y2:CMACE4_X0Y4 ILKNE4_X0Y0:ILKNE4_X0Y0}
resize_pblock CR_X0Y8_To_CR_X3Y11 -add {CMACE4_X0Y5:CMACE4_X0Y7 ILKNE4_X0Y2:ILKNE4_X0Y2}

# assign island to pblocks
set base_addr pfm_top_i/dynamic_region/${kernel_name}/inst
add_cells_to_pblock anchor_region [get_cells ${base_addr}] -clear_locs
add_cells_to_pblock CR_X4Y0_To_CR_X7Y3  [get_cells ${base_addr}/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3] -clear_locs
add_cells_to_pblock CR_X0Y0_To_CR_X3Y3  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3] -clear_locs
add_cells_to_pblock CR_X0Y4_To_CR_X3Y7  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7] -clear_locs
add_cells_to_pblock CR_X0Y8_To_CR_X3Y11 [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11] -clear_locs
add_cells_to_pblock CR_X4Y4_To_CR_X7Y7  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7] -clear_locs
add_cells_to_pblock CR_X4Y8_To_CR_X7Y11 [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11] -clear_locs
