open_project bucket_sort

set_top bucket_sort
add_files "src/concat_engine.cpp"
add_files "src/bucket_sort.cpp"
add_files "src/local_shift.cpp"
add_files "src/local_group.cpp"
add_files "src/bitonic_sort.cpp"
add_files "src/constant.h"
add_files -tb "src/test_bucket_sort.cpp"

open_solution solution
set_part xcu280-fsvh2892-2L-e
create_clock -period 300.000000MHz -name default

config_dataflow -strict_mode warning
set_clock_uncertainty 27.000000%
config_rtl -enable_maxiConservative=1
config_interface -m_axi_addr64
config_sdx -target xocc

csynth_design

close_project
exit
