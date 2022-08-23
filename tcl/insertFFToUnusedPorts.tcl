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

# for input pins, connect to D pin of dummy FFs
foreach wrapper ${wrapper_cells} {
  set empty_pins []
  set nets_to_connect []
  set GND_net "${wrapper}/<const0>"
  set VCC_net "${wrapper}/<const1>"
  set clk_net "${wrapper}/ap_clk"

  set all_input_pins [get_pins -of_object [get_cells ${wrapper}] -filter {DIRECTION == IN}]

  foreach pin ${all_input_pins} {
    set all_nets [get_nets -segments -of_object [get_pins ${pin}]]
    set net_count [ llength ${all_nets} ]
    if { ${net_count} == 1} {
      lappend empty_pins ${pin}
    }
  }

  foreach pin ${empty_pins} {
    puts "Found unused input pin ${pin}"
    create_cell -reference FDRE ${pin}_ff
    create_net ${pin}_ff_D
    # lappend nets_to_connect [get_nets ${pin}_ff_D]; lappend nets_to_connect [get_pins ${pin}];
    connect_net -net ${pin}_ff_D -objects [get_pins ${pin}]

    lappend nets_to_connect [get_nets ${pin}_ff_D]; lappend nets_to_connect [get_pins ${pin}_ff/D];
    lappend nets_to_connect [get_nets $VCC_net];    lappend nets_to_connect [get_pins ${pin}_ff/CE];
    lappend nets_to_connect [get_nets $GND_net];    lappend nets_to_connect [get_pins ${pin}_ff/R];
    lappend nets_to_connect [get_nets $clk_net];    lappend nets_to_connect [get_pins ${pin}_ff/C];
  }

  connect_net -hier -dict $nets_to_connect
}
