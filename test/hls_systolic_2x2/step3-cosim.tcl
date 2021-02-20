open_project kernel0
open_solution solution
cosim_design -trace_level all -disable_deadlock_detection

close_project
puts "Pack XO successfully"
exit
