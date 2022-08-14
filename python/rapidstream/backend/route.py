import click
import json
import os
import shutil

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
  """"""
  config = json.loads(open(config_path, 'r').read())
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
    script.append(f'route_design')
    script.append(f'write_checkpoint {slot_name}_routed.dcp')
    script.append(f'write_bitstream -cell pfm_top_i/dynamic_region/{top_name}/inst/{slot_name} {slot_name}.bit')

    open(f'{route_dir}/{slot_name}/route_island.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{route_dir}/{slot_name}/', 'route_island.tcl')

  open(f'{route_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))


if __name__ == '__main__':
  setup_island_route()
