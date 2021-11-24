import logging
from bisect import bisect
from collections import defaultdict
from mip import Model, minimize, BINARY, xsum, OptimizationStatus, Var
from typing import List, Dict

from autobridge.Opt.DataflowGraph import Edge, Vertex
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

    v_names = [v.slot_name for v in self.vertices]
    self._name = min(v_names) + '_To_' + max(v_names) # in case the order of vertices is different

  def __hash__(self):
    return hash(self._name)

  def __eq__(self, other):
    return self._name == other._name


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
      bridge_name: str,
      util: Dict[Slot, Dict[str, float]]
  ) -> None:
    """
    a bridge is an edge in the dataflow graph. To differentiate it 
    from the edge in the routing graph, we call it a bridge
    use bridge_name to make the path unique
    """
    self.vertices = vertices
    self.bend_count = bend_count
    self.length_limit = length_limit
    self.data_width = data_width
    self.bridge_name = bridge_name
    self.util = util
    self.edges = []

    # use bridge name to make the path name unique
    self._name = self.bridge_name + '_' + '_'.join([v.slot_name for v in self.vertices])

  def __hash__(self):
    return hash(self._name)

  def __eq__(self, other):
    return self._name == other._name

  def initEdges(self):
    """
    find all edges belong to this path based on the vertices
    """
    for i in range(len(self.vertices)-1):
      curr = self.vertices[i]
      next = self.vertices[i+1]
      e_common = [bridge for bridge in curr.edges if bridge in next.edges]
      assert len(e_common) == 1
      self.edges.append(e_common[0])

  def _isBend(self, prev, curr, next) -> bool:
    """
    check if three vertices are aligned either vertically or horizontally
    """
    if prev.getDownLeftX() == curr.getDownLeftX() and \
       next.getDownLeftX() == curr.getDownLeftX():
      return False
    elif prev.getDownLeftY() == curr.getDownLeftY() and \
         next.getDownLeftY() == curr.getDownLeftY():
      return False
    else:
      return True

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
    if len(self.vertices) > self.length_limit:
      return []

    # attempt to extend one more context from the current tail
    child_paths = []
    for next in curr.neighbors:
      if next != prev: # disable u turn at the site
        new_bend_count = self.bend_count + int(self._isBend(prev, curr, next))

        # limit on bend count
        if new_bend_count > BEND_COUNT_LIMIT:
          continue
        
        child_paths.append(
          RoutingPath(
            self.vertices + [next], 
            new_bend_count, 
            self.length_limit, 
            self.data_width,
            self.bridge_name,
            self.util
          )
        )
    return child_paths

  def getDest(self) -> RoutingVertex:
    """
    get the current tail vertex of the path
    """
    return self.vertices[-1]

  def printPath(self):
    logging.debug(f'path from {self.vertices[0].slot_name} to {self.vertices[-1].slot_name} ')
    for v in self.vertices:
      logging.debug(f' => {v.slot_name}')

  def getLength(self) -> int:
    """
    number of vertices in this path
    """
    return len(self.vertices)

  def getSlotsOfPath(self) -> List[Slot]:
    """
    get all the Slot objects corresponding to the path
    """
    return [v.slot for v in self.vertices]

  def getTheoreticalShortestLength(self):
    """
    get the manhatten distance beween the source and destination slots
    the distance is the number of slots
    """
    src = self.vertices[0]
    dst = self.vertices[-1]
    dist_x = abs(src.getDownLeftX() - dst.getDownLeftX() ) / 2
    dist_y = abs(src.getDownLeftY() - dst.getDownLeftY() ) / 2
    return dist_x + dist_y + 1

  def getCost(self) -> float:
    """
    calculate a cost if this slot is selected. 
    We want to pass through less utilized slots as much as possible
    use the sum of DSP and BRAM percentage of each slot * wire_length
    """
    try:
      dsp_costs = [self.util[v.slot]['DSP'] if v.slot in self.util else 0 for v in self.vertices]
      bram_costs = [self.util[v.slot]['BRAM'] if v.slot in self.util else 0  for v in self.vertices]
      lut_costs = [self.util[v.slot]['LUT'] if v.slot in self.util else 0  for v in self.vertices]
    except:
      [v.slot.getRTLModuleName() if v.slot not in self.util else '' for v in self.vertices]
      import pdb; pdb.set_trace()


    cost = (sum(dsp_costs) + sum(bram_costs) + 0.7 * sum(lut_costs)) * self.data_width

    return round(cost, 4)

  def getSrcSlotName(self) -> str:
    return self.vertices[0].slot_name

  def getDstSlotName(self) -> str:
    return self.vertices[-1].slot_name


