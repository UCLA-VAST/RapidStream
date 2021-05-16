set anchors [get_cells -regexp ".*_q0_reg.{0,6}"]
set all_dead_nets []
set all_chosen_nets []
set all_target_ports []

set num [llength $anchors]

foreach anchor $anchors {
  set dead_net [ get_nets -of_objects [get_cells $anchor] -filter { NAME !~ "*ap_clk*" && NAME !~ "*const*" && ROUTE_STATUS == "HIERPORT" } ]
  set chosen_net [ get_nets -of_objects [get_cells $anchor] -filter { NAME !~ "*ap_clk*" && NAME !~ "*const*" && ROUTE_STATUS != "HIERPORT" } ]
  set target_port [get_ports -of_objects [get_nets $dead_net]]

  set_property DONT_TOUCH 0 [get_nets $dead_net]
  set_property DONT_TOUCH 0 [get_nets $chosen_net]

  lappend all_dead_nets $dead_net
  lappend all_chosen_nets $chosen_net
  lappend all_target_ports $target_port

}

for {set i 0} {$i < $num} {incr i} {
  set anchor [lindex $anchors $i]
  set dead_net [lindex $all_dead_nets $i]
  set chosen_net [lindex $all_chosen_nets $i]
  set target_port [lindex $all_target_ports $i]

  disconnect_net -net $dead_net -objects [get_ports $target_port]
}

for {set i 0} {$i < $num} {incr i} {
  set anchor [lindex $anchors $i]
  set dead_net [lindex $all_dead_nets $i]
  set chosen_net [lindex $all_chosen_nets $i]
  set target_port [lindex $all_target_ports $i]

  # disconnect_net -quiet -net $chosen_net -objects [get_pins -of_objects [get_cells $anchor]]
  foreach pin [get_pins -of_objects $chosen_net] {
    if { [get_property PARENT_CELL [get_pins $pin] ] == $anchor} {
      set dead_pin $pin
      break
    }
  }
  disconnect_net -net $chosen_net -objects [get_pins $dead_pin]
}

for {set i 0} {$i < $num} {incr i} {
  set chosen_net [lindex $all_chosen_nets $i]
  set target_port [lindex $all_target_ports $i]

  connect_net -net $chosen_net -objects [get_ports $target_port]
}

# remove the anchors
set_property DONT_TOUCH 0 [get_nets ap_clk]
foreach anchor $anchors {
  set_property DONT_TOUCH 0 [get_cells $anchor]
}
remove_cell $anchors

# rename the clock port
set_property DONT_TOUCH 0 [get_nets ap_clk_port]
set_property DONT_TOUCH 0 [get_cells test_bufg]
disconnect_net -net ap_clk_port -objects [get_ports ap_clk_port]
remove_port ap_clk_port
disconnect_net -net ap_clk -objects [get_pins test_bufg/O]
remove_cell test_bufg
create_port -direction IN ap_clk
connect_net -net ap_clk -objects [get_ports ap_clk]

# unroute the clock net
set_property IS_ROUTE_FIXED 0 [get_nets ap_clk]
route_design -unroute -nets [get_nets ap_clk]

# remove dead nets
opt_design
