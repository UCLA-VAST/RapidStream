# for HMSS overlay v3, directly place the cells inside the dummy islands
# use a brute force way to assign the cells one by one to the middle region
# skip invoking place_design during overlay construction
# then we use RWRoute to route from the anchors to the dummy FFs and we choose a partition pin as close
# to the boundary as possible

unplace_cell [get_cells pfm_top_i/dynamic_region/gaussian_kernel/inst/*WRAPPER*/*anchor_reg* ]

# place all place holder FFs in these clock regions
set island_to_free_site_range [dict create \
  CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3 {X5Y1 X5Y2} \
  WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3  {X1Y1 X2Y1} \
  WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7  {X1Y5 X1Y6} \
  WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7  {X5Y5 X5Y6} \
  WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11  {X5Y9 X5Y10} \
  WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11  {X1Y9 X1Y10} \
]

set islands {
  CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3
  WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3
  WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7
  WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7
  WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11
  WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11
}

set cell_to_loc []
foreach island $islands {
  set target_cells [ get_cells pfm_top_i/dynamic_region/gaussian_kernel/inst/${island}/* -filter { ( STATUS == UNPLACED || STATUS == ASSIGNED) && PRIMITIVE_TYPE !~ OTHERS.*.* } ]
  set cell_num [llength $target_cells]

  # for the CTRL wrapper with top IOs, allow each slice to hold 4 FFs
  if {$island == "CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3" } {
    set ANCHOR_PER_SLICE 4
  } else {
    set ANCHOR_PER_SLICE 2
  }
  set group_num [expr ${cell_num} / ${ANCHOR_PER_SLICE}]
  set free_sites_range [dict get $island_to_free_site_range $island]
  set free_sites [get_sites -of_objects [get_clock_regions ${free_sites_range}] -filter {NAME =~ SLICE* && IS_USED == false}]

  for {set i 0} {$i < $group_num + 1} {incr i} {
    set site [lindex ${free_sites} $i]

    if { $site == "" } {
      error "running out of free sites in ${island}"
    }

    for {set j 0} {${j} < ${ANCHOR_PER_SLICE}} {incr j} {
      set index [expr $i * ${ANCHOR_PER_SLICE} + $j]
      if {${index} < ${cell_num}} {
        lappend cell_to_loc [lindex ${target_cells} ${index}]
        lappend cell_to_loc ${site}
      }
    }
  }
}

# place the LUT in the anchor region
set has_found_loc 0
for {set x 118} {$x < 120} {incr x} {
  for {set y 600} {$y < 720} {incr y} {
    set curr_site "SLICE_X${x}Y${y}"
    if { [get_property IS_USED [get_sites ${curr_site}]] != 1} {
      lappend cell_to_loc "pfm_top_i/dynamic_region/gaussian_kernel/inst/GND_HD_Inserted_Inst_interrupt"
      lappend cell_to_loc ${curr_site}
      set has_found_loc 1
      break
    }
  }

  if { ${has_found_loc} == 1} {
    break
  }
}

place_cell $cell_to_loc