class RoutingGraph:
  def __init__(
      self, 
      util: Dict[Slot, Dict[str, float]], 
      routing_usage_limit: int,
      detour_path_limit: int,
  ) -> None:
    self.slot_name_to_vertex = {}
    self.edges = []
    self.util = util  # resource usage of each slot
    self.routing_usage_limit = routing_usage_limit
    self.detour_path_limit = detour_path_limit
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

        e = RoutingEdge(v1, v2, int(VERTICAL_BOUNDARY_CAPACITY*self.routing_usage_limit))
        self.edges.append(e)

    # create all edges for slr crossing boundaries
    for x in range(0, 8, 2):
      for y in range(2, 12, 4):
        lower_slot = left_slot = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        upper_slot = left_slot = f'CR_X{x}Y{y+2}_To_CR_X{x+1}Y{y+3}'
        v_lower = self.slot_name_to_vertex[lower_slot]
        v_upper = self.slot_name_to_vertex[upper_slot]

        e = RoutingEdge(v_lower, v_upper, int(SLR_CROSSING_BOUNDARY_CAPACITY*self.routing_usage_limit))
        self.edges.append(e)

    # create all edges for non-slr-crossing horizontal boundaries
    for x in range(0, 8, 2):
      for y in range(0, 16, 4):
        lower_slot = left_slot = f'CR_X{x}Y{y}_To_CR_X{x+1}Y{y+1}'
        upper_slot = left_slot = f'CR_X{x}Y{y+2}_To_CR_X{x+1}Y{y+3}'
        v_lower = self.slot_name_to_vertex[lower_slot]
        v_upper = self.slot_name_to_vertex[upper_slot]

        e = RoutingEdge(v_lower, v_upper, int(NON_SLR_CROSSING_HORIZONTAL_BOUNDARY*self.routing_usage_limit))
        self.edges.append(e)

  def _getShortestDist(self, src: RoutingVertex, dst: RoutingVertex):
    """
    number of slots in the path. Include source and sink
    assume 2x2 slots
    """
    dist_x = abs(src.getDownLeftX() - dst.getDownLeftX() ) / 2
    dist_y = abs(src.getDownLeftY() - dst.getDownLeftY() ) / 2
    return dist_x + dist_y + 1

  def findAllPaths(
      self,
      src_slot: str, 
      dst_slot: str, 
      data_width: int, 
      bridge_name: str
  ) -> List[RoutingPath]:
    """
    run BFS to get all paths that satisfy the requirement
    The path include the source and destination
    """
    src = self.slot_name_to_vertex[src_slot]
    dst = self.slot_name_to_vertex[dst_slot]
    shortest_dist = self._getShortestDist(src, dst)

    init_path = RoutingPath(
      vertices = [src],
      bend_count = 0,
      length_limit = shortest_dist + self.detour_path_limit,
      data_width = data_width,
      bridge_name = bridge_name,
      util = self.util
    )

    queue = [init_path]

    paths = []
    while queue:
      curr_path = queue.pop(0)

      if curr_path.getDest() != dst:
        queue += curr_path.getChildPaths()
      else:
        curr_path.initEdges()
        paths.append(curr_path)

    assert len(set(paths)) == len(paths)
    return paths


