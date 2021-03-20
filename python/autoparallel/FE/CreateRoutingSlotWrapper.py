#! /usr/bin/python3.6
import logging
from typing import List

class CreateRoutingSlotWrapper:

  def __init__(self, compute_wrapper_creater, floorplan, global_router, top_rtl_parser):
    self.compute_wrapper_creater = compute_wrapper_creater
    self.compute_slot_to_io = compute_wrapper_creater.getSlotToIOList()
    self.floorplan = floorplan
    self.global_router = global_router
    self.top_rtl_parser = top_rtl_parser
    self.pure_routing_slots = global_router.getPureRoutingSlots()
    self.target = compute_wrapper_creater.target # maintain the same interface with CreateSlotWrapper

    self.edge_wire_to_suffix_index = {}

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

  def getIOSection(self, slot, is_pure_routing = False):
    """
    Differentiate compute slots and pure routing slots
    Add ap signals for pure routing signals for compatibility
    """
    inter_slot_e_io = self.getPassingEdgeIO(slot)
    io_section = inter_slot_e_io

    if not is_pure_routing:
      io_section += self.getInterSlotEdgeIO(slot)
      io_section += self.getWrapperCtrlIO(slot, inter_slot_e_io)
    else:
      # add pseudo control signals to maintain the same interface format
      io_section += [
        'input ap_start,',
        'output ap_done,',
        'output ap_idle,',
        'output ap_ready,',
        'input ap_continue,',
        'input ap_clk,',
        'input ap_rst_n,'
      ]

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

        else: # out-bound edges. Note the direction of assignment is reversed than the inbound case
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
    """ instantiate each slot """
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
    is_pure_routing = self.global_router.isPureRoutingSlot(slot)

    wrapper = ['\n\n`timescale 1 ns / 1 ps']

    wrapper.append(f'\n\nmodule {slot.getRTLModuleName()}_routing (')
    wrapper += self.getIOSection(slot, is_pure_routing)
    wrapper.append(f');')

    wrapper += self.connectPassingWires(slot)

    if not is_pure_routing:
      wrapper += self.connectInterSlotEdgeWiresToIO(slot)
      wrapper += self.getInnerWrapperInst(slot)
    else:
      wrapper += [
        'assign ap_done = 1;',
        'assign ap_idle = 1;',
        'assign ap_ready = 1;'
      ]

    wrapper.append(f'endmodule')

    # include the inner wrapper
    if not is_pure_routing:
      wrapper += self.compute_wrapper_creater.createSlotWrapper(slot)

    return wrapper

  def createRoutingInclusiveWrapperForAll(self, dir='wrapper_rtl'):
    def generateWrapper(wrapper, slot):
      f = open(dir + '/' + slot.getRTLModuleName()+'_routing.v', 'w')
      f.write('\n'.join(wrapper))

    for slot, wrapper_io_list in self.compute_slot_to_io.items():
      routing_wrapper = self.getRoutingInclusiveWrapper(slot)
      generateWrapper(routing_wrapper, slot)

    for slot in self.pure_routing_slots:
      routing_wrapper = self.getRoutingInclusiveWrapper(slot)
      generateWrapper(routing_wrapper, slot)    

  def getSlotToIOList(self):
    """maintain the same interface as CreateSlotWrapper """
    def processIODecl(io_decl):
      io_decl = [io.replace(',', '') for io in io_decl]
      io_decl = [io.split() for io in io_decl] # ensure that no space in width, e.g., [1+2:0]
      return io_decl

    routing_slot_2_io = {}
    for slot in self.compute_slot_to_io.keys():
      io_decl = self.getIOSection(slot)
      io_decl = processIODecl(io_decl)
      routing_slot_2_io[slot] = io_decl

    for slot in self.pure_routing_slots:
      io_decl = self.getIOSection(slot, is_pure_routing=True)
      io_decl = processIODecl(io_decl)
      routing_slot_2_io[slot] = io_decl

    return routing_slot_2_io

  def getSlotNameToIOList(self):
    routing_slot_2_io = self.getSlotToIOList()
    return {slot.getRTLModuleName() : io_list for slot, io_list in routing_slot_2_io.items()}

  def getEmptyWrappers(self):
    """
    in vivado flow, to declare a module instance as black box, we must have an empty initilization
    """
    empty_wrappers = []
    routing_slot_2_io = self.getSlotToIOList()
    for slot, io_decl in routing_slot_2_io.items():
      empty_wrappers.append(f'\n\nmodule {slot.getRTLModuleName()}_routing (')
      empty_wrappers += [' '.join(io) + ',' for io in io_decl]
      empty_wrappers[-1] = empty_wrappers[-1].replace(',', '')
      empty_wrappers.append(f');')
      empty_wrappers.append(f'endmodule')
    return empty_wrappers

  def getDirectionOfPassingEdgeWiresUpdated(self):
    """
    Since the routing wrapper will rename the wires
    the mapping from boudary to wires from global routing will be outdated
    Here the mapping is updated by attaching suffixes to the wire name
    The problem is that the same wire will go in and out of the same slot, though through different boundary
    To correctly set the index in their appendix, we start with the IN side
    And we sort the list of modified IO
    For each wire of inbound edges, we look for the first partial match in the list of modified IO
    for a passing edge, the one with smaller index will be used.
    Then we remove the used ones from the list of modified IO
    After all inbound edges are processed, we go with outbound edges.
    Example: a slot may have input "foobar_din_pass_0" on one edge
    and output "foo_bar_din_pass_1" on the other edge
    The original slot_to_wire mapping will have two "foobar_din" on two different directions
    We need to change each of them accordingly to add the suffix
    The wire at the IN side always has a smaller index 

    change 1: slot -> dir -> wires 
    change 2: routing inclusive wrapper causes the wires to have duplications, add suffix to differentiate them
    change 3: add the width information as well because of backend's need
    """

    def partialMatchAndRemove():
      updated_io_list = []
      for orig_wire in orig_wire_list:
        for updated_io in routing_wrapper_io_list[:] :
          if f'{orig_wire}_pass_' in updated_io[-1]:
            updated_io_list.append(updated_io)

            # remove so that this io will not be matched again
            routing_wrapper_io_list.remove(updated_io)

            # break to prevent redundant matching
            break

      dir_to_wires[dir] = updated_io_list

    # at this point no width or i/o direction is appended
    slot_to_dir_to_wires = self.global_router.getDirectionOfPassingEdgeWires()
    
    routing_slot_2_io = self.getSlotNameToIOList() # the return has separated direction, width and wire name
    
    for slot, dir_to_wires in slot_to_dir_to_wires.items():
      routing_wrapper_io_list = routing_slot_2_io[slot]
      routing_wrapper_wire_list = [io[-1] for io in routing_wrapper_io_list]

      # sort the updated io list so that small index comes first
      routing_wrapper_io_list.sort(key=lambda io : io[-1])

      # first match the IN side because inbound edges have smaller indices
      for dir, orig_wire_list in dir_to_wires.items():
        if '_IN' in dir:
          partialMatchAndRemove()
        
      # next match the OUT side. Previously matched IOs have been removed
      for dir, orig_wire_list in dir_to_wires.items():
        if '_OUT' in dir:
          partialMatchAndRemove()

      # only ctrl IOs should be left
      assert all(io[-1].startswith('ap_') or '_axi' in io[-1] or 'interrupt' in io[-1] \
        for io in routing_wrapper_io_list)

    # the width and i/o direction is also attached
    return slot_to_dir_to_wires