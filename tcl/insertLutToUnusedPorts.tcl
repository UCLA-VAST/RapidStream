
# get all wrapper cells
set wrapper_cells [get_cells -filter {IS_PRIMITIVE == False}]
foreach wrapper ${wrapper_cells} {
  set GND_net "${wrapper}/<const0>"
  set VCC_net "${wrapper}/<const1>"

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

  # disconnect the pins from GND/VCC
  disconnect_net -net [get_nets $GND_net] -objects ${GND_pins}
  disconnect_net -net [get_nets $VCC_net] -objects ${VCC_pins}

  # inject an LUT between the unused pins and VCC
  foreach gnd_pin $GND_pins {
    set lut_name ${gnd_pin}_lut1
    create_cell -reference LUT1 ${lut_name}

    # O = ! I0
    # invert VCC to become GND
    set_property INIT 2'h1 [ get_cells ${lut_name}]

    create_net -net ${lut_name}_output
    connect_net -net ${lut_name}_output -objects [concat [get_pins ${gnd_pin}]  [get_pins ${lut_name}/O ] ]
    connect_net -net $GND_net -objects [get_pins ${lut_name}/I0 ]
  }
  foreach vcc_pin $VCC_pins {
    set lut_name ${vcc_pin}_lut1
    create_cell -reference LUT1 ${lut_name}

    # O = I0
    set_property INIT 2'h2 [ get_cells ${lut_name}]

    create_net -net ${lut_name}_output
    connect_net -net ${lut_name}_output -objects [concat [get_pins ${vcc_pin}]  [get_pins ${lut_name}/O ] ]
    connect_net -net $VCC_net -objects [get_pins ${lut_name}/I0 ]
  }
}
