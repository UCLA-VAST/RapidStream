from typing import Dict
from rapidstream.hierarchy_rebuild.gen_wrapper_io_property import generate_no_ctrl_vertex_io_list

# how to route from the bottom right island to each island
TOPOLOGY = {
  'WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11': [
    'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3',
    'WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3',
    'WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7',
  ],
  'WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7': [
    'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3',
    'WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3',
  ],
  'WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7': [
    'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3',
  ],
  'WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3': [
    'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3',
  ],
  'WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11': [
    'CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3',
    'WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7',
  ],
}

def hard_code_embed_ctrl_signals(config: Dict) -> None:
  """Make sure that ap signals jump from island only to adjacent islands
     Must be run before generating the group wrapper
  """
  for island, props in config['vertices'].items():
    props['port_wire_map']['passing_constants'] = []

  for ap_signal in ('ap_start', 'ap_rst_n', 'ap_done'):
    dir1, dir2 = 'input', 'output'
    if ap_signal == 'ap_done':
      dir1, dir2 = dir2, dir1

    # for WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11
    config['vertices']['WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3']['port_wire_map']['passing_constants'] += [
      {
        dir1: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11',
        dir2: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q1',
      },
    ]
    config['vertices']['WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7']['port_wire_map']['passing_constants'] += [
      {
        dir1: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q1',
        dir2: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q2',
      },
    ]
    config['wire_decl'][f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q1'] = ''
    config['wire_decl'][f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q2'] = ''
    config['vertices']['WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11']['port_wire_map']['ctrl_ports'][ap_signal] = f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y8_To_CR_X3Y11_q2'

    # for WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7
    config['vertices']['WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3']['port_wire_map']['passing_constants'] += [
      {
        dir1: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7',
        dir2: f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7_q1',
      },
    ]
    config['wire_decl'][f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7_q1'] = ''
    config['vertices']['WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7']['port_wire_map']['ctrl_ports'][ap_signal] = f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y4_To_CR_X3Y7_q1'


    # for WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11
    config['vertices']['WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7']['port_wire_map']['passing_constants'] += [
      {
        dir1: f'{ap_signal}_WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11',
        dir2: f'{ap_signal}_WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11_q1',
      },
    ]
    config['wire_decl'][f'{ap_signal}_WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11_q1'] = ''
    config['vertices']['WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11']['port_wire_map']['ctrl_ports'][ap_signal] = f'{ap_signal}_WRAPPER_VERTEX_CR_X4Y8_To_CR_X7Y11_q1'

    # for WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7
    config['vertices']['WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7']['port_wire_map']['ctrl_ports'][ap_signal] = f'{ap_signal}_WRAPPER_VERTEX_CR_X4Y4_To_CR_X7Y7'

    # for WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3
    config['vertices']['WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3']['port_wire_map']['ctrl_ports'][ap_signal] = f'{ap_signal}_WRAPPER_VERTEX_CR_X0Y0_To_CR_X3Y3'


  # update io list
  for island, props in config['vertices'].items():
    if props['category'] in ('CTRL_VERTEX', 'PORT_VERTEX'):
      continue

    generate_no_ctrl_vertex_io_list(props)
