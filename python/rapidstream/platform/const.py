CR_Y_TO_LAGUNA_RANGE_Y = {
  3: (0, 119),
  4: (120, 239),
  7: (240, 359),
  8: (360, 479),
}

def GET_CR_X_TO_LAGUNA_RANGE(x: int):
  return (4*x, 4*x+3)

ISLAND_ORIENTATIONS = (
  'NORTH',
  'SOUTH',
  'WEST' ,
  'EAST' ,
)

ISLAND_TOPOLOGY = {
  'CR_X0Y8_To_CR_X3Y11' : {
    'NORTH': '',
    'SOUTH': 'CR_X0Y4_To_CR_X3Y7',
    'WEST' : '',
    'EAST' : 'CR_X4Y8_To_CR_X7Y11',
  },
  'CR_X0Y4_To_CR_X3Y7': {
    'NORTH': 'CR_X0Y8_To_CR_X3Y11',
    'SOUTH': 'CR_X0Y0_To_CR_X3Y3',
    'WEST' : '',
    'EAST' : 'CR_X4Y4_To_CR_X7Y7',
  },
  'CR_X0Y0_To_CR_X3Y3': {
    'NORTH': 'CR_X0Y4_To_CR_X3Y7',
    'SOUTH': 'CR_X4Y0_To_CR_X7Y3',
    'WEST' : '',
    'EAST' : '',
  },
  'CR_X4Y8_To_CR_X7Y11': {
    'NORTH': '',
    'SOUTH': 'CR_X4Y4_To_CR_X7Y7',
    'WEST' : 'CR_X0Y8_To_CR_X3Y11',
    'EAST' : '',
  },
  'CR_X4Y4_To_CR_X7Y7': {
    'NORTH': 'CR_X4Y8_To_CR_X7Y11',
    'SOUTH': 'CR_X4Y0_To_CR_X7Y3',
    'WEST' : 'CR_X0Y4_To_CR_X3Y7',
    'EAST' : '',
  },
  'CR_X4Y0_To_CR_X7Y3': {
    'NORTH': 'CR_X4Y4_To_CR_X7Y7',
    'SOUTH': '',
    'WEST' : 'CR_X0Y0_To_CR_X3Y3',
    'EAST' : '',
  },
}
