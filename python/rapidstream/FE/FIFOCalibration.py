import json
import logging

from autobridge.Opt.Floorplan import Floorplanner
from autobridge.Opt.FloorplanLegalize import RESOURCE_TYPES


def logFIFOSizes(floorplan: Floorplanner) -> None:
  for slot, e_list in floorplan.s2e.items():
    logging.debug(f'Slot: {slot.getRTLModuleName()}')
    for e in e_list:
      logging.debug(json.dumps(e.getArea(skip_balance_part=False)))

  for slot, e_list in floorplan.s2e.items():
    total_fifo_resource = {r : sum(e.getArea(skip_balance_part=False)[r] for e in e_list) for r in RESOURCE_TYPES }
    orig_fifo_resource = {r : sum(e.getArea(skip_balance_part=True)[r] for e in e_list) for r in RESOURCE_TYPES }    
    percentage = {r: total_fifo_resource[r] / slot.area[r] for r in RESOURCE_TYPES}
    orig_percentage = {r: orig_fifo_resource[r] / slot.area[r] for r in RESOURCE_TYPES}
    logging.info(f'Slot: {slot.getRTLModuleName()}')
    logging.info(json.dumps(total_fifo_resource, indent=2))
    logging.info(json.dumps(percentage, indent=2))
    logging.info(json.dumps(orig_percentage, indent=2))

def FIFOCalibration(floorplan: Floorplanner) -> None:
  slot_to_vertex_utilization = floorplan.getUtilization()

  for slot, e_list in floorplan.s2e.items():
    v_util = slot_to_vertex_utilization[slot]
    e_util = {r: sum(e.getArea(skip_balance_part=False)[r] for e in e_list) / slot.area[r] for r in RESOURCE_TYPES }
    total_util = {r: e_util[r] + v_util[r] for r in RESOURCE_TYPES}

    logging.info(f'Total utilization for slot {slot.getRTLModuleName()}:')
    logging.info(json.dumps(total_util, indent=2))

    # if total_util['BRAM'] < 0.4 and total_util['LUT'] > 0.5:
    #   logging.info(f'Convert FIFO to BRAM type for slot {slot.getRTLModuleName()}')
    #   e_list.sort(key=lambda e: (0-(e.depth+e.latency), e.width))
    #   for e in e_list:
    #     logging.info(f'convert {e.name} of width {e.width} and depth {e.depth+e.latency} to BRAM FIFO')
    #     e.fifo_type = 'BRAM'
    #     e_util = {r: sum(e.getArea(skip_balance_part=False)[r] for e in e_list) / slot.area[r] for r in RESOURCE_TYPES }
    #     total_util = {r: e_util[r] + v_util[r] for r in RESOURCE_TYPES}
    #     if total_util['BRAM'] > 0.45:
    #       break

    #   logging.info(f'Adjusted total utilization for slot {slot.getRTLModuleName()}:')
    #   logging.info(json.dumps(total_util, indent=2))