import json
import sys
import os
from collections import OrderedDict

def getMainScriptOfGlobalClockRouting(empty_ref_checkpoint):
  main = []

  main.append(f"open_checkpoint {empty_ref_checkpoint}")

  main.append("create_cell -reference BUFGCE bufg")
  main.append("place_cell bufg BUFGCE_X0Y194")
  main.append("create_net ap_clk")
  main.append("connect_net -net ap_clk -objects {bufg/O}")
  main.append("create_clock -name ap_clk -period 2.50 [get_pins bufg/O ]")

  main.append("source -notrace create_all_nets.tcl")
  main.append("source -notrace create_all_cells.tcl")
  main.append("source -notrace place_all_cells.tcl")
  main.append("source -notrace connect_all_nets.tcl")
  main.append("source -notrace connect_clocks.tcl")

  main.append("write_checkpoint before_global_clock_routing.dcp")
  main.append("route_design")

  main.append(f'set clock_route_file [open ooc_clock_route.tcl "w" ]')
  main.append(f'set clock_route [get_property ROUTE [get_nets ap_clk] ]')
  main.append(f'puts $clock_route_file "set_property ROUTE $clock_route \[get_nets ap_clk\]"')
  main.append(f'close $clock_route_file')

  main.append("write_checkpoint after_global_clock_routing.dcp")

  return main

def globalClockRouting(hub, base_dir, empty_ref_checkpoint):
  """
  Collect the sample nets from each slot, generate a skeleton design
  Route the design and collect the clock
  """
  clock_dir = f'{base_dir}/clock_routing'

  create_all_nets = []
  connect_all_nets = []
  create_all_cells = []

  place_all_cells = []
  connect_clocks = []

  for slot_name in hub['SlotIO'].keys():
    slot_dir = f'{clock_dir}/{slot_name}'

    # filter empty lines
    loads_tcl = lambda tcl_name: list(filter(None, open(f'{slot_dir}/{tcl_name}', 'r').read().split('\n') ))

    # no additional processing for create_cells
    create_all_cells += loads_tcl('create_all_cells.tcl')

    # distinguish nets and disable printing. FIXME
    slot_create_all_nets = loads_tcl('create_all_nets.tcl')
    slot_connect_all_nets = loads_tcl('connect_all_nets.tcl')  
    connect_all_nets += [net.replace('connect_net -net ', f'connect_net -net {slot_name}_') for net in slot_connect_all_nets]
    create_all_nets += [net.replace('create_net ', f'create_net {slot_name}_') for net in slot_create_all_nets]

    # the first line is "place_cell { \"; the last line is "}"
    slot_place_all_cells = loads_tcl('place_all_cells.tcl')
    assert slot_place_all_cells[0] == 'place_cell { \\', slot_place_all_cells[0]
    assert slot_place_all_cells[-1] == '}', slot_place_all_cells[-1]
    place_all_cells += slot_place_all_cells[1:-1] 

    # the first line is "connect_net -net ap_clk -objects { \"; the last line is "}"
    slot_connect_clocks = loads_tcl('connect_clocks.tcl')
    assert slot_connect_clocks[0] == 'connect_net -net ap_clk -objects { \\', slot_connect_clocks[0]
    assert slot_connect_clocks[-1] == '}', slot_connect_clocks[-1]
    connect_clocks += slot_connect_clocks[1:-1]

    # --- end of for loop ---
  
  # remove duplication
  dedup = lambda tcl : list(OrderedDict.fromkeys(tcl))
  create_all_nets = dedup(create_all_nets)
  connect_all_nets = dedup(connect_all_nets)
  create_all_cells = dedup(create_all_cells)
  place_all_cells = dedup(place_all_cells)
  connect_clocks = dedup(connect_clocks)

  # complete the scripts
  place_all_cells.insert(0, 'place_cell { \\')
  place_all_cells.append('}')

  connect_clocks.insert(0, 'connect_net -net ap_clk -objects { \\')
  connect_clocks.append('}')

  # run
  global_clock_route_dir = f'{clock_dir}/global_clock_routing'
  os.mkdir(global_clock_route_dir)
  open(f'{global_clock_route_dir}/create_all_nets.tcl', 'w').write('\n'.join(create_all_nets))
  open(f'{global_clock_route_dir}/connect_all_nets.tcl', 'w').write('\n'.join(connect_all_nets))
  open(f'{global_clock_route_dir}/create_all_cells.tcl', 'w').write('\n'.join(create_all_cells))
  open(f'{global_clock_route_dir}/place_all_cells.tcl', 'w').write('\n'.join(place_all_cells))
  open(f'{global_clock_route_dir}/connect_clocks.tcl', 'w').write('\n'.join(connect_clocks))

  main = getMainScriptOfGlobalClockRouting(empty_ref_checkpoint)
  open(f'{global_clock_route_dir}/main.tcl', 'w').write('\n'.join(main))

