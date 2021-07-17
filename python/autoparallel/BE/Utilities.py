import re
from typing import List

from autobridge.Opt.Slot import Slot
from autobridge.Device.DeviceManager import DeviceU250
U250_inst = DeviceU250()


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


def isPairSLRCrossing(slot1_name: str, slot2_name: str) -> bool:
  """
  check if two slots span two SLRs
  """
  slot1 = Slot(U250_inst, slot1_name)
  slot2 = Slot(U250_inst, slot2_name)

  if slot1.down_left_x != slot2.down_left_x:
    return False
  else:
    up_slot = slot1 if slot1.down_left_y > slot2.down_left_y else slot2
    if not any(y == up_slot.down_left_y for y in [4, 8, 12]):
      return False
    else:
      return True


def getNeighborSlots(hub, slot_name: str) -> List[str]:
  neighbors = []
  for slot1_name, slot2_name in hub["AllSlotPairs"]:
    if slot1_name == slot_name:
      neighbors.append(slot2_name)
    elif slot2_name == slot_name:
      neighbors.append(slot1_name)

  return neighbors


def getAnchorTimingReportScript() -> List[str]:
  script = []

  # generate the timing report
  script.append('report_timing -from [get_cells  "*q0_reg*"] -delay_type max -max_paths 100000 -sort_by group -input_pins -routable_nets -file timing_report_from_anchor.txt')
  script.append('report_timing -to [get_cells  "*q0_reg*"] -delay_type max -max_paths 100000 -sort_by group -input_pins -routable_nets -file timing_report_to_anchor.txt')

  # this is to enable calling python from within vivado
  script.append('unset ::env(PYTHONPATH)')
  script.append('unset ::env(PYTHONHOME)')

  script.append(f'exec python3.6 autoparallel.BE.TimingReportParser')

  return script
