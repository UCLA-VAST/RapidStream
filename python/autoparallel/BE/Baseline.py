import json
import logging
import os
import sys


def getVivadoFlowWithOrigRTL(
  fpga_part_name,
  orig_rtl_path
):
  script = []

  # to differentiate with the original top
  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # read in the generated wrappers
  script.append(f'set WRAPPER_PATH "{WRAPPER_PATH}"') 
  script.append(r'set wrapper_files [glob ${WRAPPER_PATH}/*.v]') 
  script.append(r'read_verilog ${wrapper_files}') 

  # instantiate IPs used in the RTL. Use "-nocomplain" in case no IP is used
  script.append(r'set orig_ip_files [glob -nocomplain ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # clock xdc
  script.append(f'read_xdc "clock.xdc"')

  script.append(f'synth_design -top "{TOP_NAME}" -mode out_of_context')
  script.append(f'write_checkpoint synth.dcp')

  script.append(f'opt_design')
  script.append(f'write_checkpoint synth-opt.dcp')

  script.append(f'place_design -directive Explore')
  script.append(f'write_checkpoint place.dcp')

  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint place-opt.dcp')

  script.append(f'route_design -directive Explore')
  script.append(f'write_checkpoint route.dcp')

  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint route-opt.dcp')

  return script


def createClockFromBUFGXDC(target_period=2.50):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_pins test_bufg/O]')
  return xdc


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  assert len(sys.argv) == 6, 'input (1) the path to the front end result file and (2) the target directory'
  hub_path = sys.argv[1]
  base_dir = sys.argv[2]
  VIV_VER = sys.argv[3]
  TOP_NAME = sys.argv[4]
  WRAPPER_PATH = sys.argv[5]

  hub = json.loads(open(hub_path, 'r').read())

  baseline_dir = f'{base_dir}/baseline'
  os.mkdir(baseline_dir)
  os.mkdir(f'{baseline_dir}/pipelined_baseline')

  xdc = createClockFromBUFGXDC()
  script = getVivadoFlowWithOrigRTL(hub['FPGA_PART_NAME'], hub['ORIG_RTL_PATH'])

  open(f'{baseline_dir}/pipelined_baseline/clock.xdc', 'w').write('\n'.join(xdc))
  open(f'{baseline_dir}/pipelined_baseline/baseline.tcl', 'w').write('\n'.join(script))

