# for each new hmss shell, run this script and rapidstream.backend.get_laguna_blocker.py
# to get a list of pre-used laguna TXs and RXs.
# We need to create dummy FFs to block those positions when we place the anchors

set xnets [::xilinx::designutils::get_inter_slr_nets]

set blocked_RXs []
foreach xnet $xnets {
  # examples:
  # LAG_LAG_X69Y180/LAG_LAGUNA_SITE_3_RXD0
  # LAG_LAG_X69Y180/RXD18
  # LAG_LAG_X69Y180/LAG_MUX_ATOM_9_TXOUT
  # LAG_LAG_X69Y180/UBUMP18
  set routing_nodes [get_nodes -of_objects $xnet]
  foreach routing_node $routing_nodes {
    set tile_and_node [split $routing_node "/"]
    set tile_name [lindex $tile_and_node 0]
    set node_name [lindex $tile_and_node 1]
    if { [string match "LAG_LAG*" $tile_name]} {
      if { [string match "LAG_LAGUNA_SITE_*_RXD*" $node_name] } {
        # so we only get the blocked RX reg
        # we dont care about laguna usage in the static region
        # in U280 situation, we hard code the value
        regexp "X([0-9]+)Y" $tile_name full_match part_match
        if {${part_match} >= 123 } {
          continue
        }

        # each site contains 4 laguna slices
        set LAG_LAGUNA_SITE_ID_PIN [split $node_name "_"]
        set site_id [lindex $LAG_LAGUNA_SITE_ID_PIN 3]
        set pin_name [lindex $LAG_LAGUNA_SITE_ID_PIN 4]
        # select the slice that is being blocked
        set blocked_laguna_site [lindex [get_sites -of_objects [get_tiles ${tile_name}] ] ${site_id}]
        # get the bel based on the name of the blocked pin name
        set blocked_laguna_bel [string map {"D" "_REG"} ${pin_name}]

        lappend blocked_RXs "${blocked_laguna_site}/${blocked_laguna_bel}"
      }
    }
  }
}

set file [open "blocked_laguna_RX_list.txt" "w"]
puts $file [join $blocked_RXs "\n"]
close $file
