open_project mm_16x2
set_top kernel0
add_files "kernel_kernel.cpp"
add_files "kernel_kernel.h"
add_files -tb "kernel_host.cpp"
open_solution solution
set_part xcu250-figd2104-2L-e
create_clock -period 300.000000MHz -name default
config_dataflow -strict_mode warning
set_clock_uncertainty 27.000000%
config_rtl -enable_maxiConservative=1
config_interface -m_axi_addr64
config_sdx -target xocc
# csim_design
csynth_design
# cosim_design -rtl verilog -setup

close_project
puts "HLS completed successfully"
exit

