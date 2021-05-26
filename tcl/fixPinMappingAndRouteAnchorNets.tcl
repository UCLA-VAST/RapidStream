# get all anchor nets
set anchor_nets [get_nets  -regexp -top_net_of_hierarchical_group -filter { NAME !~  ".*clk.*" && NAME !~  ".*const.*" }  -of_objects [get_cells  -regexp -filter { NAME =~  ".*q0_reg.*" } ]]

# get all LUTs connected to anchor nets
set all_target_luts []
foreach net $anchor_nets {
  set all_cells [get_cells -of_object [get_nets -segments $net] -filter { PRIMITIVE_TYPE =~ CLB.LUT.* }]

  foreach cell $all_cells {
    # if {![regexp (srl) $cell ] } {
      lappend all_target_luts [get_cells $cell]
    # }    
  }
}

# remove duplicates
set unique_targets [lsort -unique $all_target_luts]

# fix the pin mapping of those LUTs
foreach lut $unique_targets {
  set all_pins [get_pins -of_object $lut]

  set pin_mapping ""
  foreach pin $all_pins {
    set bel_pin [get_bel_pins -of_object $pin]

    set pin_name [lindex [split $pin /] end]
    set bel_pin_name [lindex [split $bel_pin /] end]
    
    # exclude the output port of the LUT
    if { ![regexp (O) $bel_pin_name ] } { 
      append pin_mapping " $pin_name:$bel_pin_name "
    }

  }

  puts "set_property LOCK_PINS $pin_mapping $lut"
  set_property LOCK_PINS $pin_mapping $lut
}

# set the clock route
source /home/einsx7/auto-parallel/src/clock/only_hdistr.tcl
set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]

# only route the anchor nets
route_design -preserve

# print out the routes of the anchor nets
set anchor_nets [get_nets  -regexp -top_net_of_hierarchical_group -filter { NAME !~  ".*clk.*" && NAME !~  ".*const.*" }  -of_objects [get_cells  -regexp -filter { NAME =~  ".*q0_reg.*" } ]]
set file [open "enforce_anchor_routes.tcl" "w"]
foreach lut_name [array names lut_array] {
  puts "Creating LOC_PINS constraint $lut_array($lut_name) for LUT $lut_name."
  puts $file "set_property LOCK_PINS \"$lut_array($lut_name)\" \[get_cells $lut_name \]"
}
foreach net $anchor_nets {
  set route [get_property ROUTE $net]
  puts $file "set_property ROUTE $route \[get_nets $net\]"
}
close $file