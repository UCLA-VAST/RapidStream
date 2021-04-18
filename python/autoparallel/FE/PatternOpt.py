#! /usr/bin/python3.6
import logging
from autobridge.Opt.DataflowGraph import DataflowGraph
import os
import subprocess
import re
from collections import defaultdict
from mip import Model, BINARY, xsum, maximize, OptimizationStatus

# collect graph data and invoke Peregrine
# Note that Vitis libraries will conflict with Peregrine
def patternMining(graph : DataflowGraph, peregrine_home : str):
  # prepare for Peregrine inputs
  int_e_list, int_v_labels = graph.getIntegerGraph()

  fsm_dir = f'{os.getcwd()}/pattern_mining'
  os.mkdir(fsm_dir)
  os.mkdir(f'{fsm_dir}/graph_src')
  os.mkdir(f'{fsm_dir}/graph_pg')
  open(f'{fsm_dir}/graph_src/edges.txt', 'w').write('\n'.join(' '.join(map(str,row)) for row in int_e_list))
  open(f'{fsm_dir}/graph_src/labels.txt', 'w').write('\n'.join(' '.join(map(str,row)) for row in int_v_labels))  

  # create Peregrine input format
  subprocess.run([f'{peregrine_home}/bin/convert_data', \
                  f'{fsm_dir}/graph_src/edges.txt', \
                  f'{fsm_dir}/graph_src/labels.txt', \
                  f'{fsm_dir}/graph_pg'])

  # run frequent pattern mining
  fsm_size = '4'
  fsm_threshold = '50'
  induce_type = 'v'

  try:
    pg_output_raw = subprocess.check_output([f'{peregrine_home}/bin/fsm', 
                                      f'{fsm_dir}/graph_pg', 
                                      fsm_size, 
                                      fsm_threshold, 
                                      induce_type],
                                      stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))  

  pg_output = pg_output_raw.decode('utf-8').split('\n') # format conversion

  return pg_output

# parse Peregrine results, collect all patterns and instances
def parsePeregrine(pg_output : list, int_2_v_name : dict, int_2_v_type : dict):
  patterns = []
  curr = {}

  for line in pg_output:
    if '[Pattern]' in line:
      # store the previous pattern
      if curr:
        patterns.append(curr)

      # new pattern
      curr = {}

      # extract the connection between vertices in the pattern
      # [vertex 1,label1-vertex 2,label 2]
      pattern_edges = re.findall('\[(\d+),(\d+)-(\d+),(\d+)\]', line)
      curr['PatternEdges'] = [(int(e[0]), int(e[2])) for e in pattern_edges]
      curr['PatternType'] = [(int_2_v_type[int(e[1])], int_2_v_type[int(e[3])]) for e in pattern_edges]
      curr['Instances'] = []

    elif '[Instance]' in line:
      # [Instance] v1 v2 v3 v4
      vertices_of_inst = [int_2_v_name[int(id)] for id in line.split()[1:]]
      curr['Instances'].append(tuple(vertices_of_inst))

  return patterns

# compute a weight for each pattern
def annotatePatternWeights(patterns : list, graph):
  for pat in patterns:
    # TODO: run multiple pattern instances to verify Peregrine results
    inst = pat['Instances'][0] # list of vertex names in the pattern instance
    inter_edges = set()
    
    # get the Vertex objects from names
    v_list = [graph.getVertex(v_name) for v_name in inst]

    # get intra edges and inter edges
    for v in v_list:
      for e in v.getOutEdges():
        if e.dst.name not in inst:
          inter_edges.add(e)
      for e in v.getInEdges():
        if e.src.name not in inst:
          inter_edges.add(e)
    
    # total interface width of the pattern
    interface_width = sum(e.width for e in inter_edges) 
    
    # get the total interface width of each vertex in the pattern
    e_list_of_each_v = [v.getEdges() for v in v_list] # list of list
    width_of_each_v = [sum(e.width for e in e_list) for e_list in e_list_of_each_v]
    vertex_total_width = sum(width_of_each_v)

    # define weight as the reduction rate of width
    pat['Weight'] = vertex_total_width / interface_width

    logging.info(f'Assign weight {pat["Weight"]} to pattern {pat["PatternType"]}')

# pattern selection
# TODO: transit to CONTINUOUS
def patternSelection(patterns : list):
  m = Model()

  # each pattern instance has a decision variable
  inst2var = {}
  for pattern in patterns:
    for inst in pattern['Instances']:
      assert inst not in inst2var, 'detect repetitive pattern instances!'
      inst2var[inst] = m.add_var(var_type=BINARY)

  # each vertex can only be used by one pattern
  vname2insts_with_v = defaultdict(list)
  for pattern in patterns:
    for inst in pattern['Instances']:
      for vname in inst:
        vname2insts_with_v[vname].append(inst)

  for vname, insts_with_v in vname2insts_with_v.items():
    m += xsum(inst2var[inst] for inst in insts_with_v) == 1

  # maximize total pattern weight. Insts of the same pattern have the same weight
  m.objective = maximize(xsum(pat['Weight'] * inst2var[inst] for pat in patterns for inst in pat['Instances'] ) )

  status = m.optimize(max_seconds=60)
  if status == OptimizationStatus.OPTIMAL:
    logging.info('pattern selection succeed')
  elif status == OptimizationStatus.FEASIBLE:
    logging.warning('pattern selection too slow!')
  else:
    logging.critical('pattern selection failed!')

  # extract pattern selection results
  selected_pattern_insts = [inst for pattern in patterns for inst in pattern['Instances'] \
                            if inst2var[inst].x]
  for inst in selected_pattern_insts:
    logging.info(f'{inst}')

  return selected_pattern_insts

# dump grouping constraints
def getPatternBasedGrouping(graph : DataflowGraph, peregrine_home):
  pg_output = patternMining(graph, peregrine_home)
  patterns = parsePeregrine(pg_output, graph.getIntIdToVName(), graph.getIntIdToVType())
  annotatePatternWeights(patterns, graph)
  selected_pattern_insts = patternSelection(patterns)
  return selected_pattern_insts