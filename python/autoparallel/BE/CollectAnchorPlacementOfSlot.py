import sys
import json
from autoparallel.BE.CreateAnchorWrapper import getAnchoredIOAndWiredIO, getStrictAnchoredIO
from autoparallel.BE.LegalizeAnchorPlacement import getAnchorSourceNameFromFDRE

def getAnchorPlacementFiles(hub, slot_name, base_dir):
  """
  get all slot pairs that include this slot
  """
  pair_list = hub["AllSlotPairs"]
  pair_name_list = ['_AND_'.join(pair) for pair in pair_list]
  local_pairs = [pair_name for pair_name in pair_name_list if slot_name in pair_name]

  stitch_run_dir = base_dir + '/parallel_stitch'
  anchor_placement_files = [f'{stitch_run_dir}/{pair}/{pair}_anchor_placement.json' for pair in local_pairs]
  return anchor_placement_files

def __checkAnchors(hub, local_anchor_placement):
  """
  check the collected anchors are matching to what the RTL should generate
  """
  in_slot_pipeline_style = hub['InSlotPipelineStyle']

  if  in_slot_pipeline_style == 'LUT' or \
      in_slot_pipeline_style == 'WIRE' or \
      in_slot_pipeline_style == 'DOUBLE_REG':
    anchored_io = getAnchoredIOAndWiredIO(hub, slot_name) # note that passing wires are also anchored
  elif in_slot_pipeline_style == 'REG':
    anchored_io = getStrictAnchoredIO(hub, slot_name)
  else:
    assert False

  anchor_names = set(io[-1]+'_q0' for io in anchored_io)

  for FDRE in local_anchor_placement.keys():
    anchor_source_name = getAnchorSourceNameFromFDRE(FDRE)
    assert anchor_source_name in anchor_names

def asyncGetSlotAnchorPlacementScript(hub, slot_name, base_dir):
  """ 
  merge the locations of anchors of the current slot 
  """
  anchor_placement_files = getAnchorPlacementFiles(hub, slot_name, base_dir)
  local_anchor_placement = {}
  for file in anchor_placement_files:
    partial_anchors = json.loads(open(file, 'r').read())
    local_anchor_placement.update(partial_anchors)

  # safety check
  __checkAnchors(hub, local_anchor_placement)

  script = []
  script.append('place_cell { \\')
  for FDRE, loc in local_anchor_placement.items():
    script.append(f'  {FDRE} {loc} \\')
  script.append('}')

  return script


def getParallelMonitorScript(hub, hub_path, base_dir):
  all_tasks = []

  for slot_name in hub['SlotIO'].keys():
    # find all anchor files to the slot
    anchor_placement_files = getAnchorPlacementFiles(hub, slot_name, base_dir)
    
    # wait until they are ready
    # note that we check the flag files to prevent race conditions
    guard = 'until [[ ' + ' && '.join(f' -f {anchor_file}.done.flag ' for anchor_file in anchor_placement_files) + ' ]] ; do sleep 10; done'
    
    # merge the anchors together, trigger slot opt process
    command = f'{guard} && python3.6 -m autoparallel.BE.CollectAnchorPlacementOfSlot {hub_path} {base_dir} {slot_name}'
    
    all_tasks.append(command)

  open(f'{base_dir}/parallel_stitch/parallel-monitor-progress.txt', 'w').write('\n'.join(all_tasks))

if __name__ == '__main__':
  """
  monitors the progress of anchor placement
  If all anchors of a slot are ready, collect them and fire the slot opt process
  """

  assert len(sys.argv) >= 3, 'input (1) the path to the front end result file and (2) the target directory'

  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())
  
  if len(sys.argv) == 3:
    # execute at the beginning, produce parallel polling processes
    hub_path = sys.argv[1]
    base_dir = sys.argv[2]
    getParallelMonitorScript(hub, hub_path, base_dir)
  
  elif len(sys.argv) == 4:
    # once a polling process finishes, collect the anchors
    slot_name = sys.argv[3]
    script = asyncGetSlotAnchorPlacementScript(hub, slot_name, base_dir)

    opt_dir = base_dir + '/opt_test'
    open(f'{opt_dir}/{slot_name}/place_anchors_of_slot.tcl', 'w').write('\n'.join(script))
    open(f'{opt_dir}/{slot_name}/place_anchors_of_slot.done.flag', 'w').write('flag')
