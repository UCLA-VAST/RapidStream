import coloredlogs
import logging
import os
from typing import Optional, Dict

_logger = logging.getLogger().getChild(__name__)


def setup_logging(verbose: Optional[int] = None,
                  quiet: Optional[int] = None) -> None:
  verbose = 0 if verbose is None else verbose
  quiet = 0 if quiet is None else quiet
  logging_level = (quiet - verbose) * 10 + logging.DEBUG
  logging_level = max(logging.DEBUG, min(logging.CRITICAL, logging_level))

  coloredlogs.install(
      level=logging_level,
      fmt='[%(levelname)s %(name)s:%(lineno)d] %(message)s',
      datefmt='%m%d %H:%M:%S.%f',
  )

  # filename = os.path.join(log_dir, basename)
  handler = logging.FileHandler('rapidstream.log', encoding='utf-8')
  handler.setFormatter(
      logging.Formatter(
          fmt=('[%(levelname)s '
               '%(name)s:%(lineno)d] %(message)s'),
          datefmt='%m%d %H:%M:%S',
      ))
  handler.setLevel(logging.DEBUG)
  logging.getLogger().addHandler(handler)

  _logger.info('logging level set to %s', logging.getLevelName(logging_level))


def create_xo(top_name: str, old_xo_path: str, name_to_file: Dict, output_dir: str, xo_suffix: str, temp_dir: str):
  """Create a new xo file that includes the new RTL files"""
  temp_dir = f'{output_dir}/{temp_dir}'
  os.system(f'rm -rf {temp_dir}/')
  os.system(f'mkdir -p {temp_dir}/')
  os.system(f'cp {old_xo_path} {temp_dir}/')
  os.system(f'unzip {temp_dir}/{top_name}.xo -d {temp_dir}/')
  os.system(f'rm {temp_dir}/{top_name}.xo')

  # xosim requires that the top rtl file only contains logic for the top module
  xo_rtl_path = f'{temp_dir}/ip_repo/haoda_xrtl_{top_name}_1_0/src/'
  top_rtl_name = f'{top_name}.v'
  victim_file = f'{top_name}_inner.v'

  with open(f'{xo_rtl_path}/{top_rtl_name}', 'w') as top:
    _logger.info(f'overwrite the top-level module in {top_rtl_name}')
    top.write('\n'.join(name_to_file[top_rtl_name]))

  # put the rest of the wrapper rtl files in another existing rtl file
  with open(f'{xo_rtl_path}/{victim_file}', 'w') as top:
    for name, file in name_to_file.items():
      if name != top_rtl_name:
        _logger.info(f'add wrapper file {name} into {victim_file}')
        top.write('\n'.join(file))

  os.system(f'cd {temp_dir}/; zip -r {top_name}{xo_suffix}.xo *; cd -')
  os.system(f'mv {temp_dir}/{top_name}{xo_suffix}.xo {output_dir}/')


def dump_files(name_to_file: Dict, output_dir: str):
  os.system(f'mkdir -p {output_dir}')
  for name, file in name_to_file.items():
    open(f'{output_dir}/{name}', 'w').write('\n'.join(file))
