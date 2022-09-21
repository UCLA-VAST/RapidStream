import os
import shutil
from typing import Dict, List

from .util import ParallelManager, mark_false_paths_to_placeholder_ff


def setup_island_route(
    config: Dict,
    abs_shell_dir: str,
    route_dir: str,
    place_opt_dir: str,
    top_name: str,
    re_place_before_routing: bool,
    vitis_config_dir = '/share/einsx7/vast-lab-tapa/RapidStream/platform/u280/vitis_config_int/int',
    unfix_anchor_nets = False,
):
  """"""
  route_dir = os.path.abspath(route_dir)
  place_opt_dir = os.path.abspath(place_opt_dir)

  if os.path.exists(route_dir):
    shutil.rmtree(route_dir)
  os.mkdir(route_dir)

  mng = ParallelManager()
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{route_dir}/{slot_name}')

    script = []

    script.append(f'open_checkpoint {abs_shell_dir}/{slot_name}/{slot_name}_abs_shell.dcp')
    script.append(f'read_checkpoint -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {place_opt_dir}/{slot_name}/{slot_name}_island_place.dcp')

    # set false path from place holder FFs to top-level IOs and place holder FFs in other islands
    script += mark_false_paths_to_placeholder_ff(slot_name)

    # UNTESTED: make laguna anchor D/Q nets unfixed
    if unfix_anchor_nets:
      script.append('set_property IS_ROUTE_FIXED 0 [get_nets -of_objects [ get_cells pfm_top_i/dynamic_region/gaussian_kernel/inst/*q_reg* -filter {LOC =~ LAG*} ] -filter {TYPE == SIGNAL} ]')

    if re_place_before_routing:
      script.append(f'place_design -unplace')
      script.append(f'place_design -place')

    script.append(f'catch {{route_design}}')
    script.append(f'write_checkpoint {slot_name}_routed.dcp')
    script.append(f'write_checkpoint -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {slot_name}.dcp')
    script.append(f'write_bitstream -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {slot_name}.bit')

    open(f'{route_dir}/{slot_name}/route_island.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{route_dir}/{slot_name}/', 'route_island.tcl')

  open(f'{route_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))

  # setup xclbin generation
  setup_local_vitis_config_files(vitis_config_dir, route_dir)

  parallel = []
  for slot_name in config['vertices'].keys():
    xclbin_script = get_xclbin_gen_script(f'{route_dir}/int', slot_name)
    open(f'{route_dir}/{slot_name}/generate_xclbin.sh', 'w').write('\n'.join(xclbin_script))
    parallel.append(f'cd {route_dir}/{slot_name}; bash generate_xclbin.sh')

  open(f'{route_dir}/parallel_xclbin.txt', 'w').write('\n'.join(parallel))


def setup_local_vitis_config_files(
  vitis_config_dir,
  route_dir,
):
  # FIXME: adjust clock frequency based on routing result
  os.system(f'cp -r {vitis_config_dir} {route_dir}')


def get_xclbin_gen_script(
    vitis_config_dir,
    slot_name,
) -> List[str]:
  script = f'''
BASE_DIR={vitis_config_dir}
ISLAND=CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3
xclbinutil \
  --add-section DEBUG_IP_LAYOUT:JSON:${{BASE_DIR}}/debug_ip_layout.rtd \
  --add-section BITSTREAM:RAW:{slot_name}.bit \
  --force \
  --target hw \
  --key-value SYS:dfx_enable:true \
  --add-section :JSON:${{BASE_DIR}}/gaussian_kernel_xilinx_u280_xdma_201920_3.rtd \
  --append-section :JSON:${{BASE_DIR}}/appendSection.rtd \
  --add-section CLOCK_FREQ_TOPOLOGY:JSON:${{BASE_DIR}}/gaussian_kernel_xilinx_u280_xdma_201920_3_xml.rtd \
  --add-section BUILD_METADATA:JSON:${{BASE_DIR}}/gaussian_kernel_xilinx_u280_xdma_201920_3_build.rtd \
  --add-section EMBEDDED_METADATA:RAW:${{BASE_DIR}}/gaussian_kernel_xilinx_u280_xdma_201920_3_{slot_name}.xml \
  --add-section SYSTEM_METADATA:RAW:${{BASE_DIR}}/systemDiagramModelSlrBaseAddress.json \
  --output {slot_name}.xclbin
'''

  return script.split('\n')
