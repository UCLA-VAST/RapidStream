import json
import re
import sys
import os
from collections import defaultdict
from mip import Model, minimize, CONTINUOUS, xsum
from autoparallel.BE.CreatePairwiseWrapper import CreateWrapperForSlotPair
from autoparallel.BE.CreateVivadoRun import createClockXDC

def setupAnchorConnectionExtraction(hub, anchor_placement_dir, get_slot_dcp_path, anchor_connection_extraction_script_path):
  """
  open each placed slot, extract which cells connect to the anchors
  """

  tasks = []

  for slot_name in hub['SlotIO'].keys():
    result_dir = f'{anchor_placement_dir}/{slot_name}'
    src_dcp_path = get_slot_dcp_path(slot_name)

    os.mkdir(result_dir)

    script = []
    script.append(f'open_checkpoint {src_dcp_path}')
    script.append(f'source {anchor_connection_extraction_script_path}')

    open(f'{result_dir}/extract_anchor_connection.tcl', 'w').write('\n'.join(script))

    tasks.append(f'cd {result_dir} && VIV_VER=2020.1 vivado -mode batch -source extract_anchor_connection.tcl')

  open(f'{anchor_placement_dir}/parallel-extraction.txt', 'w').write('\n'.join(tasks))

if __name__ == '__main__':
  assert len(sys.argv) == 3, 'input (1) the path to the front end result file; (2) the target directory; (3) which action'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  hub = json.loads(open(hub_path, 'r').read())

  anchor_placement_dir = f'{base_dir}/parallel_ILP_anchor_placement'
  os.mkdir(anchor_placement_dir)

  current_path = os.path.dirname(os.path.realpath(__file__))
  extraction_script_path = f'{current_path}/../../../tcl/extractSrcAndDstOfAnchors.tcl'

  slot_placement_dir = f'{base_dir}/parallel_run'
  get_slot_dcp_path = lambda slot_name : f'{slot_placement_dir}/{slot_name}/{slot_name}_placed_free_run/{slot_name}_placed_free_run.dcp'
  setupAnchorConnectionExtraction(hub, anchor_placement_dir, get_slot_dcp_path, extraction_script_path)