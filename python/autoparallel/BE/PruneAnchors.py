import sys
import json
import os

def pruneAnchors(hub, pruning_dir, routing_dir, pruning_script_path):
  """
  Run the final routing of each slot with the given clock network
  """
  os.mkdir(pruning_dir)

  commands = []
  for slot_name in hub['SlotIO'].keys():
    os.mkdir(f'{pruning_dir}/{slot_name}')

    script = []
    script.append(f'open_checkpoint {routing_dir}/{slot_name}/routed_with_ooc_clock.dcp')

    # unroute the routes in anchor regions
    script.append(f'set anchor_region_cells [get_cells -hierarchical -regexp -filter {{ PBLOCK !~ "{slot_name}" && PRIMITIVE_TYPE !~ OTHERS.*.* }} ]')
    script.append(f'route_design -unroute -nets [get_nets -of_objects $anchor_region_cells -filter {{ TYPE != "GROUND" && TYPE != "POWER"}}]')

    script.append(f'source {pruning_script_path}')

    script.append(f'write_checkpoint {pruning_dir}/{slot_name}/{slot_name}_after_pruning_anchors.dcp')

    open(f'{pruning_dir}/{slot_name}/pruning_anchors.tcl', 'w').write('\n'.join(script))
    commands.append(f'cd {pruning_dir}/{slot_name} && VIV_VER=2020.1 vivado -mode batch -source pruning_anchors.tcl')

  open(f'{pruning_dir}/parallel-pruning-anchors.txt', 'w').write('\n'.join(commands))

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  routing_dir = f'{base_dir}/slot_routing'
  pruning_dir = f'{base_dir}/pruning_anchors'

  current_path = os.path.dirname(os.path.realpath(__file__))
  pruning_script_path = f'{current_path}/../../../tcl/removeAnchorRegs.tcl'

  hub = json.loads(open(hub_path, 'r').read())
  pruneAnchors(hub, pruning_dir, routing_dir, pruning_script_path)