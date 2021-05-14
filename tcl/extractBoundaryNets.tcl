set main [open "sample_connection.tcl" "w"]
set anchor_cells [get_cells -regexp .*q0_reg.{0,6}] 

puts $main "create_cell -reference BUFGCE bufg"
puts $main "place_cell bufg BUFGCE_X0Y194"
puts $main "create_net ap_clk"
puts $main "connect_net -net ap_clk -objects {bufg/O}"
puts $main "create_clock -name ap_clk -period 2.50 \[get_pins bufg/O\]"

puts $main "source create_all_nets.tcl"
puts $main "source create_all_cells.tcl"
puts $main "source place_all_cells.tcl"
puts $main "source connect_all_nets.tcl"
puts $main "source connect_clocks.tcl"

close $main

set create_all_nets [open "create_all_nets.tcl" "w"]
set create_all_cells [open "create_all_cells.tcl" "w"]
set place_all_cells [open "place_all_cells.tcl" "w"]
set connect_all_nets [open "connect_all_nets.tcl" "w"]
set connect_clocks [open "connect_clocks.tcl" "w"]

puts $place_all_cells "place_cell { \\"
puts $connect_clocks "connect_net -net ap_clk -objects { \\"


# for each anchor register
foreach anchor $anchor_cells {
  # get the signal nets of the reg
  set all_nets_of_anchor [get_nets -segment -of_objects [get_cells $anchor ] \
      -filter { NAME !~ "*ap_clk*" && NAME !~ "*const*" && ROUTE_STATUS != "HIERPORT"}] 

  # command to construct the net in the new design
  set anchor_updated_name [regsub -all "/" $anchor "_"]
  set net_name "${anchor_updated_name}_net"
  puts $create_all_nets "create_net ${net_name}"

  # for each pin_full_name connected to the anchor reg
  foreach pin_full_name [get_pins -of_objects $all_nets_of_anchor ] {
    set parent_cell [get_cells [get_property PARENT_CELL $pin_full_name] ]
    
    set pin_split [split $pin_full_name "/"]
    set pin [lindex $pin_split [expr { [llength $pin_split] - 1}]]

    # filter hierarchical cells
    if { [get_property IS_PRIMITIVE $parent_cell] == 1 } {
      set parent_cell_type [get_property REF_NAME [get_cells $parent_cell]]
      set new_cell [regsub -all "/" $parent_cell "_"]

      # command to create and place the cell in the new design
      set loc [get_property LOC [get_cells $parent_cell] ]
      set bel [get_property BEL [get_cells $parent_cell] ]
      set extracted_bel [lindex [split $bel "."] 1] 

      puts $create_all_cells "create_cell -reference ${parent_cell_type} ${new_cell}"
      puts $place_all_cells "  ${new_cell} ${loc}/${extracted_bel} \\"
      puts $connect_all_nets "connect_net -net ${net_name} -objects { ${new_cell}/${pin} }"

      # connect the new cell to the clock
      if {$parent_cell_type == "FDRE"} {
        puts $connect_clocks "  ${new_cell}/C \\"
      } elseif { [regexp {.*SRL.*} $parent_cell_type] } {
        puts $connect_clocks "  ${new_cell}/CLK \\"
      } elseif { [regexp {.*RAMB.*} $parent_cell_type] } {
        puts $connect_clocks "  ${new_cell}/CLKARDCLK \\"
        puts $connect_clocks "  ${new_cell}/CLKBWRCLK \\"
      } elseif { [regexp {.*LUT.*} $parent_cell_type] } {

      } else {
        puts "unrecognized type: ${parent_cell_type}"
        puts $connect_clocks "unrecognized type: ${parent_cell_type}"
        break
      }

    }
  }
}

puts $place_all_cells "}"
puts $connect_clocks "}"

close $create_all_nets 
close $create_all_cells
close $place_all_cells 
close $connect_all_nets
close $connect_clocks 