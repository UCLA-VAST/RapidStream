import json
import os
import re
import sys

from typing import List, Dict
from collections import OrderedDict, defaultdict

from autoparallel.BE.Device import U250


class TimingReportParser:
  def __init__(self, direction: str, timing_report_path: str) -> None:
    """
    direction: Literal['to_anchor', 'from_anchor']
    """
    self.timing_report_path = timing_report_path

    # each timing path is a list of lines
    self.slack_sections = self.splitReportIntoSlackSections()

    self.direction = direction # whether the timing paths in the report are to anchors or from anchors
    self.end_cell_role = 'source' if self.direction == 'to_anchor' else 'sinks'

  def getAnchorConnection(self, filename='') -> Dict[str, Dict[str, List[Dict]]]:
    """
    anchor -> [ {timing_path_source_site, LUT_count, ...}, ... ]
    """
    anchor_connections = defaultdict(list)
    for slack_section in self.slack_sections:
      anchor = self.getAnchorFromSlackSection(slack_section)
      
      timing_path = self.getDataTimingPathOfSlackSection(slack_section)
      if self.direction == 'to_anchor':
        end_cell_site = timing_path[0]
      else:
        end_cell_site = timing_path[-1]

      lut_count = self.getLUTCountInSlackSection(slack_section)

      anchor_connections[anchor].append(
        {
          'src_or_sink' : self.end_cell_role,
          'end_cell_site': end_cell_site,
          'num_lut_on_path' : lut_count,
          'normalized_coordinate' : U250.getCalibratedCoordinatesFromSiteName(end_cell_site),
          'setup_slack': self.getSetupSlackOfSlackSection(slack_section)
        }  
      )

    if filename:
      open(filename, 'w').write(json.dumps(anchor_connections, indent=2))

    return anchor_connections

  def splitReportIntoSlackSections(self) -> List[List[str]]:
    """
    partition the original report into local groups of lines
    each group correspond to one slack section
    """
    report = open(self.timing_report_path)
    slack_sections = []

    curr = []
    for line in report:
      if line.startswith('Slack'):
        slack_sections.append(curr)
        curr = [line]
      else:
        curr.append(line)

    slack_sections.append(curr)

    # not that the first entry is the headings of the report
    return slack_sections[1:]

  def getAnchorFromSlackSection(self, slack_section: List[str]) -> str:
    """
    extract which anchor is in this timing path
    """
    if self.direction == 'to_anchor':
      for line in slack_section:
        if 'Destination:' in line:
          assert '_q0_reg' in line
          # example:   
          # "Destination:            PE_wrapper247_U0_fifo_cout_drain_out_V_write_pass_0_q0_reg/D"
          return re.search(' ([^/ ]+)/', line).group(1)

    elif self.direction == 'from_anchor':
      for line in slack_section:
        if 'Source:' in line:
          assert '_q0_reg' in line
          # example:   
          # "Destination:            PE_wrapper247_U0_fifo_cout_drain_out_V_write_pass_0_q0_reg/D"
          return re.search(' ([^/ ]+)/', line).group(1)    
    else:
      assert False


  def getLUTCountInSlackSection(self, slack_section: List[str]) -> int:
    """
    count how many LUTs are there in the path from/to the anchor
    Example:
    -------------------------------------------------------------------    -------------------
    SLICE_X54Y111        FDRE (Prop_DFF_SLICEL_C_Q)
                                                      0.079     3.871 r  CR_X0Y0_To_CR_X1Y1_ctrl_U0/ap_done_Boundary_X0Y2_To_X2Y2_q_reg/Q
                         net (fo=2, estimated)        0.146     4.017    CR_X0Y0_To_CR_X1Y1_ctrl_U0/ap_done_Boundary_X0Y2_To_X2Y2_q
    SLICE_X54Y111                                                     r  CR_X0Y0_To_CR_X1Y1_ctrl_U0/ap_done_Boundary_X2Y0_To_X2Y2_INST_0/I0
    SLICE_X54Y111        LUT2 (Prop_H6LUT_SLICEL_I0_O)
                                                      0.051     4.068 r  CR_X0Y0_To_CR_X1Y1_ctrl_U0/ap_done_Boundary_X2Y0_To_X2Y2_INST_0/O
                         net (fo=1, estimated)        0.385     4.453    ap_done_Boundary_X2Y0_To_X2Y2_out
    SLICE_X57Y111        FDRE                                         r  ap_done_Boundary_X2Y0_To_X2Y2_q0_reg/D
    -------------------------------------------------------------------    -------------------
    Seems that we only need to count how many lines have the '  LUT' pattern
    """
    return len([line for line in slack_section if '   LUT' in line])

  def getSetupSlackOfSlackSection(self, slack_section: List[str]) -> float:
    """
    extract setup slack. Examples:
    Slack (MET) :             1.347ns  (required time - arrival time)
    Slack (VIOLATED) :        -1.347ns  (required time - arrival time)
    """
    for line in slack_section:
      if re.search('^Slack', line):
        return float(re.search(' ([-]*[ ]*[0-9.]+)ns', line).group(1))
    
    assert False

  def getDataTimingPathOfSlackSection(self, slack_section: List[str]) -> List[str]:
    """
    get all elements from the last/next sequential element to the anchor register
    a sample slack section. The data signal path is the 2nd section divided by '---------'

    Slack (MET) :             0.208ns  (required time - arrival time)
    Source:                 CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/ram_reg/CLKARDCLK
                              (rising edge-triggered cell RAMB36E2 clocked by ap_clk  {rise@0.000ns fall@1.250ns period=2.500ns})
    Destination:            cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0_q0_reg[42]/D
                              (rising edge-triggered cell FDRE clocked by ap_clk  {rise@0.000ns fall@1.250ns period=2.500ns})
    ......
    ......

      Location             Delay type                Incr(ns)  Path(ns)    Netlist Resource(s)
    -------------------------------------------------------------------    -------------------
                          (clock ap_clk rise edge)     0.000     0.000 r  
      BUFGCE_X0Y194        BUFGCE                       0.000     0.000 r  test_bufg/O
      X4Y4 (CLOCK_ROOT)    net (fo=22739, estimated)    2.677     2.677    CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/ap_clk
      SLR Crossing[2->1]   
      RAMB36_X10Y61        RAMB36E2                                     r  CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/ram_reg/CLKARDCLK
    -------------------------------------------------------------------    -------------------
      RAMB36_X10Y61        RAMB36E2 (Prop_RAMB36E2_RAMB36_CLKARDCLK_DOUTBDOUT[10])
                                                        0.830     3.507 r  CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/ram_reg/DOUTBDOUT[10]
                          net (fo=2, estimated)        0.478     3.985    CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/local_cout_V_q0[42]
      SLICE_X156Y305                                                    r  CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/fifo_cout_drain_out_V_V_din[42]_INST_0/I0
      SLICE_X156Y305       LUT5 (Prop_E6LUT_SLICEM_I0_O)
                                                        0.124     4.109 r  CR_X4Y4_To_CR_X5Y5_ctrl_U0/CR_X4Y4_To_CR_X5Y5_routing_U0/CR_X4Y4_To_CR_X5Y5_U0/cout_drain_IO_L1_out_wrapper441_U0/grp_cout_drain_IO_L1_out_fu_28/local_cout_V_U/kernel0_cout_drain_IO_L1_out_boundary_wrapper367_local_cout_V_ram_U/fifo_cout_drain_out_V_V_din[42]_INST_0/O
                          net (fo=1, estimated)        0.572     4.681    cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0_out[42]
      SLICE_X175Y292       FDRE                                         r  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0_q0_reg[42]/D
    -------------------------------------------------------------------    -------------------

                          (clock ap_clk rise edge)     2.500     2.500 r  
      BUFGCE_X0Y194        BUFGCE                       0.000     2.500 r  test_bufg/O
      X4Y4 (CLOCK_ROOT)    net (fo=22739, estimated)    2.268     4.768    ap_clk
      SLR Crossing[2->1]   
      SLICE_X175Y292       FDRE                                         r  cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0_q0_reg[42]/C
                          clock pessimism              0.131     4.899    
                          clock uncertainty           -0.035     4.864    
      SLICE_X175Y292       FDRE (Setup_GFF2_SLICEM_C_D)
                                                        0.025     4.889    cout_drain_IO_L1_out_wrapper441_U0_fifo_cout_drain_out_V_V_din_pass_0_q0_reg[42]
    -------------------------------------------------------------------
                          required time                          4.889    
                          arrival time                          -4.681    
    -------------------------------------------------------------------
                          slack                                  0.208    
    """
    dividing_line_indices = []
    for i in range(len(slack_section)):
      if '-----' in slack_section[i]:
        dividing_line_indices.append(i)

    data_signal_path_begin = dividing_line_indices[1] + 1 # inclusive
    data_signal_path_end = dividing_line_indices[2] # exclusive
    data_signal_path_part = slack_section[data_signal_path_begin : data_signal_path_end]

    data_signal_path = []
    for line in data_signal_path_part:
      match = re.search(' ([^ ]*_X\d+Y\d+) ', line)
      if match:
        data_signal_path.append(match.group(1))

    # remove repetitions
    data_signal_path = list(OrderedDict.fromkeys(data_signal_path))

    return data_signal_path


