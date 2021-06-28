import re


def getSlotsInSLRIndex(hub, slr_index):
  """
  get all slots within a given SLR
  """
  all_slot_names = hub['SlotIO'].keys()
  slots_in_slr = []
  for name in all_slot_names:
    match = re.search(r'CR_X(\d+)Y(\d+)_To_CR_X(\d+)Y(\d+)', name)
    DL_y = int(match.group(2))
    UR_y = int(match.group(4))

    # assume that each SLR has 4 rows of clock regions
    if slr_index * 4 <= DL_y <= slr_index * 4 + 3:
      if slr_index * 4 <= UR_y <= slr_index * 4 + 3:
        slots_in_slr.append(name)

  return slots_in_slr


def getPruningAnchorScript(dcp_path, inner_module_name, output_dir):
  """
  after we mark the checkpoint as non-ooc, use write_checkpoint -cell
  to remove the anchored wrapper
  Note that the route of VCC/GND nets will be lost during write_checkpoint -cell
  And 2020.1 has a bug that cannot route them back in preserve mode
  To work around the problem, we first record the route of VCC/GND nets
  then re-apply them in the child checkpoint
  """
  script = []
  script.append(f'open_checkpoint {dcp_path}')
  
  # record the VCC/GND routes
  script.append(f'set GND_route [get_property ROUTE [get_nets <const0>]]')
  script.append(f'set VCC_route [get_property ROUTE [get_nets <const1>]]')
  script.append(f'set_property HD.RECONFIGURABLE 1 [get_cells {inner_module_name}]')
  script.append( 'set anchor_cells [get_cells -regexp .*q0_reg.*]')
  script.append( 'route_design -unroute -nets [get_nets -of_object ${anchor_cells} -filter {TYPE != "GOURND" && TYPE != "POWER" && NAME !~ "*ap_clk*"} ]')
  script.append(f'write_checkpoint -cell {inner_module_name} {output_dir}/{inner_module_name}_temp.dcp')
  
  # re-apply the VCC/GND routes
  script.append(f'open_checkpoint {output_dir}/{inner_module_name}_temp.dcp')
  script.append(f'set_property ROUTE $GND_route [get_nets <const0>]')
  script.append(f'set_property ROUTE $VCC_route [get_nets <const1>]')
  
  # since the anchors are gone, parts of the VCC/GND route are float. Clean it up. 
  script.append(f'route_design -preserve -physical_nets')
  script.append(f'write_checkpoint {output_dir}/{inner_module_name}.dcp')

  return script
