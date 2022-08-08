import click

from .util import get_pairing_laguna_tx

@click.command()
@click.option(
  '--rx-list',
  required=True,
)
def block_pre_existing_lagunas(rx_list: str):
  """extract bleed over nets from static region that uses lagunas"""
  file = open(rx_list, 'r').readlines()
  rx_list = (rx_loc.strip('\n') for rx_loc in file)

  rx_tx_pairs = [(rx_loc, get_pairing_laguna_tx(rx_loc)) for rx_loc in rx_list]

  script = []
  script.append('create_cell -reference FDRE { \\')
  for rx_loc, tx_loc in rx_tx_pairs:
    script.append(f'  placeholder_RX_{rx_loc.replace("/", "_")} \\')
    script.append(f'  placeholder_TX_{tx_loc.replace("/", "_")} \\')
  script.append('}')

  script.append('create_net { \\')
  for rx_loc, tx_loc in rx_tx_pairs:
    script.append(f'  placeholder_net_{rx_loc.replace("/", "_")} \\')
  script.append('}')

  script.append('set nets_to_connect []')
  for rx_loc, tx_loc in rx_tx_pairs:
    script.append(f'lappend nets_to_connect [get_nets placeholder_net_{rx_loc.replace("/", "_")}]')
    script.append(f'lappend nets_to_connect [get_pins placeholder_RX_{rx_loc.replace("/", "_")}/D ]')

    script.append(f'lappend nets_to_connect [get_nets placeholder_net_{rx_loc.replace("/", "_")}]')
    script.append(f'lappend nets_to_connect [get_pins placeholder_TX_{tx_loc.replace("/", "_")}/Q ]')
  script.append('connect_net -dict $nets_to_connect')

  script.append(f'connect_net -net ap_clk -objects [get_pins placeholder*/C]')

  script.append('place_cell { \\')
  for rx_loc, tx_loc in rx_tx_pairs:
    script.append(f'  placeholder_RX_{rx_loc.replace("/", "_")} {rx_loc} \\')
    script.append(f'  placeholder_TX_{tx_loc.replace("/", "_")} {tx_loc} \\')
  script.append('}')

  open('add_laguna_blocks.tcl', 'w').write('\n'.join(script))


if __name__ == '__main__':
  block_pre_existing_lagunas()