def extractSampleNetsFromSlots(hub, base_dir, anchor_net_extractions_script, empty_ref_checkpoint):
  """
  Extract the anchor nets of each slot and route the clock net
  """
  clock_dir = f'{base_dir}/clock_routing'
  opt_dir = f'{base_dir}/opt_test'

  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{clock_dir}/{slot_name}')

    script = []

    # open the post-opt post-placed checkpoint
    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')

    # extract anchor nets & connections. Will result in a tcl file "sample_connection.tcl"
    script.append(f'source {anchor_net_extractions_script}')
    
    # open an empty checkpoint to route the clock based on the sample
    # extract the route of the clock
    script.append(f'open_checkpoint {empty_ref_checkpoint}')
    script.append(f'source {clock_dir}/{slot_name}/sample_connection.tcl')
    script.append(f'exit')

    open(f'{clock_dir}/{slot_name}/setup_ooc_clock_route.tcl', "w").write('\n'.join(script))

  # generate the gnu parallel tasks
  parallel_txt = open(f'{clock_dir}/parallel-extract-sample.txt', "w")
  vivado = 'VIV_VER=2020.1 vivado -mode batch -source'
  all_tasks = [f'cd {clock_dir}/{slot_name} && {vivado} setup_ooc_clock_route.tcl' \
                for slot_name in hub['SlotIO'].keys()]
  parallel_txt.write('\n'.join(all_tasks))

def routeWithGivenClock(hub, base_dir):
  """
  Run the final routing of each slot with the given clock network
  """
  clock_dir = f'{base_dir}/clock_routing'
  opt_dir = f'{base_dir}/opt_test'

  for slot_name in hub['SlotIO'].keys():
  # the final routing
    script = []
    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')
    script.append(f'source -notrace {clock_dir}/global_clock_routing/ooc_clock_route.tcl')
    script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

    # relax placement pblocks
    script.append(f'delete_pblock [get_pblocks *]')
    script.append(f'create_pblock {slot_name}')
    pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
    script.append(f'resize_pblock [get_pblocks {slot_name}] -add {pblock_def}')
    script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')
    script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_U0]')

    script.append(f'route_design')
    script.append(f'phys_opt_design')
    script.append(f'write_checkpoint -force {clock_dir}/{slot_name}/routed_with_ooc_clock.dcp')

    open(f'{clock_dir}/{slot_name}/route_with_ooc_clock.tcl', "w").write('\n'.join(script))

  # generate the gnu parallel tasks
  parallel_txt = open(f'{clock_dir}/parallel-route-with-ooc-clock.txt', "w")
  vivado = 'VIV_VER=2020.1 vivado -mode batch -source'
  all_tasks = [f'cd {clock_dir}/{slot_name} && {vivado} route_with_ooc_clock.tcl' \
                for slot_name in hub['SlotIO'].keys()]
  parallel_txt.write('\n'.join(all_tasks))

def setGlobalClockRoute(clock_route_path):
  script = []

  script.append(f'set clock_route_file [open {clock_route_path} "r" ]')
  script.append(f'set clock_route [read -nonewline $clock_route_file ]')
  script.append(f'set_property ROUTE $clock_route [get_nets ap_clk]')
  script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

  return script
  
if __name__ == '__main__':
  assert len(sys.argv) == 4, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  option = sys.argv[3]

  hub = json.loads(open(hub_path, 'r').read())

  anchor_net_extractions_script = '/home/einsx7/auto-parallel/src/tcl/extractBoundaryNets.tcl'
  empty_ref_checkpoint = '/home/einsx7/auto-parallel/src/clock/test_clock.dcp'

  if option == 'ExtractSample':
    os.mkdir(f'{base_dir}/clock_routing')
    extractSampleNetsFromSlots(hub, base_dir, anchor_net_extractions_script, empty_ref_checkpoint)
    routeWithGivenClock(hub, base_dir)
  elif option == 'GlobalClockRouting':
    globalClockRouting(hub, base_dir, empty_ref_checkpoint)
  else:
    assert False