open_project bucket_sort

open_solution solution

cosim_design -trace_level all -disable_deadlock_detection
# export_design -rtl verilog -format ip_catalog -xo bucket_sort.xo

close_project
exit