class ILPRouter:
  def __init__(
      self, 
      bridge_list: List[Edge], 
      v2s: Dict[Vertex, Slot], 
      util: Dict[Slot, Dict[str, float]]
  ) -> None:
    """
    to avoid confusion, here we call the data transfer path betwee two slots a "bridge"
    we need to map each bridge to a set of routing edges in the routing graph
    """
    self.bridge_list = bridge_list
    self.v2s = v2s
    self.util = util

  def _getBridgeToCandidatePaths(
      self, 
      routing_usage_limit: float, 
      detour_path_limit: int
  ) -> Dict[Edge, List[RoutingPath]]:
    """
    for each edge, generate the candidate paths to select from
    """
    routing_graph = RoutingGraph(self.util, routing_usage_limit, detour_path_limit)

    bridge_to_paths = {}
    for bridge in self.bridge_list:
      src_slot_name = self.v2s[bridge.src].getRTLModuleName()
      dst_slot_name = self.v2s[bridge.dst].getRTLModuleName()
      path_candidates = routing_graph.findAllPaths(
        src_slot_name, dst_slot_name, bridge.width, bridge.name
      )

      logging.debug(f'bridge {bridge.name} has candidate paths:')
      for path in path_candidates:
        path.printPath()

      bridge_to_paths[bridge] = path_candidates

    return bridge_to_paths

  def _getRoutingEdgeToPassingPaths(
      self, bridge_to_paths: Dict[Edge, List[RoutingPath]]
  ) -> Dict[RoutingEdge, List[RoutingPath]]:
    """
    for each routing edge, get all bridge and corresponding path candidates that go through it.
    """
    routing_edge_to_paths = defaultdict(list)
    for bridge, path_list in bridge_to_paths.items():
      for path in path_list:
        for routing_edge in path.edges:
          routing_edge_to_paths[routing_edge].append(path)

    return routing_edge_to_paths

  def _getPathToVar(self, m: Model, bridge_to_paths: Dict[Edge, List[RoutingPath]]):
    """
    for each bridge, for each candidate path, 
    create a variable to represent if this candidate path is selected
    """
    path_to_var = {}
    for bridge, path_list in bridge_to_paths.items():
      for path in path_list:
        assert path not in path_to_var
        # weight matching model, relax the variable to continous
        path_to_var[path] = m.add_var(var_type=BINARY, lb=0, ub=1) 

    return path_to_var

  def _constrOnePathForOneBridge(
      self, 
      m: Model, 
      bridge_to_paths: Dict[Edge, List[RoutingPath]], 
      path_to_var: Dict[RoutingPath, Var]
  ) -> None:
    """
    for each bridge, only one candidate path is selected
    """
    for paths in bridge_to_paths.values():
      m += xsum([path_to_var[path] for path in paths]) == 1

  def _constrRoutingEdgeCapacity(
      self, 
      m: Model, 
      path_to_var: Dict[RoutingPath, Var], 
      routing_edge_to_paths: Dict[RoutingEdge, List[RoutingPath]]
  ) -> None:
    """
    for each routing edge, limit the paths that go through a routing edge
    """
    for routing_edge, paths in routing_edge_to_paths.items():
      m += xsum(path_to_var[path] * path.data_width for path in paths) <= routing_edge.capacity

  def _minimizeTotalPathArea(
      self, 
      m: Model, 
      bridge_to_paths: Dict[Edge, List[RoutingPath]], 
      path_to_var: Dict[RoutingPath, Var]
  ) -> None:
    """
    minimize the total length * width of all selected paths
    """
    # concatenate to get all paths
    all_paths: List[RoutingPath] = sum(bridge_to_paths.values(), [])
    m.objective = minimize(
      xsum(path_to_var[path] * path.getCost() for path in all_paths)
    )

  def _analyzeILPResults(
    self,
    bridge_to_paths,
    bridge_to_selected_path,
    routing_edge_to_selected_paths
  ) -> None:
    # log the quality of the selected path
    for bridge, paths in bridge_to_paths.items():
      if len(paths) > 1:
        all_costs = [p.getCost() for p in paths]
        all_costs.sort()
        selected_path = bridge_to_selected_path[bridge]
        rank = bisect(all_costs, selected_path.getCost())

        rank_info = f'{bridge.name} from {selected_path.getSrcSlotName()} to {selected_path.getDstSlotName()} is routed with the rank {rank} / {len(all_costs)} path. '
        overall_info = f'Path cost: {selected_path.getCost()}. All costs: {all_costs}'
        logging.info(rank_info + overall_info)
          
    # log the utilization ratio of each boundary
    for routing_edge, paths in routing_edge_to_selected_paths.items():
      total_data_width = sum([path.data_width for path in paths])
      logging.debug(f'boundary {routing_edge._name} is passed by {total_data_width} / {routing_edge.capacity} = {total_data_width / routing_edge.capacity} ')
      for path in paths:
        logging.debug(f'  {path.bridge_name}')

  def _getILPResults(
    self,
    bridge_to_paths,
    path_to_var,
    routing_edge_to_paths
  ) -> Dict[str, List[Slot]]:

    # get the selected paths
    bridge_to_selected_path = {}
    for bridge, paths in bridge_to_paths.items():
      for path in paths:
        val = path_to_var[path].x
        assert abs(val - round(val)) < 0.0001
        if round(val) == 1:
          bridge_to_selected_path[bridge] = path
          logging.debug(f'bridge {bridge.name} is routed to: ')
          path.printPath()
          if path.getLength() > path.getTheoreticalShortestLength():
            logging.warning(f'{bridge.name} is not routed with the shortest paths')

          break
      assert bridge in bridge_to_selected_path

    # get which paths will pass through a boundary
    routing_edge_to_selected_paths = defaultdict(list)
    for routing_edge, paths in routing_edge_to_paths.items():
      logging.debug(f'boundary {routing_edge._name} is passed by:')
      for path in paths:
        val = path_to_var[path].x
        if round(val) == 1:
          routing_edge_to_selected_paths[routing_edge].append(path)
          logging.debug(f'  {path.bridge_name}')

    return bridge_to_selected_path, routing_edge_to_selected_paths

  def _getENameToPathsExcludeSrcAndDst(self, bridge_to_selected_path):
    e_name_to_paths = {}
    # exclude the source and destination to feed back to the outside world   
    for bridge, selected_path in bridge_to_selected_path.items():
      e_name_to_paths[bridge.name] = selected_path.getSlotsOfPath()[1:-1]

    return e_name_to_paths

  def ILPRouting(
      self,
      routing_usage_limit: float = 0.7,
      detour_path_limit: int = 4
  ) -> Dict[str, List[Slot]]:

    while 1:
      logging.info(f'Global routing attempt with routing usage limit {routing_usage_limit}')

      m = Model()

      bridge_to_paths = self._getBridgeToCandidatePaths(routing_usage_limit, detour_path_limit)
      path_to_var = self._getPathToVar(m, bridge_to_paths)
      routing_edge_to_paths = self._getRoutingEdgeToPassingPaths(bridge_to_paths)

      logging.info(f'there are {len(bridge_to_paths)} dataflow edges')
      logging.info(f'there are {len(path_to_var)} potential paths to select from')

      self._constrOnePathForOneBridge(m, bridge_to_paths, path_to_var)

      self._constrRoutingEdgeCapacity(m, path_to_var, routing_edge_to_paths)

      self._minimizeTotalPathArea(m, bridge_to_paths, path_to_var)

      status = m.optimize()

      if status == OptimizationStatus.OPTIMAL:
        logging.warning(f'Succeeded: global routing attempt with routing usage limit {routing_usage_limit}')
        break
      else:
        logging.warning(f'Failed: global routing attempt with routing usage limit {routing_usage_limit}')
        routing_usage_limit += 0.03

    # extract results
    bridge_to_selected_path, routing_edge_to_selected_paths = \
      self._getILPResults(bridge_to_paths, path_to_var, routing_edge_to_paths)

    # logging and analysis
    self._analyzeILPResults(bridge_to_paths, bridge_to_selected_path, routing_edge_to_selected_paths)

    # convert the data format of the path
    e_name_to_paths_without_src_and_dst =  self._getENameToPathsExcludeSrcAndDst(bridge_to_selected_path)

    return e_name_to_paths_without_src_and_dst


if __name__ == '__main__':  
  routing_graph = RoutingGraph()

  # paths = routing_graph.findAllPaths('CR_X4Y0_To_CR_X5Y1', 'CR_X4Y8_To_CR_X5Y9', 10, 'test_name')
  # print(len(paths))

  paths = routing_graph.findAllPaths('CR_X4Y2_To_CR_X5Y3', 'CR_X4Y8_To_CR_X5Y9', 10, 'test_name')
  print(len(paths))

  for path in paths:
    path.printPath()