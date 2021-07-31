import logging
from typing import List

from autobridge.Opt.Slot import Slot
from autobridge.Device.DeviceManager import DeviceU250
U250_inst = DeviceU250()

root = logging.getLogger()
root.setLevel(logging.DEBUG)

BEND_COUNT_LIMIT = 2
VERTICAL_BOUNDARY_CAPACITY = 5280
SLR_CROSSING_BOUNDARY_CAPACITY = 5760
NON_SLR_CROSSING_HORIZONTAL_BOUNDARY = 9440


class RoutingVertex:
  def __init__(self, slot_name):
    self.slot_name = slot_name
    self.slot = Slot(U250_inst, slot_name)
    self.edges = []
    self.neighbors = set()

  def __eq__(self, other):
    return self.slot_name == other.slot_name

  def __hash__(self):
    return hash(self.slot_name)

  def getDownLeftX(self):
    return self.slot.down_left_x

  def getDownLeftY(self):
    return self.slot.down_left_y


class RoutingEdge:
  def __init__(self, v1: RoutingVertex, v2: RoutingVertex, capacity):
    self.vertices = [v1, v2]
    self.capacity = capacity
    v1.edges.append(self)
    v2.edges.append(self)
    v1.neighbors.add(v2)
    v2.neighbors.add(v1)


class RoutingPath:
  """
  a path contains the vertcies it passed through
  """

  def __init__(
      self, 
      vertices: List[RoutingVertex], 
      bend_count: int, 
      length_limit: int, 
      data_width: int,
  ) -> None:
    self.vertices = vertices
    self.bend_count = bend_count
    self.length_limit = length_limit
    self.data_width = data_width

  def _isBend(self, prev, curr, next) -> bool:
    """
    check if three vertices are aligned either vertically or horizontally
    """
    if prev.getDownLeftX() == curr.getDownLeftX() and \
       next.getDownLeftX() == curr.getDownLeftX():
      return True
    elif prev.getDownLeftY() == curr.getDownLeftY() and \
         next.getDownLeftY() == curr.getDownLeftY():
      return True
    else:
      return False

  def getChildPaths(self) -> List['RoutingPath']:
    """
    extend the current path for one more vertex.
    Filter out candidates if the bend count is over the limit
    """
    curr = self.vertices[-1]
    # if the path only has one vertex, set prev to curr to be compatible with bend test
    if len(self.vertices) == 1:
      prev = curr
    else:
      prev = self.vertices[-2]

    # if a path is too long, stop generating child paths
    if len(self.vertices) >= self.length_limit:
      return []

    # attempt to extend one more context from the current tail
    child_paths = []
    for next in curr.neighbors:
      if next != prev:
        new_bend_count = self.bend_count + int(self._isBend(prev, curr, next))

        # limit on bend count
        if new_bend_count > BEND_COUNT_LIMIT:
          continue
        
        child_paths.append(
          RoutingPath(
            self.vertices + [next], 
            new_bend_count, 
            self.length_limit, 
            self.data_width)
        )
    return child_paths

  def getDest(self) -> RoutingVertex:
    """
    get the current tail vertex of the path
    """
    return self.vertices[-1]

  def printPath(self):
    logging.info(f'path from {self.vertices[0].slot_name} to {self.vertices[-1].slot_name} ')
    for v in self.vertices:
      logging.info(f' => {v.slot_name}')


class RoutingGraph:
  def __init__(self):
    self.slot_name_to_vertex = {}
    self.edges = []
    self._getRoutingGraphForU250()

  def _getRoutingGraphForU250(self):
    """
    hardcode the routing graph for U250
    assume slots are 2x2
    """
    
    # create all vertices
    for x in range(0, 8, 2):
      for y in range(0, 16, 2):
        slot_name = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        self.slot_name_to_vertex[slot_name] = RoutingVertex(slot_name)

    # create all edges for vertical boundaries
    for y in range(0, 16, 2):
      for x in range(0, 6, 2):
        left_slot = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        right_slot = f'CR_X{x+2}Y{y}_To_CR_X{x+3}Y{y+1}'
        v1 = self.slot_name_to_vertex[left_slot]
        v2 = self.slot_name_to_vertex[right_slot]

        e = RoutingEdge(v1, v2, VERTICAL_BOUNDARY_CAPACITY)
        self.edges.append(e)

    # create all edges for slr crossing boundaries
    for x in range(0, 8, 2):
      for y in range(2, 12, 4):
        lower_slot = left_slot = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        upper_slot = left_slot = f'CR_X{x}Y{y+2}_To_CR_X{x+1}Y{y+3}'
        v_lower = self.slot_name_to_vertex[lower_slot]
        v_upper = self.slot_name_to_vertex[upper_slot]

        e = RoutingEdge(v_lower, v_upper, SLR_CROSSING_BOUNDARY_CAPACITY)
        self.edges.append(e)

    # create all edges for non-slr-crossing horizontal boundaries
    for x in range(0, 8, 2):
      for y in range(0, 16, 4):
        lower_slot = left_slot = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        upper_slot = left_slot = f'CR_X{x}Y{y+2}_To_CR_X{x+1}Y{y+3}'
        v_lower = self.slot_name_to_vertex[lower_slot]
        v_upper = self.slot_name_to_vertex[upper_slot]

        e = RoutingEdge(v_lower, v_upper, NON_SLR_CROSSING_HORIZONTAL_BOUNDARY)
        self.edges.append(e)

  def _getShortestDist(self, src: RoutingVertex, dst: RoutingVertex):
    dist_x = abs(src.getDownLeftX() - dst.getDownLeftX() ) / 2
    dist_y = abs(src.getDownLeftY() - dst.getDownLeftY() ) / 2
    return dist_x + dist_y

  def findAllPaths(self, src_slot: str, dst_slot: str, data_width: int) -> List[RoutingPath]:
    """
    run BFS to get all paths that satisfy the requirement
    """
    src = self.slot_name_to_vertex[src_slot]
    dst = self.slot_name_to_vertex[dst_slot]
    shortest_dist = self._getShortestDist(src, dst)

    init_path = RoutingPath([src], 0, shortest_dist + 4, data_width)
    queue = [init_path]

    paths = []
    while queue:
      curr_path = queue.pop(0)

      if curr_path.getDest() != dst:
        queue += curr_path.getChildPaths()
      else:
        paths.append(curr_path)

    return paths