if __name__ == '__main__':
  curr_dir = os.getcwd()
  assert len(sys.argv) == 2
  report_prefix = sys.argv[1]

  from_anchor_report = f'{curr_dir}/{report_prefix}_timing_path_from_anchor.txt'
  to_anchor_report = f'{curr_dir}/{report_prefix}_timing_path_to_anchor.txt'
  assert os.path.isfile(from_anchor_report)
  assert os.path.isfile(to_anchor_report)

  parser_from_anchor = TimingReportParser('from_anchor', from_anchor_report)
  parser_to_anchor = TimingReportParser('to_anchor', to_anchor_report)
  connection_from_anchor = parser_from_anchor.getAnchorConnection()
  connection_to_anchor = parser_to_anchor.getAnchorConnection()

  anchor_connections = {**connection_from_anchor, **connection_to_anchor}

  # check that one anchor must not exist in both report
  assert len(anchor_connections) == len(connection_from_anchor) + len(connection_to_anchor)

  open(f'{report_prefix}_anchor_connections.json', 'w').write(json.dumps(anchor_connections, indent=2))
  open(f'{report_prefix}_anchor_connections_source.json', 'w').write(json.dumps(connection_to_anchor, indent=2))
  open(f'{report_prefix}_anchor_connections_sink.json', 'w').write(json.dumps(connection_from_anchor, indent=2))
  open(f'{report_prefix}_anchor_connections.json.done.flag', 'w').write(' ')

