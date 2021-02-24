import logging
from mip import *

class LatencyBalancing:
  def __init__(self, graph, floorplan, global_router):
    logging.info('running latency balancing...')
    self.name2edge = graph.getNameToEdgeMap()
    self.name2vertex = graph.getNameToVertexMap()
    self.floorplan = floorplan
    self.global_router = global_router
    self.e_name2lat = {}

    self.__rebalance()

  def __rebalance(self):
    m = Model()

    # map Vertex -> "arrival time"
    v2var = {}
    for name, v in self.name2vertex.items():
      v2var[v] = m.add_var(var_type=INTEGER, name=name)

    # differential constraint for each edge
    for e_name, e in self.name2edge.items():
      m += v2var[e.src] >= v2var[e.dst] + self.global_router.getPipelineLevelOfEdge(e)

    m.objective = minimize(xsum( 
      e.width * (v2var[e.src] - v2var[e.dst]) for e in self.name2edge.values() 
    ))

    status = m.optimize(max_seconds=120)
    assert status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE, 'Failed to balance reconvergent paths at loop level. Dependency loop detected.'

    # get result
    for e_name, e in self.name2edge.items():
      self.e_name2lat[e_name] = int(v2var[e.src].x - v2var[e.dst].x)
      logging.info(f'Latency of edge {e_name}: {self.e_name2lat[e_name]} ')

  def getLatencyofEdgeName(self, e_name : str):
    return self.e_name2lat[e_name]