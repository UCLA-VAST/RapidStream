#! /usr/bin/python3.6
import logging
import re
import copy
import os
import shutil
from autobridge.Codegen.FIFOTemplate import fifo_template

class CreateSlotWrapper:
  def __init__(self, graph, top_rtl_parser, floorplan, global_router, rebalance, target='hw'):
    self.graph = graph
    self.top_rtl_parser = top_rtl_parser
    self.floorplan = floorplan
    self.global_router = global_router
    self.rebalance = rebalance
    self.target = target

    # only contains the ap_done signals that are part of the final ap_done
    self.ap_done_v_name_to_wire = top_rtl_parser.getApDoneVNameToWire()

    # only contains the ap_done signals that are part of the final ap_done
    self.ap_ready_v_name_to_wire = top_rtl_parser.getApReadyVNameToWire()

    self.s2v = floorplan.getSlotToVertices()
    self.s2e = floorplan.getSlotToEdges()

    self.slot2wrapper = {}
    self.__initSlotWrapper()
    
  def __getWireDeclCopy(self, slot) -> str:
    """
    Different wrappers will filter out different wires
    To avoid interference, we make a deep copy of the entire wire list from the original top RTL
    """
    return copy.deepcopy(self.top_rtl_parser.getAllDeclExceptIO())

  def __getVertexInstances(self, slot):
    v_list = self.s2v[slot]
    logging.debug(f'slot {slot.getRTLModuleName()} has {len(v_list)} v insts')
    return [self.top_rtl_parser.getRTLOfInst(v.name) for v in v_list]

  def __getEdgeInstances(self, slot):
    """
    get the RTL snippet of each FIFO instantiation
    replace the original HLS fifo by our almost-full template
    """
    e_list = self.s2e[slot]
    logging.debug(f'slot {slot.getRTLModuleName()} has {len(e_list)} e insts')

    edge_insts = []
    for e in e_list:
      balance = self.rebalance.getLatencyofEdgeName(e.name)
      pipeline_level = self.global_router.getPipelineLevelOfEdge(e)

      # note the difference between grace_period and edge latency
      # since we pipeline both the outbound signal and the inbound signal
      # for each unit of pipeline latency on the edge
      # we need twice the grace period
      grace_period = pipeline_level * 2 # round trip latency
      grace_period += 1 # additional pipelining of the full_n
      
      inst = self.top_rtl_parser.getFIFOInstOfNewTemplate(e.name, e.width, e.depth + balance, grace_period)
      edge_insts.append(inst)
    
    return edge_insts

  def __getHeader(self, slot):
    """
    note the difference between getHeader and getIOSec:
    getHeader -> module xxx (a, b, c, ...)
    getIOSec  -> input a; output [1:0] b, ...
    """
    io_decl = self.__getIODecl(slot)
    io_decl_with_comma = [io.replace(';', ',') for io in io_decl]

    # need to consider if the IO name contains "input" or "output"
    io_header = [re.sub(r'^[ ]*input[ ]*|^[ ]*output[ ]*', '', io) for io in io_decl_with_comma]
    
    io_header = [re.sub(r'[ ]*\[.*\][ ]*', '', io) for io in io_header]
    io_header[-1] = io_header[-1].replace(',', '') # the last io does not have comma

    # add indentation
    io_header = ['  '+io for io in io_header]

    beg = ['\n\n`timescale 1 ns / 1 ps', f'module {slot.getRTLModuleName()} (']
    io_header = beg + io_header
    io_header.append(');')

    return io_header

  def __getEnding(self):
    return ['endmodule']

  def __getIODecl(self, slot):
    """
    get the IO of each wrapper
    1. inter-slot edges
    2. top-level IOs
    """
    IO_section = []
    v_set = set(self.s2v[slot])

    # wires of inter-slot edges become IOs. Differentiate in-bound and out-bound edges
    # note that for both sides the interface is the out-bound side of the FIFO
    intra_edges, inter_edges = self.floorplan.getIntraAndInterEdges(self.s2v[slot])
    inbound_dir = {'_din' : 'input', '_write' : 'input', '_full_n' : 'output'}
    outbound_dir = {'_din' : 'output', '_write' : 'output', '_full_n' : 'input'}

    for e in inter_edges:
      is_inbound = e.dst in v_set
      wire_dir = inbound_dir if is_inbound else outbound_dir
      for port_name, wire_name in self.top_rtl_parser.getWiresOfFIFOName(e.name):
        suffix = [key for key in ['_din', '_full_n', '_write'] if port_name.endswith(key)]
        if suffix:
          dir = wire_dir[suffix[0]]
          wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
          IO_section.append(f'{dir} {wire_width} {wire_name};')

    # if any vertex is an AXI module, it will contain top-level IO
    for v in self.s2v[slot]:
      if '_axi' in v.name:
        for wire in self.top_rtl_parser.getWiresOfVertexName(v.name):
          if self.top_rtl_parser.isIO(wire) and 'ap_' not in wire: # to avoid redundant ap ports
            IO_section.append(f'{self.top_rtl_parser.getDirOfIO(wire)} {self.top_rtl_parser.getWidthOfIO(wire)} {wire};')

    # control signals
    IO_section.append('input  ap_start;')
    IO_section.append('output ap_done;')
    IO_section.append('output ap_idle;')
    IO_section.append('output ap_ready;')
    IO_section.append('input  ap_continue;')
    IO_section.append('input ap_clk;')
    IO_section.append('input ap_rst_n;')

    if any('s_axi' in v.name for v in self.s2v[slot]):
      IO_section.append('output ap_start_orig;')
      IO_section.append('input  ap_done_final;')
      IO_section.append('input  ap_idle_final;')
      IO_section.append('input  ap_ready_final;')

    return IO_section

  def __setApStart(self, decl, v_insts, stmt):
    """
    pipeline the ap_start signal
    update the ap_start used in each module instance
    """
    v_insts[:] = [re.sub(r'\.ap_start[ ]*\(.*\)', '.ap_start(ap_start_pipe)', inst) for inst in v_insts]

    decl.append('// pipeline ap_start')
    decl.append('(* shreg_extract = "no" *) reg ap_start_p1;')
    decl.append('(* shreg_extract = "no" *) reg ap_start_p2;')
    decl.append('(* shreg_extract = "no" *) reg ap_start_pipe;')

    stmt.append('// pipeline ap_start')
    stmt.append('initial begin')
    stmt.append('  ap_start_p1 = 1\'b0;')
    stmt.append('  ap_start_p2 = 1\'b0;')
    stmt.append('  ap_start_pipe = 1\'b0;')
    stmt.append('end')
    stmt.append('always @ (posedge ap_clk) begin')
    stmt.append('  ap_start_p1 <= ap_start;')
    stmt.append('  ap_start_p2 <= ap_start_p1;')
    stmt.append('  ap_start_pipe <= ap_start_p2;')
    stmt.append('end')

  def __setApContinue(self, v_insts):
    """
    set ap_continue = 1
    """
    v_insts[:] = [re.sub(r'\.ap_continue[ ]*\(.*\)', '.ap_continue(1\'b1)', inst) for inst in v_insts]

  def __setApDone(self, decl, slot, stmt):
    """
    implement the ap_done logic for each wrapper
    We first extract from the original top RTL which ap_done signals are used for the final ap_done
    if a wrapper contains one or more of them, use them to comprise the ap_done of the wrapper
    otherwise set the ap_done of the wrapper to be 1
    """
    ap_done_wires = []
    for v in self.s2v[slot]:
      try: ap_done_wires.append(self.ap_done_v_name_to_wire[v.name])
      except: pass

    # if the slot does not contain valid ap_ready modules:
    if not ap_done_wires:
      stmt.append('assign ap_done = 1\'b1;') # if the slot only contains controller, ap_done should be 1
      return

    decl.append('// pipeline ap_done')
    for ap_done in ap_done_wires:
      decl.append(f'(* shreg_extract = "no" *) reg {ap_done}_p1;')
      decl.append(f'(* shreg_extract = "no" *) reg {ap_done}_p2;')
      decl.append(f'(* shreg_extract = "no" *) reg {ap_done}_pipe;')
      decl.append(f'(* shreg_extract = "no" *) reg {ap_done}_backup;') 

    stmt.append('// pipeline ap_done')
    for ap_done in ap_done_wires:
      stmt.append(f'always @ (posedge ap_clk) begin')
      stmt.append(f'  {ap_done}_p1 <= {ap_done};')
      stmt.append(f'  {ap_done}_p2 <= {ap_done}_p1;')
      stmt.append(f'  {ap_done}_pipe <= {ap_done}_p2;')
      stmt.append(f'end')

    # in case different modules stagger their ap_done signal
    # hold the ap_done until the final ap_done is asserted
    stmt.append('(* dont_touch = "yes" *) reg ap_done_reg_;')
    stmt.append(f'always @ (posedge ap_clk) begin')
    stmt.append('  ap_done_reg_ <= ' + '&'.join(f'{ap_done}_backup' for ap_done in ap_done_wires) + ';')
    stmt.append(f'end')    
    stmt.append('assign ap_done = ap_done_reg_;')

    stmt.append('// backup ap_done')
    for ap_done in ap_done_wires:
      stmt.append(f'always @ (posedge ap_clk) begin')
      stmt.append(f'  if (ap_done_reg_) begin')
      stmt.append(f'    {ap_done}_backup <= {ap_done}_pipe;')
      stmt.append(f'  end')
      stmt.append(f'  else begin')
      stmt.append(f'    {ap_done}_backup <= {ap_done}_backup | {ap_done}_pipe;')
      stmt.append(f'  end')
      stmt.append(f'end')
 
  def __setApReady(self, decl, slot, stmt):
    """
    similar to __setApDone. Currently not used. May not be able to extract all needed ap_ready signals because of coding style
    For simplicity we set the final ap_ready = ap_done
    """
    ap_ready_wires = []
    for v in self.s2v[slot]:
      try: ap_ready_wires.append(self.ap_ready_v_name_to_wire[v.name])
      except: pass

    # if the slot does not contain valid ap_ready modules:
    if not ap_ready_wires:
      stmt.append('assign ap_ready = 1\'bx;')
      return

    decl.append('// pipeline ap_ready')
    for ap_ready in ap_ready_wires:
      decl.append(f'(* shreg_extract = "no" *) reg {ap_ready}_p1;')
      decl.append(f'(* shreg_extract = "no" *) reg {ap_ready}_p2;')
      decl.append(f'(* shreg_extract = "no" *) reg {ap_ready}_pipe;')

    stmt.append('// pipeline ap_ready')
    for ap_ready in ap_ready_wires:
      stmt.append(f'always @ (posedge ap_clk) begin')
      stmt.append(f'  {ap_ready}_p1 <= {ap_ready};')
      stmt.append(f'  {ap_ready}_p2 <= {ap_ready}_p1;')
      stmt.append(f'  {ap_ready}_pipe <= {ap_ready}_p2;')
      stmt.append(f'end')
    assignment = 'assign ap_ready = ' + '&'.join(f'{ap_ready}_pipe' for ap_ready in ap_ready_wires) + ';'
    stmt.append(assignment)

  # lazy approach, so far works fine
  def __setApReadyAsApDone(self, stmt):
    stmt.append('assign ap_ready = ap_done;')

  # no modification to the ap_idle signals
  def __setApIdle(self, stmt):
    stmt.append('assign ap_idle = ap_done;')

  # TODO: this one is too slow
  def __filterUnusedDecl(self, decl, v_insts, e_insts, io_decl):
    """
    we start with the complete wire/reg declaration from the original top file
    for each wrapper, we only keep the ones that are used in this wrapper
    """
    insts = v_insts + e_insts
    decl_filter = []
    ap_signals = ['ap_start', 'ap_done', 'ap_ready', 'ap_idle']

    # find out the io names
    io_names = set([re.search(' ([^ ]+)[ ]*;', line).group(1) for line in io_decl])

    # find out which wires are used by the instances
    used_wires_in_insts = set()
    for inst in insts:
      inst_list = inst.split('\n')
      for line in inst_list:
        match = re.search('\.[^\(]+\([ ]*([^ ]+)[ ]*\)', line)
        if match:
          used_wires_in_insts.add(match.group(1))

    for d in decl:
      # remove the original ap signals
      if any(re.search(f' {signal}', d) for signal in ap_signals):
        continue
      # do not filter comments
      elif re.search(r'^[ ]*//', d):
        decl_filter.append(d)
        continue
      # do not filter parameters because parameters may be used to calculate other param, making things complicated
      elif 'parameter' in d:
        decl_filter.append(d)
        continue

      else:
        # get the wire name
        # case 1: wire x;
        # case 2: wire [1:0] x;
        # case 3: wire [1:0]x;
        match = re.search(r' ([^ \]]*);', d); assert match
        name = match.group(1)

        # we do not want redundant wire and IO declaration
        # add a space before name for exact match
        # avoid filtering out a wire unexpectedly
        if name in io_names:
          logging.debug(f'filter out {name} due to io redundancy')
          continue
        # if a wire is used & it is not an IO
        # no exact match here as it is OK to add more wires
        elif name in used_wires_in_insts:
          decl_filter.append(d)
        else:
          logging.debug(f'filter out {name} due to no match')

    decl[:] = decl_filter

  def __addIndent(self, *sections):
    for sec in sections:
      sec = ['  ' + line for line in sec]

  def __setSAxiCtrl(self, v_insts):
    """
    the s_axi_control sends out the initial ap_start signal and takes in
    the final ap_done signal 
    """
    for i, v_inst in enumerate(v_insts):
      if 's_axi_control' in v_inst:
        v_inst = re.sub(r'\.ap_start[ ]*\(.*\)', '.ap_start(ap_start_orig)', v_inst)
        v_inst = re.sub(r'\.ap_ready[ ]*\(.*\)', '.ap_ready(ap_ready_final)', v_inst)
        v_inst = re.sub(r'\.ap_done[ ]*\(.*\)', '.ap_done(ap_done_final)', v_inst)
        v_inst = re.sub(r'\.ap_idle[ ]*\(.*\)', '.ap_idle(ap_idle_final)', v_inst)
        v_insts[i] = v_inst
        return

  def __setApRst(self, decl, v_insts, e_insts, stmt):
    """
    replace the original reset signals to the pipelined once
    Need to first correctly identify the reset signals
    ap_rst, ap_rst_n, ap_rst_n_inv, reset, ARESET,
    """
    v_insts[:] = [re.sub(r'\.ap_rst[ ]*\(.*\)', '.ap_rst(ap_rst_pipe)', inst) for inst in v_insts]
    v_insts[:] = [re.sub(r'\.ap_rst_n[ ]*\(.*\)', '.ap_rst_n(ap_rst_n_pipe)', inst) for inst in v_insts]
    v_insts[:] = [re.sub(r'\.reset[ ]*\(.*\)', '.reset(ap_rst_pipe)', inst) for inst in v_insts]
    v_insts[:] = [re.sub(r'\.ARESET[ ]*\(.*\)', '.ARESET(ap_rst_pipe)', inst) for inst in v_insts]

    decl.append('// pipeline ap_rst_n')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_p1;')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_p2;')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_pipe;')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_n_p1;')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_n_p2;')
    decl.append('(* shreg_extract = "no" *) reg ap_rst_n_pipe;')

    stmt.append('// pipeline ap_start')
    stmt.append('initial begin')
    stmt.append('  ap_rst_p1 = 1\'b0;')
    stmt.append('  ap_rst_p2 = 1\'b0;')
    stmt.append('  ap_rst_pipe = 1\'b0;')
    stmt.append('  ap_rst_n_p1 = 1\'b0;')
    stmt.append('  ap_rst_n_p2 = 1\'b0;')
    stmt.append('  ap_rst_n_pipe = 1\'b0;')
    stmt.append('end')
    stmt.append('always @ (posedge ap_clk) begin')
    stmt.append('  ap_rst_p1 <= ~ap_rst_n;') # note the inversion here
    stmt.append('  ap_rst_p2 <= ap_rst_p1;')
    stmt.append('  ap_rst_pipe <= ap_rst_p2;')
    stmt.append('  ap_rst_n_p1 <= ap_rst_n;')
    stmt.append('  ap_rst_n_p2 <= ap_rst_n_p1;')
    stmt.append('  ap_rst_n_pipe <= ap_rst_n_p2;')
    stmt.append('end')

  def __initSlotWrapper(self):
    for s in self.s2v.keys():
      wrapper = self.createSlotWrapper(s)
      self.slot2wrapper[s] = wrapper

  def createSlotWrapper(self, slot):
    header = self.__getHeader(slot)
    decl = self.__getWireDeclCopy(slot)
    io_decl = self.__getIODecl(slot)
    v_insts = self.__getVertexInstances(slot)
    e_insts = self.__getEdgeInstances(slot)
    stmt = []
    ending = self.__getEnding()

    logging.debug(f'create wrapper for {slot.getRTLModuleName()}')
    logging.debug(f'{slot.getRTLModuleName()}: v_insts contains:' + '\n'.join(v_insts))
    logging.debug(f'{slot.getRTLModuleName()}: e_insts contains:' + '\n'.join(e_insts))
    
    # must do the filtering at the beginning, otherwise it may mess up our added signals
    self.__filterUnusedDecl(decl, v_insts, e_insts, io_decl)

    self.__setApStart(decl, v_insts, stmt)
    self.__setApContinue(v_insts)
    self.__setApDone(decl, slot, stmt)
    self.__setApReadyAsApDone(stmt)
    self.__setApIdle(stmt)
    self.__setSAxiCtrl(v_insts)
    self.__setApRst(decl, v_insts, e_insts, stmt)

    self.__addIndent(decl, io_decl, v_insts, e_insts, stmt)

    wrapper = header + decl + io_decl + v_insts + e_insts + stmt + ending
    if self.target == 'hw':
      wrapper += [fifo_template]
    return wrapper

  def getSlotWrapperForAll(self, dir='wrapper_rtl'):
    if os.path.isdir(dir):
      shutil.rmtree(dir)
    os.mkdir(dir)
    for s in self.s2v.keys():
      wrapper = self.slot2wrapper[s]
      f = open(dir + '/' + s.getRTLModuleName()+'.v', 'w')
      f.write('\n'.join(wrapper))

  def getSlotWrapper(self, slot):
    return self.slot2wrapper[slot]

  def getSlotNameToIOList(self):
    slot_2_io = self.getSlotToIOList()
    return {slot.getRTLModuleName() : io_list for slot, io_list in slot_2_io.items()}

  def getSlotToIOList(self):
    slot_2_io = {}
    for slot in self.s2v.keys():
      io_decl = self.__getIODecl(slot)
      io_decl = [io.replace(';', '') for io in io_decl]
      io_decl = [io.split() for io in io_decl] # ensure that no space in width, e.g., [1+2:0]
      
      slot_2_io[slot] = io_decl
    return slot_2_io

  # to be used as black box
  def getEmptyWrappers(self):
    """
    in vivado flow, to declare a module instance as black box, we must have an empty initilization
    """
    empty_wrappers = []
    for s in self.s2v.keys():
      empty_wrappers += self.__getHeader(s)
      empty_wrappers += self.__getIODecl(s)
      empty_wrappers += self.__getEnding()
    return empty_wrappers