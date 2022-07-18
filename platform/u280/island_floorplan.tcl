# Assume:
# 1. Use half-SLR islands
# 2. Use <4 HBM channels, from 28 to 31
# 3. Platform xilinx_u280_xdma_201920_3

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
resize_pblock CR_X0Y8_To_CR_X3Y11 -add {SLICE_X0Y480:SLICE_X116Y719 DSP48E2_X0Y186:DSP48E2_X15Y281 RAMB18_X0Y192:RAMB18_X7Y287 RAMB36_X0Y96:RAMB36_X7Y143 URAM288_X0Y128:URAM288_X1Y191}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y8_To_CR_X3Y11]

create_pblock CR_X0Y4_To_CR_X3Y7
resize_pblock CR_X0Y4_To_CR_X3Y7 -add {SLICE_X0Y240:SLICE_X116Y479 DSP48E2_X0Y90:DSP48E2_X15Y185 RAMB18_X0Y96:RAMB18_X7Y191 RAMB36_X0Y48:RAMB36_X7Y95 URAM288_X0Y64:URAM288_X1Y127}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y4_To_CR_X3Y7]

create_pblock CR_X0Y0_To_CR_X3Y3
resize_pblock CR_X0Y0_To_CR_X3Y3 -add {SLICE_X0Y0:SLICE_X116Y239 DSP48E2_X0Y0:DSP48E2_X15Y89 RAMB18_X0Y0:RAMB18_X7Y95 RAMB36_X0Y0:RAMB36_X7Y47 URAM288_X0Y0:URAM288_X1Y63}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y0_To_CR_X3Y3]

create_pblock CR_X4Y0_To_CR_X7Y3
resize_pblock CR_X4Y0_To_CR_X7Y3 -add {SLICE_X117Y0:SLICE_X179Y239 DSP48E2_X16Y0:DSP48E2_X24Y89 RAMB18_X8Y0:RAMB18_X11Y95 RAMB36_X8Y0:RAMB36_X11Y47 URAM288_X2Y0:URAM288_X3Y63}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y0_To_CR_X7Y3]

create_pblock CR_X4Y4_To_CR_X7Y7
resize_pblock CR_X4Y4_To_CR_X7Y7 -add {SLICE_X117Y240:SLICE_X179Y479 DSP48E2_X16Y90:DSP48E2_X24Y185 RAMB18_X8Y96:RAMB18_X11Y191 RAMB36_X8Y48:RAMB36_X11Y95 URAM288_X2Y64:URAM288_X3Y127}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y4_To_CR_X7Y7]

create_pblock CR_X4Y8_To_CR_X7Y11
resize_pblock CR_X4Y8_To_CR_X7Y11 -add {SLICE_X117Y480:SLICE_X186Y719 DSP48E2_X16Y186:DSP48E2_X25Y281 RAMB18_X8Y192:RAMB18_X11Y287 RAMB36_X8Y96:RAMB36_X11Y143 URAM288_X2Y128:URAM288_X4Y191}
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

  # some SLICE nearby the IO columns are not included in the dynamic region
  resize_pblock ${island} -remove {SLICE_X117Y600:SLICE_X117Y719 SLICE_X117Y480:SLICE_X117Y539 SLICE_X117Y180:SLICE_X117Y239}

  # reserve area for HMSS
  resize_pblock ${island} -remove {SLICE_X0Y0:SLICE_X232Y29 RAMB36_X0Y0:RAMB36_X13Y0}
}

# assign island to pblocks
set base_addr pfm_top_i/dynamic_region/*/inst
add_cells_to_pblock anchor_region [get_cells ${base_addr}] -clear_locs
add_cells_to_pblock CR_X4Y0_To_CR_X7Y3  [get_cells ${base_addr}/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3] -clear_locs
add_cells_to_pblock CR_X0Y0_To_CR_X3Y3  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3] -clear_locs
add_cells_to_pblock CR_X0Y4_To_CR_X3Y7  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7] -clear_locs
add_cells_to_pblock CR_X0Y8_To_CR_X3Y11 [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11] -clear_locs
add_cells_to_pblock CR_X4Y4_To_CR_X7Y7  [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7] -clear_locs
add_cells_to_pblock CR_X4Y8_To_CR_X7Y11 [get_cells ${base_addr}/WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11] -clear_locs
