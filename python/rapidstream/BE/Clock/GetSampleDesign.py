def getSampleLoc(x, y):
  sample_x = [0, 46, 73, 105, 131, 159, 192, 232]
  sample_y = [20 + 60 * row_idx for row_idx in range(16)]
  return f'SLICE_X{sample_x[x]}Y{sample_y[y]}'

def getSampleDesign(empty_ref_checkpoint, num_row, num_col):
  """
  use a chain of registers to cover the entire device
  """
  main = []
  main.append(f'open_checkpoint {empty_ref_checkpoint}')

  main.append('create_cell -reference BUFGCE bufg')
  main.append('place_cell bufg BUFGCE_X0Y194')
  main.append('create_net ap_clk')
  main.append('connect_net -net ap_clk -objects {bufg/O}')
  main.append('create_clock -name ap_clk -period 2.50 [get_pins bufg/O ]')

  for x in range(num_col):
    for y in range(num_row):
      main.append(f'create_cell -reference FDRE FF_X{x}Y{y}')
      # main.append(f'create_pblock CR_X{x}Y{y}')
      # main.append(f'resize_pblock CR_X{x}Y{y} -add {{CLOCKREGION_X{x}Y{y}:CLOCKREGION_X{x}Y{y}}}')
      # main.append(f'add_cells_to_pblock CR_X{x}Y{y} [get_cells FF_X{x}Y{y}]')
      main.append(f'connect_net -net ap_clk -objects FF_X{x}Y{y}/C')
      main.append(f'place_cell FF_X{x}Y{y} {getSampleLoc(x, y)}')

  # add horizontal connection. Row 0 will go rightwards and row 1 will go leftwards
  for y in range(num_row):
    if y % 2:
      for x in reversed(range(num_col-1)):
        main.append(f'create_net FF_X{x+1}Y{y}_To_FF_X{x}Y{y}')
        main.append(f'connect_net -net FF_X{x+1}Y{y}_To_FF_X{x}Y{y} -objects {{ FF_X{x+1}Y{y}/Q FF_X{x}Y{y}/D }}')
    else:
      for x in range(num_col-1):
        main.append(f'create_net FF_X{x}Y{y}_To_FF_X{x+1}Y{y}')
        main.append(f'connect_net -net FF_X{x}Y{y}_To_FF_X{x+1}Y{y} -objects {{ FF_X{x}Y{y}/Q FF_X{x+1}Y{y}/D }}')

  # add vertical connection
  for y in range(num_row):
    if y % 2: # odd rows
      main.append(f'create_net FF_X{num_col-1}Y{y-1}_To_FF_X{num_col-1}Y{y}')
      main.append(f'connect_net -net FF_X{num_col-1}Y{y-1}_To_FF_X{num_col-1}Y{y} -objects {{ FF_X{num_col-1}Y{y-1}/Q FF_X{num_col-1}Y{y}/D }}')
    else: # even rows
      if y-1 >= 0:
        main.append(f'create_net FF_X0Y{y-1}_To_FF_X0Y{y}')
        main.append(f'connect_net -net FF_X0Y{y-1}_To_FF_X0Y{y} -objects {{ FF_X0Y{y-1}/Q FF_X0Y{y}/D }}')

  main.append('route_design')
  
  return main

if __name__ == '__main__':
  script = getSampleDesign('/home/einsx7/share/empty_U250.dcp', num_row=16, num_col=8)
  open('./test_sample_design/get_sample_design.tcl', 'w').write('\n'.join(script))