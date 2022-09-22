# for HMSS overlay v3, directly place the cells connected to upper level dfx region
# skip invoking place_design during overlay construction

set target_cells [ get_cells pfm_top_i/dynamic_region/gaussian_kernel/inst/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3/* -filter { ( STATUS == UNPLACED || STATUS == ASSIGNED) && PRIMITIVE_TYPE !~ OTHERS.*.* } ]
set free_sites [get_sites -of_objects [get_clock_regions X5Y1] -filter {NAME =~ SLICE* && IS_USED == false}]

set cell_num [llength $target_cells]
set ANCHOR_PER_SLICE 4
set group_num [expr ${cell_num} / ${ANCHOR_PER_SLICE}]
set cell_to_loc []
for {set i 0} {$i < $group_num + 1} {incr i} {
  set site [lindex ${free_sites} $i]
  for {set j 0} {${j} < ${ANCHOR_PER_SLICE}} {incr j} {
    set index [expr $i * ${ANCHOR_PER_SLICE} + $j]
    if {${index} < ${cell_num}} {
      lappend cell_to_loc [lindex ${target_cells} ${index}]
      lappend cell_to_loc ${site}
    }
  }
}

place_cell $cell_to_loc
