#! /usr/bin/python3.6
import logging
from typing import List

class CreateRoutingSlotWrapper:

  def __init__(self, compute_wrapper_creater, floorplan, global_router, top_rtl_parser):
    self.compute_slot_to_io = compute_wrapper_creater.getSlotToIOList()
    self.floorplan = floorplan
    self.global_router = global_router
    self.top_rtl_parser = top_rtl_parser

    self.inbound_dir = {'_din' : 'input', '_write' : 'input', '_full_n' : 'output'}
    self.outbound_dir = {'_din' : 'output', '_write' : 'output', '_full_n' : 'input'}

  def getPassingEdgeIO(self, slot):
    """
    add the edges that pass by this slot
    each passing edge corresponds to
    input _din, input _write, output _dout (inbound side, connect to src)
    output _din, output _write, input _dout (outbound side, connect to dst)
    """

    passing_e_io = []
    passing_e_names = self.global_router.getPassingEdgeNamesOfSlot(slot)
    for e_name in passing_e_names:
      index = self.global_router.getIndexOfSlotInPath(e_name, slot)

      # originally one wire connect the two slots
      # now this wire goes through multiple intermediate slots
      # add tags to differentiate them
      # note that we want the two ports connected by a wire to have the same name
      # this makes it easier to generate the top RTL
      # since we change the IO name here, we need to connect the IO to the internal
      in_tag = f'_pass_{index}'# connect to preivous wire segment
      out_tag = f'_pass_{index+1}' # connect to next segment
      
      for port_name, wire_name in self.top_rtl_parser.getWiresOfFIFOName(e_name):
        suffix = [key for key in ['_din', '_full_n', '_write'] if port_name.endswith(key)]
        if suffix:
          wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
          passing_e_io.append(f'{self.inbound_dir[suffix[0]]} {wire_width} {wire_name}{in_tag};')
          passing_e_io.append(f'{self.outbound_dir[suffix[0]]} {wire_width} {wire_name}{out_tag};')

    return passing_e_io

  def getInterSlotEdgeIO(self, slot):
    """
    wires of inter-slot edges become IOs. Differentiate in-bound and out-bound edges
    note that for both sides the interface is the out-bound side of the FIFO
    """
    inter_slot_e_io = []
    s2v = self.floorplan.getSlotToVertices()
    v_set = set(s2v[slot])
    intra_edges, inter_edges = self.floorplan.getIntraAndInterEdges(s2v[slot])

    for e in inter_edges:
      is_inbound = e.dst in v_set
      wire_dir = self.inbound_dir if is_inbound else self.outbound_dir
      for port_name, wire_name in self.top_rtl_parser.getWiresOfFIFOName(e.name):
        suffix = [key for key in ['_din', '_full_n', '_write'] if port_name.endswith(key)]
        if suffix:
          dir = wire_dir[suffix[0]]
          wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)

          # change the IO name for the dst of an edge 
          # in order to make it easier to create the top, two ports connected by a wire have the same name
          # thus for each inter-slot edge, the port names on the inbound side are changed 
          # a side effect is that the IO will be mismatching the ports of the internal FIFOs
          # this issue is fixed in __connectPassingWires
          if is_inbound:
            # the current slot is the dst of the edge
            path_len = self.global_router.getPathLength(e.name)
            inter_slot_e_io.append(f'{dir} {wire_width} {wire_name}_pass_{path_len};')
          else: # outbound
            inter_slot_e_io.append(f'{dir} {wire_width} {wire_name}_pass_0;')

    return inter_slot_e_io

  def getWrapperCtrlIO(self, slot, inter_slot_e_io : List[str]):
    """ get the remaining IO besides the inter slot edge IO """
    ctrl_io = []
    compute_slot_io_list = self.compute_slot_to_io[slot]
    for io in compute_slot_io_list:
      if any(f'{io[-1]}_pass_' in e_io for e_io in inter_slot_e_io):
        continue
      else:
        ctrl_io.append(' '.join(io) + ';')

    return ctrl_io

  def getIOSection(self, slot):
    passing_e_io = self.getPassingEdgeIO(slot)
    inter_slot_e_io = self.getInterSlotEdgeIO(slot)
    ctrl_io = self.getWrapperCtrlIO(slot, inter_slot_e_io)
    io_section = passing_e_io + inter_slot_e_io + ctrl_io

    io_section = [io.replace(';', ',') for io in io_section]
    io_section[-1] = io_section[-1].replace(',', '')

    return io_section

  def connectPassingWires(self, slot):
    """ 
    use wire to connect the input and output port of passing wires
    The actual pipeline registers appear as anchor registers
    """
    stmt = []
    passing_e_names = self.global_router.getPassingEdgeNamesOfSlot(slot)
    for e_name in passing_e_names:
      index = self.global_router.getIndexOfSlotInPath(e_name, slot)
      for port_name, wire_name in self.top_rtl_parser.getWiresOfFIFOName(e_name):
        if port_name.endswith('_din') or port_name.endswith('_write'):
          stmt.append(f'assign {wire_name}_pass_{index+1} = {wire_name}_pass_{index};')
        elif port_name.endswith('_full_n'):
          stmt.append(f'assign {wire_name}_pass_{index} = {wire_name}_pass_{index+1};')

    return stmt

  def connectInterSlotEdgeWiresToIO(self, slot):
    """
    if we include the passing edges, the IOs of inbound inter-slot FIFOs are modified with a suffix
    here we need to connect the IO ports with the actual FIFO instances internal to the slot
    """
    connection_stmt = []
    s2v = self.floorplan.getSlotToVertices()
    v_set = set(s2v[slot])
    intra_edges, inter_edges = self.floorplan.getIntraAndInterEdges(s2v[slot])

    print(slot.getRTLModuleName())

    for e in inter_edges:
      path_len = self.global_router.getPathLength(e.name)

      for port_name, wire_name in self.top_rtl_parser.getWiresOfFIFOName(e.name):
        # the wire without suffix will connect to the module instances
        if any(port_name.endswith(tag) for tag in ['_din', '_write', '_full_n']):
          wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
          connection_stmt.append(f'wire {wire_width} {wire_name};')

        if e.dst in s2v[slot]: # process in-bound edges
          # _din and _write are input
          if port_name.endswith('_din') or port_name.endswith('_write'):
            wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
            connection_stmt.append(f'assign {wire_name} = {wire_name}_pass_{path_len};')
          # _full_n is output
          elif port_name.endswith('_full_n'):
            wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
            connection_stmt.append(f'assign {wire_name}_pass_{path_len} = {wire_name};')

        else: # out-bound edges
          # _din and _write are output
          if port_name.endswith('_din') or port_name.endswith('_write'):
            wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
            connection_stmt.append(f'assign {wire_name}_pass_0 = {wire_name};')
          # _full_n is input
          elif port_name.endswith('_full_n'):
            wire_width = self.top_rtl_parser.getWidthOfRegOrWire(wire_name)
            connection_stmt.append(f'assign {wire_name} = {wire_name}_pass_0;')

    return connection_stmt

  def getInnerWrapperInst(self, slot):
    # instantiate each slot
    slot_inst = []
    
    # if targeting implementation, we mark the modules as black box
    # so that they can be replaced later by separately implemented DCPs
    slot_inst.append(f'\n\n  {slot.getRTLModuleName()} {slot.getRTLModuleName()}_U0 (')

    compute_slot_io_list = self.compute_slot_to_io[slot]
    for io in compute_slot_io_list:
      slot_inst.append(f'    .{io[-1]}({io[-1]}),') 
      
    # handle the last io
    slot_inst[-1] = slot_inst[-1].replace(',', '\n  );') 
    
    return slot_inst

  def getRoutingInclusiveWrapper(self, slot):
    wrapper = []

    wrapper.append(f'module {slot.getRTLModuleName()}_routing (')
    wrapper += self.getIOSection(slot)
    wrapper.append(f');')

    wrapper += self.connectPassingWires(slot)
    wrapper += self.connectInterSlotEdgeWiresToIO(slot)
    wrapper += self.getInnerWrapperInst(slot)

    wrapper.append(f'endmodule')

    return wrapper

  def createRoutingInclusiveWrapperForAll(self, dir='wrapper_rtl'):
    for slot, wrapper_io_list in self.compute_slot_to_io.items():
      routing_wrapper = self.getRoutingInclusiveWrapper(slot)
      f = open(dir + '/' + slot.getRTLModuleName()+'_routing.v', 'w')
      f.write('\n'.join(routing_wrapper))

  def getRoutingSlotToIOList(self):
    routing_slot_2_io = {}
    for slot in self.compute_slot_to_io.keys():
      io_decl = self.getIOSection(slot)
      io_decl = [io.replace(';', '') for io in io_decl]
      io_decl = [io.split() for io in io_decl] # ensure that no space in width, e.g., [1+2:0]
      
      routing_slot_2_io[slot.getRTLModuleName()] = io_decl
    return routing_slot_2_io

  def getRoutingSlotNameToIOList(self):
    routing_slot_2_io = self.getRoutingSlotToIOList()
    return {slot.getRTLModuleName() : io_list for slot, io_list in routing_slot_2_io.items()}