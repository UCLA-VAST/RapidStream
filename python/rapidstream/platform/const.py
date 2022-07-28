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
