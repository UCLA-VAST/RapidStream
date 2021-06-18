#! /usr/bin/python3.6
import logging
import copy

class CreateCtrlSlotWrapper:
  def __init__(
      self,
      routing_wrapper_creater,
      floorplan,
      slot_manager):
    self.routing_wrapper_creater = routing_wrapper_creater
    self.routing_slot_to_io = routing_wrapper_creater.getSlotToIOList()
    self.floorplan = floorplan
    self.s2v = self.floorplan.getSlotToVertices()
    self.all_active_slots = slot_manager.getActiveSlotsIncludeRouting()
    self.all_slot_names_list = [s.getName() for s in self.all_active_slots]
    self.s_axi_slot = None
    self.in_slot_pipeline_style = routing_wrapper_creater.in_slot_pipeline_style
    
    self.__findSAxiSlot()

  def __findSAxiSlot(self):
    """ determine which slot contains the s_axi_control """
    for slot, vertices in self.s2v.items():
      v_names = [v.name for v in vertices]
      if any('control' in name and 's_axi' in name for name in v_names):
        self.s_axi_slot = slot
        break
    assert self.s_axi_slot

  def __getSAxiSlotCtrlIO(self, s_axi_slot):
    ctrl_io_list = []

    # connect to top-level port
    ctrl_io_list.append(['input', 'ap_clk'])
    ctrl_io_list.append(['input', 'ap_rst_n'])
    
    # broadcast the ap_start and ap_rst_n signals
    # collect the ap_done signals
    # check in each direction if there is a neighbor slot
    ctrl_fanout_dir = []
    for dir in ['UP', 'DOWN', 'RIGHT', 'LEFT']:

      # be careful a Slot has multiple naming convention
      if s_axi_slot.getNeighborSlotName(dir) in self.all_slot_names_list:
        ctrl_fanout_dir.append(dir)

    for dir in ctrl_fanout_dir:
      boundary_name = s_axi_slot.getBoundarySegmentName(dir)
      ctrl_io_list.append(['output', f'ap_start_{boundary_name}'])
      ctrl_io_list.append(['output', f'ap_rst_n_{boundary_name}'])
      ctrl_io_list.append(['input',  f'ap_done_{boundary_name}'])

    return ctrl_io_list

  def __getCtrlInboundAndOutboundDir(self, slot):
    assert slot != self.s_axi_slot
    # relative position to the s_axi_slot
    # the ctrl signal first pass vertically from the s_axi_slot
    # then from each slot in the same row as the s_axi_slot, signals pass horizontally
    is_same_column = slot.getPositionX() == self.s_axi_slot.getPositionX()
    is_same_row = slot.getPositionY() == self.s_axi_slot.getPositionY()
    is_to_the_left = slot.getPositionX() < self.s_axi_slot.getPositionX()
    is_to_the_down = slot.getPositionY() < self.s_axi_slot.getPositionY()
    
    # ----|----dst
    # ----|----dst
    #     |
    # ---src---...
    #     |----
    # ----|----
    # which direction the ap_start comes from
    # ctrl_source_dir = None
    # if is_same_column:
    #   if is_to_the_down:
    #     ctrl_source_dir = 'UP'
    #   else:
    #     ctrl_source_dir = 'DOWN'
    # else:
    #   if is_to_the_left:
    #     ctrl_source_dir = 'RIGHT'
    #   else:
    #     ctrl_source_dir = 'LEFT'

    ctrl_source_dir = None
    if is_same_row:
      if is_to_the_left:
        ctrl_source_dir = 'RIGHT'
      else:
        ctrl_source_dir = 'LEFT'
    else:

      if is_to_the_down:
        ctrl_source_dir = 'UP'
      else:
        ctrl_source_dir = 'DOWN'

    # which directions the ap_starts go to
    # if the slot is on the same row as the s_axi slot, broadcast to all directions except to the s_axi
    # otherwise, only pass the control signal vertically away from the source
    ctrl_fanout_dir = []
    if is_same_row:
      for dir in ['UP', 'DOWN', 'RIGHT', 'LEFT']:
        if dir == ctrl_source_dir:
          continue
        if slot.getNeighborSlotName(dir) in self.all_slot_names_list:
          ctrl_fanout_dir.append(dir)
    else:
      if is_to_the_down:
        if slot.getNeighborSlotName('DOWN') in self.all_slot_names_list:
          ctrl_fanout_dir = ['DOWN']
      else:
        if slot.getNeighborSlotName('UP') in self.all_slot_names_list:
          ctrl_fanout_dir = ['UP']

    return ctrl_source_dir, ctrl_fanout_dir

  def __getOtherSlotCtrlIO(self, slot):
    ctrl_io_list = []

    # no global ap_rst_n
    ctrl_io_list.append(['input', 'ap_clk'])

    ctrl_source_dir, ctrl_fanout_dir = self.__getCtrlInboundAndOutboundDir(slot)

    # ctrl in
    # [FIXME] it is possible that there is not routing slot at this direction 
    assert slot.getNeighborSlotName(ctrl_source_dir) in self.all_slot_names_list

    boundary_name = slot.getBoundarySegmentName(ctrl_source_dir)
    ctrl_io_list.append(['input', f'ap_start_{boundary_name}'])
    ctrl_io_list.append(['input', f'ap_rst_n_{boundary_name}'])
    ctrl_io_list.append(['output',  f'ap_done_{boundary_name}'])

    # ctrl fan-out
    for dir in ctrl_fanout_dir:
      fanout_boundary_name = slot.getBoundarySegmentName(dir)
      ctrl_io_list.append(['output', f'ap_start_{fanout_boundary_name}'])
      ctrl_io_list.append(['output', f'ap_rst_n_{fanout_boundary_name}'])
      ctrl_io_list.append(['input',  f'ap_done_{fanout_boundary_name}'])

    return ctrl_io_list

  def __getIOSection(self, slot):

    # filter out all ap signals from routing wrapper
    routing_io_list = self.routing_slot_to_io[slot]
    routing_io_list = [io for io in routing_io_list if not io[-1].startswith('ap_') ]     

    if slot == self.s_axi_slot:
      ctrl_io_list = self.__getSAxiSlotCtrlIO(slot)
    else:
      ctrl_io_list= self.__getOtherSlotCtrlIO(slot)

    # the actual rtl code
    io_section = ['  ' + ' '.join(io) + ',' for io in routing_io_list + ctrl_io_list]
    io_section[-1] = io_section[-1].replace(',', '')
    
    return io_section

  def __connectCtrlSignalsForSAXISlot(self, s_axi_slot):
    ctrl_io_list = self.__getSAxiSlotCtrlIO(s_axi_slot)

    connect = []
    
    # note that there are also non-s-axi modules in this slot
    connect.append(f'wire ap_start;')
    connect.append(f'wire ap_done;')
    connect.append(f'wire ap_idle;')
    connect.append(f'wire ap_ready;')
    connect.append(f'wire ap_continue = 1;')

    # connect ap_start
    connect.append('wire ap_start_orig;')
    out_bound_ap_start = [io[-1] for io in ctrl_io_list if 'ap_start' in io[-1] ]
    for sig in out_bound_ap_start:
      connect.append(f'(* keep = "true" *) reg {sig}_q;')
      connect.append(f'always @ (posedge ap_clk) {sig}_q <= ap_start_orig;')
      connect.append(f'assign {sig} = {sig}_q;')
    connect.append(f'assign ap_start = ap_start_orig;') # connect to self

    # connect ap_rst_n
    out_bound_ap_rst_n = [io[-1] for io in ctrl_io_list if 'ap_rst_n_' in io[-1] ]
    for sig in out_bound_ap_rst_n:
      connect.append(f'(* keep = "true" *) reg {sig}_q;')
      connect.append(f'always @ (posedge ap_clk) {sig}_q <= ap_rst_n;') # ap_rst_n connect to top level port
      connect.append(f'assign {sig} = {sig}_q;')

    # connect ap_done
    in_bound_ap_done = [io[-1] for io in ctrl_io_list if 'ap_done' in io[-1] ]
    for sig in in_bound_ap_done:
      connect.append(f'(* keep = "true" *) reg {sig}_q;')

      # hold each individual ap_done to deal with synchronous ending
      connect.append(f'always @ (posedge ap_clk) begin')
      connect.append(f'  if (!ap_rst_n) {sig}_q <= 0;')
      connect.append(f'  else {sig}_q <= {sig}_q | {sig};')
      connect.append(f'end')

    in_bound_ap_done_reg = [f'{sig}_q' for sig in in_bound_ap_done]
    in_bound_ap_done_reg.append('ap_done') # connect to self
    connect.append(f'wire ap_done_final = ' + ' & '.join(in_bound_ap_done_reg) + ';')

    # others
    connect.append(f'wire ap_ready_final = ap_done_final;')
    connect.append(f'wire ap_idle_final = ap_done_final;')

    return connect

  def __connectCtrlSignalsForOtherSlot(self, slot):
    ctrl_io_list = self.__getOtherSlotCtrlIO(slot)
    connect = []

    ctrl_source_dir, ctrl_fanout_dir = self.__getCtrlInboundAndOutboundDir(slot)
    in_boundary_name = slot.getBoundarySegmentName(ctrl_source_dir)
    
    # connect to the inner instance
    connect.append(f'wire ap_start;')
    connect.append(f'wire ap_rst_n;')
    connect.append(f'wire ap_done;')
    connect.append(f'wire ap_idle;')
    connect.append(f'wire ap_ready;')
    connect.append(f'wire ap_continue = 1;')

    # ap_start
    connect.append(f'(* keep = "true" *) reg ap_start_{in_boundary_name}_q;')
    connect.append(f'always @ (posedge ap_clk) ap_start_{in_boundary_name}_q <= ap_start_{in_boundary_name};')
    for dir in ctrl_fanout_dir:
      fanout_boundary_name = slot.getBoundarySegmentName(dir)
      connect.append(f'assign ap_start_{fanout_boundary_name} = ap_start_{in_boundary_name}_q;')
    connect.append(f'assign ap_start = ap_start_{in_boundary_name}_q;') # for the inner wrapper

    # ap_rst_n
    connect.append(f'(* keep = "true" *) reg ap_rst_n_{in_boundary_name}_q;')
    connect.append(f'always @ (posedge ap_clk) ap_rst_n_{in_boundary_name}_q <= ap_rst_n_{in_boundary_name};')
    for dir in ctrl_fanout_dir:
      fanout_boundary_name = slot.getBoundarySegmentName(dir)
      connect.append(f'assign ap_rst_n_{fanout_boundary_name} = ap_rst_n_{in_boundary_name}_q;')
    connect.append(f'assign ap_rst_n = ap_rst_n_{in_boundary_name}_q;')

    # ap_done, in reverse direction
    out_bound_ap_done_reg = []
    for dir in ctrl_fanout_dir:
      fanout_boundary_name = slot.getBoundarySegmentName(dir)
      ap_done_name = f'ap_done_{fanout_boundary_name}'
      connect.append(f'(* keep = "true" *) reg {ap_done_name}_q;')
      connect.append(f'always @ (posedge ap_clk) begin')
      connect.append(f'  if (!ap_rst_n) {ap_done_name}_q <= 0;')
      connect.append(f'  else {ap_done_name}_q <= {ap_done_name}_q | {ap_done_name};')
      connect.append(f'end')

      out_bound_ap_done_reg.append(f'{ap_done_name}_q')

    out_bound_ap_done_reg.append('ap_done') # collect the ap_done of the current slot
    connect.append(f'assign ap_done_{in_boundary_name} = ' + ' & '.join(out_bound_ap_done_reg) + ';')

    return connect

  def __getInnerWrapperInst(self, slot):
    slot_inst = []
    
    # if targeting implementation, we mark the modules as black box
    # so that they can be replaced later by separately implemented DCPs
    slot_inst.append(f'\n\n  (* dont_touch = "yes" *) {slot.getRTLModuleName()}_routing {slot.getRTLModuleName()}_routing_U0 (')

    routing_slot_io_list = self.routing_slot_to_io[slot]
    for io in routing_slot_io_list:
      slot_inst.append(f'    .{io[-1]}({io[-1]}),') 
      
    # handle the last io
    slot_inst[-1] = slot_inst[-1].replace(',', '\n  );') 
    
    return slot_inst

  def getCtrlInclusiveWrapper(self, slot):

    wrapper = ['\n\n`timescale 1 ns / 1 ps']

    wrapper.append(f'\n\nmodule {slot.getRTLModuleName()}_ctrl (')
    wrapper += self.__getIOSection(slot)
    wrapper.append(f');')

    if slot == self.s_axi_slot:
      wrapper += self.__connectCtrlSignalsForSAXISlot(slot)
    else:
      wrapper += self.__connectCtrlSignalsForOtherSlot(slot)

    wrapper += self.__getInnerWrapperInst(slot)

    wrapper.append(f'endmodule')

    # include the inner wrapper
    wrapper += self.routing_wrapper_creater.getRoutingInclusiveWrapper(slot)

    return wrapper
  
  def createCtrlInclusiveWrapperForAll(self, dir='ctrl_wrapper_rtl'):
    for slot in self.all_active_slots:
      wrapper = self.getCtrlInclusiveWrapper(slot)
      f = open(dir + '/' + slot.getRTLModuleName()+'_ctrl.v', 'w')
      f.write('\n'.join(wrapper))

  def getSlotToIOList(self):
    """maintain the same interface as CreateSlotWrapper """
    def processIODecl(io_decl):
      io_decl = [io.replace(',', '') for io in io_decl]
      io_decl = [io.split() for io in io_decl] # ensure that no space in width, e.g., [1+2:0]
      return io_decl

    slot_2_io = {}
    for slot in self.all_active_slots:
      io_section = self.__getIOSection(slot)
      io_section = processIODecl(io_section)
      slot_2_io[slot] = io_section

    return slot_2_io

  def getSlotNameToIOList(self):
    slot_2_io = self.getSlotToIOList()
    return {slot.getRTLModuleName() : io_list for slot, io_list in slot_2_io.items()}

  # include all signals except top-level ports
  def getSlotToDirToWires(self):

    # note that routing_slot_to_dir_to_wires excludes all ap signals
    routing_slot_to_dir_to_wires = self.routing_wrapper_creater.getDirectionOfPassingEdgeWiresUpdated()

    ctrl_slot_to_dir_to_wires = copy.deepcopy(routing_slot_to_dir_to_wires)

    # get rid of the 'IN' and 'OUT'
    # TODO: remove them from the global router
    for slot, dir_to_wires in ctrl_slot_to_dir_to_wires.items():
      for dir in ['UP', 'DOWN', 'RIGHT', 'LEFT']:
        wires = []
        if f'{dir}_IN' in dir_to_wires:
          wires += dir_to_wires[f'{dir}_IN']
          dir_to_wires.pop(f'{dir}_IN')
        if f'{dir}_OUT' in dir_to_wires:
          wires += dir_to_wires[f'{dir}_OUT']          
          dir_to_wires.pop(f'{dir}_OUT')

        if wires:
          dir_to_wires[dir] = wires

    for slot, dir_to_wires in ctrl_slot_to_dir_to_wires.items():
      if slot == self.s_axi_slot:
        ctrl_io_list = self.__getSAxiSlotCtrlIO(slot)
      else:
        ctrl_io_list= self.__getOtherSlotCtrlIO(slot)

      for dir in ['UP', 'DOWN', 'RIGHT', 'LEFT']:
        boundary_name = slot.getBoundarySegmentName(dir)
        for io in ctrl_io_list:
          if boundary_name in io[-1]:
            if dir in dir_to_wires:
              dir_to_wires[dir].append(io)
            else:
              dir_to_wires[dir] = [io]

    return ctrl_slot_to_dir_to_wires

  def getSlotNameToDirToWires(self):
    ctrl_slot_to_dir_to_wires = self.getSlotToDirToWires()
    ctrl_slotname_to_dir_to_wires = {slot.getRTLModuleName() : dir_to_wires \
                                    for slot, dir_to_wires in ctrl_slot_to_dir_to_wires.items()}
    return ctrl_slotname_to_dir_to_wires