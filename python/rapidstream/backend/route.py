import click
import json
import os
import shutil
from typing import Dict, List

from .util import ParallelManager

@click.command()
@click.option(
  '--config-path',
  required=True,
  help='Path to the TAPA configuration file.'
)
@click.option(
  '--overlay-dir',
  required=True,
)
@click.option(
  '--route-dir',
  required=True,
)
@click.option(
  '--place-opt-dir',
  required=True,
)
@click.option(
  '--top-name',
  required=True,
)
def setup_island_route(
    config_path: str,
    overlay_dir: str,
    route_dir: str,
    place_opt_dir: str,
    top_name: str,
):
  config_path = os.path.abspath(config_path)
  config = json.loads(open(config_path, 'r').read())
  setup_island_route_inner(
    config,
    overlay_dir,
    route_dir,
    place_opt_dir,
    top_name,
  )

def setup_island_route_inner(
    config: Dict,
    overlay_dir: str,
    route_dir: str,
    place_opt_dir: str,
    top_name: str,
    vitis_config_dir = '/share/einsx7/vast-lab-tapa/RapidStream/platform/u280/vitis_config_int/int',
):
  """"""
  overlay_dir = os.path.abspath(overlay_dir)
  route_dir = os.path.abspath(route_dir)
  place_opt_dir = os.path.abspath(place_opt_dir)

  if os.path.exists(route_dir):
    shutil.rmtree(route_dir)
  os.mkdir(route_dir)

  mng = ParallelManager()
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{route_dir}/{slot_name}')

    script = []
    script.append(f'open_checkpoint {overlay_dir}/overlay.dcp')
    script.append(f'lock_design -unlock -level routing')
    script.append(f'update_design -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} -black_box')
    script.append(f'lock_design -level routing')
    script.append(f'read_checkpoint -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {place_opt_dir}/{slot_name}/{slot_name}_island_place.dcp')

    # set false path from place holder FFs to top-level IOs
    script.append('set top_io_place_holder_ff [get_cells -hierarchical -regexp -filter { PRIMITIVE_TYPE =~ REGISTER.*.* && NAME =~  ".*_ff$.*" && NAME =~  ".*_axi_.*" } ]')
    script.append('if { [ llength ${top_io_place_holder_ff} ] > 0 } {')
    script.append('  set_false_path -from [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*C"}]')
    script.append('  set_false_path -to [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*D"}]')
    script.append('  set_false_path -hold -from [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*C"}]')
    script.append('  set_false_path -hold -to [get_pins -of_objects ${top_io_place_holder_ff} -filter {NAME =~ "*D"}]')
    script.append('}')

    # set false path from place holder FFs in other islands
    # if an FDRE has _anchor_reg in its name, and does not have the slot name in its parent cell name
    # then it is a place holder FF in other islands
    script.append(f'set place_holder_ff [get_cells -hierarchical -regexp -filter {{ PRIMITIVE_TYPE =~ REGISTER.*.* && NAME =~  ".*_anchor_reg.*" && PARENT !~  ".*{slot_name}.*" }} ]')
    script.append('set_false_path -from [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*C"}]')
    script.append('set_false_path -to [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*D"}]')
    script.append('set_false_path -hold -from [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*C"}]')
    script.append('set_false_path -hold -to [get_pins -of_objects ${place_holder_ff} -filter {NAME =~ "*D"}]')

    script.append(f'catch {{route_design}}')
    script.append(f'write_checkpoint {slot_name}_routed.dcp')

    if slot_name == 'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3':
      # generate bitstream for the overlay
      script.append(f'pr_recombine -cell pfm_top_i/dynamic_region/{top_name}/inst')
      script.append(f'pr_recombine -cell pfm_top_i/dynamic_region')
      script.append(f'write_bitstream -cell pfm_top_i/dynamic_region {slot_name}.bit')
    else:
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


if __name__ == '__main__':
  setup_island_route()
