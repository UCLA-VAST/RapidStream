from rapidstream.platform.const import CR_Y_TO_LAGUNA_RANGE_Y, GET_CR_X_TO_LAGUNA_RANGE

def get_pblock_range(
    resource: str,
    beg_x: int,
    end_x: int,
    beg_y: int,
    end_y: int,
) -> str:
  return f'{resource}_X{beg_x}Y{beg_y}:{resource}_X{end_x}Y{end_y}'


def get_laguna_in_clock_region(x: int, y: int) -> str:
  """get the laguna range in the given clock region"""
  if y not in CR_Y_TO_LAGUNA_RANGE_Y:
    return ''
  else:
    beg_y, end_y = CR_Y_TO_LAGUNA_RANGE_Y[y]
    beg_x, end_x = GET_CR_X_TO_LAGUNA_RANGE(x)
    return get_pblock_range('LAGUNA', beg_x, beg_y, end_x, end_y)
