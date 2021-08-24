# set anchor_cells [get_cells  -regexp -filter { NAME =~  ".*q0_reg.*" } ]

set src_cells []
set dst_cells []

foreach target $target_cells {
  set input_pin [get_pins "$target/D"]
  set output_pin [get_pins "$target/Q"]


  # get the cells connected to the D pin. Filter other cells that connect their input pins to the nets
  set input_nets [get_nets -segments -regexp -filter { TYPE == SIGNAL }  -of_objects $input_pin]
  foreach net $input_nets {
    set all_pins [get_pins -of_object [get_nets $net] -filter { DIRECTION == OUT}]
    set parent_cell [get_cells -of_object $all_pins -filter {IS_PRIMITIVE == 1}]
    lappend src_cells $parent_cell
  }

  # get the cells connected to the Q pin
  set output_nets [get_nets -segments -regexp -filter { TYPE == SIGNAL }  -of_objects $output_pin]
  foreach net $output_nets {
    set all_pins [get_pins -of_object [get_nets $net] -filter { DIRECTION == IN}]
    set parent_cell [get_cells -of_object $all_pins -filter {IS_PRIMITIVE == 1}]

    if {$parent_cell != ""} {
      foreach target $parent_cell {
        lappend dst_cells $target
      }
    }
  }
}

set unique_src_cells [lsort -unique $src_cells]
set unique_dst_cells [lsort -unique $dst_cells]
set neighbor_cells [concat $unique_dst_cells $unique_src_cells]