set main [open "sample_connection.tcl" "w"]
set anchor_cells [get_cells -regexp .*q0_reg.{0,6}] 

puts $main "create_cell -reference BUFGCE bufg"
puts $main "place_cell bufg BUFGCE_X0Y194"
puts $main "create_net ap_clk"
puts $main "connect_net -net ap_clk -objects {bufg/O}"
puts $main "create_clock -name ap_clk -period 2.50 \[get_pins bufg/O\]"

puts $main "source -notrace create_all_nets.tcl"
puts $main "source -notrace create_all_cells.tcl"
puts $main "source -notrace place_all_cells.tcl"
puts $main "source -notrace connect_all_nets.tcl"
puts $main "source -notrace connect_clocks.tcl"

close $main

set create_all_nets [open "create_all_nets.tcl" "w"]
set create_all_cells [open "create_all_cells.tcl" "w"]
set place_all_cells [open "place_all_cells.tcl" "w"]
set connect_all_nets [open "connect_all_nets.tcl" "w"]
set connect_clocks [open "connect_clocks.tcl" "w"]

set log [open "extrac_sample.log" "w"]

puts $place_all_cells "place_cell { \\"
puts $connect_clocks "connect_net -net ap_clk -objects { \\"

set visited_pins []

# for each anchor register
foreach anchor $anchor_cells {
  # get the signal nets of the reg
  set all_nets_of_anchor [get_nets -segment -of_objects [get_cells $anchor ] \
      -filter { NAME !~ "*ap_clk*" && NAME !~ "*const*" && ROUTE_STATUS != "HIERPORT"}] 

  # command to construct the net in the new design
  set anchor_updated_name [regsub -all "/" $anchor "_"]
  set net_name "${anchor_updated_name}_net"
  puts $create_all_nets "create_net ${net_name}"

  # for each pin connected to the anchor reg
  set all_pins_of_nets [get_pins -of_objects $all_nets_of_anchor ]
  foreach pin_full_name $all_pins_of_nets {
    # avoid duplication because of directly connected passing pipelines
    if { $pin_full_name in $visited_pins } {
      puts $log "skip anchor ${anchor}, seen visited pins. Nets of anchor: ${all_pins_of_nets}"
      break
    }
    lappend visited_pins $pin_full_name

    # filter hierarchical cells
    set parent_cell_of_pin [get_cells [get_property PARENT_CELL $pin_full_name] ]
    if { [get_property IS_PRIMITIVE $parent_cell_of_pin] == 1 } {
      set parent_cell_type [get_property REF_NAME [get_cells $parent_cell_of_pin]]
      set new_cell_name [regsub -all "/" $parent_cell_of_pin "_"]

      # command to create and place the cell in the new design
      set loc [get_property LOC [get_cells $parent_cell_of_pin] ]
      set bel [get_property BEL [get_cells $parent_cell_of_pin] ]
      set extracted_bel [lindex [split $bel "."] 1] 

      puts $create_all_cells "create_cell -reference ${parent_cell_type} ${new_cell_name}"
      puts $place_all_cells "  ${new_cell_name} ${loc}/${extracted_bel} \\"
      set pin_split [split $pin_full_name "/"]
      set pin [lindex $pin_split [expr { [llength $pin_split] - 1}]]
      puts $connect_all_nets "connect_net -net ${net_name} -objects { ${new_cell_name}/${pin} }"

      # connect the new cell to the clock
      if {$parent_cell_type == "FDRE"} {
        puts $connect_clocks "  ${new_cell_name}/C \\"
      } elseif { [regexp {.*SRL.*} $parent_cell_type] } {
        puts $connect_clocks "  ${new_cell_name}/CLK \\"
      } elseif { [regexp {.*RAMB.*} $parent_cell_type] } {
        puts $connect_clocks "  ${new_cell_name}/CLKARDCLK \\"
        puts $connect_clocks "  ${new_cell_name}/CLKBWRCLK \\"
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
close $log