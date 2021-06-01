set lines []
set anchor_cells [get_cells  -regexp -filter { NAME =~  ".*q0_reg.*" } ]

foreach anchor $anchor_cells {
  set input_pin [get_pins "$anchor/D"]
  set output_pin [get_pins "$anchor/Q"]
  set src_cell []
  set dst_cells []

  # get the cells connected to the D pin. Filter other cells that connect their input pins to the nets
  set input_nets [get_nets -segments -regexp -filter { NAME !~  ".*clk.*" && NAME !~  ".*const.*" }  -of_objects $input_pin]
  foreach net $input_nets {
    set all_pins [get_pins -of_object [get_nets $net] -filter { DIRECTION == OUT}]
    set parent_cell [get_cells -of_object $all_pins -filter {IS_PRIMITIVE == 1}]
    append src_cell $parent_cell
  }

  # get the cells connected to the Q pin
  set output_nets [get_nets -segments -regexp -filter { NAME !~  ".*clk.*" && NAME !~  ".*const.*" }  -of_objects $output_pin]
  foreach net $output_nets {
    set all_pins [get_pins -of_object [get_nets $net] -filter { DIRECTION == IN}]
    set parent_cell [get_cells -of_object $all_pins -filter {IS_PRIMITIVE == 1}]

    if {$parent_cell != ""} {
      lappend dst_cells $parent_cell
    }
  }

  # query the location and organize the format
  set locations []

  if {$src_cell != ""} {
    set src_cell_loc [get_property LOC [get_cells $src_cell]]
    lappend locations " \"${src_cell_loc}\""
  }

  if {$dst_cells != []} {
    foreach dst_cell $dst_cells {
      set dst_cell_loc [get_property LOC [get_cells $dst_cell]]
      lappend locations "\"${dst_cell_loc}\""
    }
  }

  set all_locations [join $locations ", "]
  set line "  \"$anchor\" : \[ $all_locations \] "
  lappend lines $line

}

set file [open "anchor_connections.json" "w"]
puts $file " { "
puts $file [join $lines ",\n"]
puts $file " } "
close $file

# set unique_cells [lsort -unique $src_cell]