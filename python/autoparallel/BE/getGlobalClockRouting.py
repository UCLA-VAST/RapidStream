import json
import sys
import os

def testIndividualClockRouting(hub, base_dir, anchor_net_extractions_script):
  """
  For test purpose. 
  Extract the anchor nets of each slot and route the clock net
  Then enforce this clock net on the slot and route the entire slot
  check if quality of the clock net obtained in this way
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
    script.append(f'open_checkpoint /home/einsx7/auto-parallel/src/clock/test_clock.dcp')
    script.append(f'source {clock_dir}/{slot_name}/sample_connection.tcl')
    script.append(f'route_design')
    script.append(f'set clock_route_file [open {clock_dir}/{slot_name}/ooc_clock_route.tcl "w" ]')
    script.append(f'set clock_route [get_property ROUTE [get_nets ap_clk] ]')
    script.append(f'puts $clock_route_file "set_property ROUTE $clock_route \[get_nets ap_clk\]"')
    script.append(f'close $clock_route_file')
    script.append(f'exit')

    open(f'{clock_dir}/{slot_name}/setup_ooc_clock_route.tcl', "w").write('\n'.join(script))

    # the final routing
    script = []
    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')
    script.append(f'source {clock_dir}/{slot_name}/ooc_clock_route.tcl')
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
    script.append(f'write_checkpoint {clock_dir}/{slot_name}/routed_with_ooc_clock.dcp')

    open(f'{clock_dir}/{slot_name}/run_ooc_clock_route.tcl', "w").write('\n'.join(script))

  # generate the gnu parallel tasks
  parallel_txt = open(f'{clock_dir}/parallel-test-all.txt', "w")
  vivado = 'VIV_VER=2020.1 vivado -mode batch -source'
  all_tasks = [f'cd {clock_dir}/{slot_name} && {vivado} setup_ooc_clock_route.tcl && {vivado} run_ooc_clock_route.tcl' \
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
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())
  os.mkdir(f'{base_dir}/clock_routing')

  anchor_net_extractions_script = '/home/einsx7/auto-parallel/src/tcl/extractBoundaryNets.tcl'

  testIndividualClockRouting(hub, base_dir, anchor_net_extractions_script)