import click
import json
from pyverilog.vparser.parser import parse

from rapidstream.hierarchy_rebuild.group_vertices import group_vertices
from rapidstream.hierarchy_rebuild.group_inbound_streams import group_inbound_streams
from rapidstream.parser.tapa_parser import parse_tapa_output_rtl
from rapidstream.opt import islandize_vertices
from rapidstream.rtl_gen.top import get_top
from rapidstream.util import setup_logging, create_xo, dump_files

@click.command()
@click.option(
  '--top-rtl-path',
  required=True,
  help='Path to the top-level RTL generated by TAPA.'
)
@click.option(
  '--post-floorplan-config-path',
  required=True,
  help='Path to the configuration file generated by AutoBridge.'
)
@click.option(
  '--top-name',
  required=True,
  help='Name of the top function.'
)
@click.option(
  '--xo-path',
  required=True,
  help='the xo file created by tapa.'
)
@click.option(
  '--output-dir',
  required=True,
)
def main(
  top_rtl_path: str,
  post_floorplan_config_path: str,
  top_name: str,
  xo_path: str,
  output_dir: str,
):
  """Entry point for RapidStream that targets TAPA"""

  setup_logging()

  config = json.load(open(post_floorplan_config_path, 'r'))
  ast_root, directives = parse([top_rtl_path])

  parse_tapa_output_rtl(config, ast_root)

  open('after_tapa_parsing.json', 'w').write(json.dumps(config, indent=2))

  name_to_file = islandize_vertices(config, '.', top_name)
  create_xo(top_name, xo_path, name_to_file, output_dir)
  dump_files(name_to_file, output_dir)

  open('after_rs_codegen.json', 'w').write(json.dumps(config, indent=2))

if __name__ == '__main__':
  main()
