set lines []

# need to set kernel_cell_addr outside
set anchor_cells [get_cells  -regexp ${kernel_cell_addr}.*q.*_reg.*]

foreach anchor $anchor_cells {
  # first get the location of anchor itself
  set anchor_loc [get_property LOC [get_cells $anchor]]
  set anchor_bel [get_property BEL [get_cells $anchor]]
  set anchor_bel [lindex [split $anchor_bel "."] 1]

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
      foreach target $parent_cell {
        lappend dst_cells $target
      }
    }
  }

  # query the location and organize the format
  set locations []

  if {$src_cell != ""} {
    set src_cell_loc [get_property LOC [get_cells $src_cell]]
    set src_cell_bel [get_property BEL [get_cells $src_cell]]
    set src_cell_bel [lindex [split $src_cell_bel "."] 1]
    set src_cell_type [get_property PRIMITIVE_TYPE [get_cells $src_cell] ]

    # the source cell may be VCC or GND
    if {$src_cell_loc != ""} {
      lappend locations " { \"name\": \"${src_cell}\", \"dir\": \"input\", \"loc\": \"${src_cell_loc}/${src_cell_bel}\", \"type\": \"${src_cell_type}\" } "
    }
  }

  if {$dst_cells != []} {
    foreach dst_cell $dst_cells {
      set dst_cell_loc [get_property LOC [get_cells $dst_cell]]
      set dst_cell_bel [get_property BEL [get_cells $dst_cell]]
      set dst_cell_bel [lindex [split $dst_cell_bel "."] 1]
      set dst_cell_type [get_property PRIMITIVE_TYPE  [get_cells $dst_cell] ]
      lappend locations " { \"name\": \"${dst_cell}\", \"dir\": \"output\", \"loc\": \"${dst_cell_loc}/${dst_cell_bel}\", \"type\": \"${dst_cell_type}\" }"
    }
  }

  set all_locations [join $locations ", "]
  set line "  \"$anchor\" : { \"anchor_loc\": \"${anchor_loc}/${anchor_bel}\", \"connections\": \[ $all_locations \] }"
  lappend lines $line

}

set file [open "anchor_connections.json" "w"]
puts $file " { "
puts $file [join $lines ",\n"]
puts $file " } "
close $file

# set unique_cells [lsort -unique $src_cell]
