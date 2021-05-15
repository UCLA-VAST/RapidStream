import sys
import json
import os

def routeWithGivenClock(hub, clock_dir, opt_dir, routing_dir):
  """
  Run the final routing of each slot with the given clock network
  """
  os.mkdir(routing_dir)

  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{routing_dir}/{slot_name}')

    script = []
    script.append(f'open_checkpoint {opt_dir}/{slot_name}/{slot_name}_post_placed_opt.dcp')
    script.append(f'source -notrace {clock_dir}/global_clock_routing/apply_ooc_clock_route.tcl')
    script.append(f'set_property IS_ROUTE_FIXED 1 [get_nets ap_clk]')

    # relax placement pblocks
    script.append(f'delete_pblock [get_pblocks *]')
    script.append(f'create_pblock {slot_name}')
    pblock_def = slot_name.replace('CR', 'CLOCKREGION').replace('_To_', ':')
    script.append(f'resize_pblock [get_pblocks {slot_name}] -add {pblock_def}')
    script.append(f'set_property CONTAIN_ROUTING 1 [get_pblocks {slot_name}]')
    script.append(f'add_cells_to_pblock [get_pblocks {slot_name}] [get_cells {slot_name}_U0]')

    script.append(f'route_design')
    # sometimes phys_opt_design make things worse, probably because of the fixed clock
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/routed_with_ooc_clock.dcp')
    script.append(f'phys_opt_design')
    script.append(f'write_checkpoint -force {routing_dir}/{slot_name}/phys_opt_routed_with_ooc_clock.dcp')

    open(f'{routing_dir}/{slot_name}/route_with_ooc_clock.tcl', "w").write('\n'.join(script))

  # generate the gnu parallel tasks
  parallel_txt = open(f'{routing_dir}/parallel-route-with-ooc-clock.txt', "w")
  vivado = 'VIV_VER=2020.1 vivado -mode batch -source'
  all_tasks = [f'cd {routing_dir}/{slot_name} && {vivado} route_with_ooc_clock.tcl' \
                for slot_name in hub['SlotIO'].keys()]
  parallel_txt.write('\n'.join(all_tasks))

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  clock_dir = f'{base_dir}/clock_routing'
  opt_dir = f'{base_dir}/opt_test'
  routing_dir = f'{base_dir}/slot_routing'

  hub = json.loads(open(hub_path, 'r').read())
  routeWithGivenClock(hub, clock_dir, opt_dir, routing_dir)
