# get all wrapper cells
set wrapper_cells [get_cells * -filter {IS_PRIMITIVE == False}]

foreach wrapper ${wrapper_cells} {
  set GND_net "${wrapper}/<const0>"
  set VCC_net "${wrapper}/<const1>"
  set clk_net "${wrapper}/ap_clk"

  # get all used pins of the wrapper that connect to GND/VCC
  set GND_pins [
    get_pins -of_objects [get_nets $GND_net] -filter {
      DIRECTION == OUT && REF_NAME != VCC && REF_NAME != GND
    }
  ]
  set VCC_pins [
    get_pins -of_objects [get_nets $VCC_net] -filter {
      DIRECTION == OUT && REF_NAME != VCC && REF_NAME != GND
    }
  ]

  set mydict []
  if {[llength $GND_pins]} {
    # disconnect the pins from GND/VCC
    disconnect_net -net [get_nets $GND_net] -objects ${GND_pins}

    # inject an FF between the unused pins and VCC
    foreach gnd_pin $GND_pins {
      set ff_name ${gnd_pin}_ff
      create_cell -reference FDRE ${ff_name}

      create_net -net ${ff_name}_Q
      connect_net -net ${ff_name}_Q -objects [concat [get_pins ${gnd_pin}]  [get_pins ${ff_name}/Q ] ]

      # connect FF input to GND
      lappend mydict [get_nets $GND_net]; lappend mydict [get_pins ${ff_name}/D]

      # enable and clock
      lappend mydict [get_nets $VCC_net]; lappend mydict [get_pins ${ff_name}/CE]
      lappend mydict [get_nets $GND_net]; lappend mydict [get_pins ${ff_name}/R]
      lappend mydict [get_nets $clk_net]; lappend mydict [get_pins ${ff_name}/C]
    }
  }

  if {[llength $VCC_pins]} {
    disconnect_net -net [get_nets $VCC_net] -objects ${VCC_pins}
    foreach vcc_pin $VCC_pins {
      set ff_name ${vcc_pin}_ff
      create_cell -reference FDRE ${ff_name}

      create_net -net ${ff_name}_Q
      connect_net -net ${ff_name}_Q -objects [concat [get_pins ${vcc_pin}]  [get_pins ${ff_name}/Q ] ]

      # connect FF source to VCC
      lappend mydict [get_nets $VCC_net]; lappend mydict [get_pins ${ff_name}/D]

      # enable and clock
      lappend mydict [get_nets $VCC_net]; lappend mydict [get_pins ${ff_name}/CE]
      lappend mydict [get_nets $GND_net]; lappend mydict [get_pins ${ff_name}/R]
      lappend mydict [get_nets $clk_net]; lappend mydict [get_pins ${ff_name}/C]
    }
  }

  connect_net -dict $mydict
}
