# when we subdivide the user DFX region, the bottom left island is directly connected to the HMSS
# however, the logical hierarchy is changed
# previous logical hierarchy:  HMSS | user region
# current logical hierarchy: HMSS | anchor region | island
# previously the partition pins are set on the ports of the user region black box
# now they should be moved to the ports of the island

set inst_pins [
  get_pins -hierarchical -filter { PARENT_CELL =~  "pfm_top_i/dynamic_region/gaussian_kernel/inst" && HD.ASSIGNED_PPLOCS != "" }
]

foreach pin ${inst_pins} {
  set inner_pin [get_pins [string map {"inst/" "inst/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3/" } $pin] ];

  set pp_loc [get_property HD.ASSIGNED_PPLOCS ${pin}];

  # remove the previous partition pin
  reset_property HD.PARTPIN_LOCS ${pin}

  # set the partition pin on the inner logical hierarchy
  if { ${inner_pin} != "" } {
    reset_property HD.PARTPIN_LOCS ${inner_pin}
    set_property HD.PARTPIN_LOCS ${pp_loc} ${inner_pin}
  }
}
