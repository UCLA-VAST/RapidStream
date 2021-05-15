import json
import sys
import os
from collections import OrderedDict

def organizeHier(sample_route : str):
  """
  Helper function to print the clock route in more readable way
  """
  hier_route = ''
  level = 1
  pad = lambda level: level * "  "

  for char in sample_route:
    if char == '{':
      level += 1
      hier_route += f'\n{pad(level-1)}{{\n{pad(level)}'
    elif char == '}':
      hier_route += f'\n{pad(level-1)}}}\n{pad(level)}'
      level -= 1
    else:
      hier_route += char
  open('hier_sample_route.txt', 'w').write(hier_route)

def pruneLeaf(clock_route_path):
  """
  prune away children nodes of leaf clock buffer nodes
  """
  sample_route = open(clock_route_path, 'r').read()
  tokens = [token for token in sample_route.split(' ') if token]

  pruned_route = []
  seen_clock_leaf = False
  stack = 0

  for i, token in enumerate(tokens):
    # now in mode to prune away children
    if seen_clock_leaf:
      if token == '}': 
        if stack == 0: # if this } is for the clock leaf
          seen_clock_leaf = False
          pruned_route.append(token)
          print(f'end CLK_LEAF at {i}, stack = {stack}')
        else:
          stack -= 1
      elif token == '{':
        stack += 1
      else:
        pass

    else:
      pruned_route.append(token)

    # after we visit a CLK_LEAF, prune away the children of CLK_LEAF
    if token.endswith('CLK_LEAF'):
      assert not seen_clock_leaf
      seen_clock_leaf = True

  # To view the results: organizeHier('  '.join(pruned_route))
  new_route = '  '.join(pruned_route)
  open('apply_ooc_clock_route.tcl', "w").write(f'set_property ROUTE {new_route} [get_nets ap_clk]')
  
def getMainScriptOfGlobalClockRouting(empty_ref_checkpoint):
  main = []

  clock_route_file = 'global_clock_route.txt'

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

  main.append(f'set clock_route_file [open {clock_route_file} "w" ]')
  main.append(f'set clock_route [get_property ROUTE [get_nets ap_clk] ]')
  main.append(f'puts $clock_route_file $clock_route')
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
  opt_dir = f'{base_dir}/opt_test'

  clock_dir = f'{base_dir}/clock_routing'
  os.mkdir(clock_dir)

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
  
if __name__ == '__main__':
  assert len(sys.argv) == 4, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  option = sys.argv[3]

  hub = json.loads(open(hub_path, 'r').read())

  anchor_net_extractions_script = '/home/einsx7/auto-parallel/src/tcl/extractBoundaryNets.tcl'
  current_path = os.path.dirname(os.path.realpath(__file__))
  empty_ref_checkpoint = f'{current_path}/../../../checkpoint/empty_U250.dcp'

  if option == 'ExtractSample':
    extractSampleNetsFromSlots(hub, base_dir, anchor_net_extractions_script, empty_ref_checkpoint)
  elif option == 'GlobalClockRouting':
    globalClockRouting(hub, base_dir, empty_ref_checkpoint)
  elif option == 'PruneClockLeaf':
    pruneLeaf('global_clock_route.txt')
  else:
    assert False