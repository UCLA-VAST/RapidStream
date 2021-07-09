export HUB=${PWD}/front_end_result.json
export BASE_DIR=/expr/mm/16x12_fix_anchor_clock_no_double_reg

# set up Gurobi solver
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

# prepare the scripts up to slot opt
python3.6 -m autoparallel.BE.BEManager ${HUB} ${BASE_DIR}
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR}
python3.6 -m autoparallel.BE.PairwiseAnchorPlacement $HUB $BASE_DIR SETUP 0
python3.6 -m autoparallel.BE.SlotRouting ${HUB} ${BASE_DIR}
python3.6 -m autoparallel.BE._TestPairwiseRouteStitching ${HUB} ${BASE_DIR}

# fire all slot synthesis & placement. In this example, run everything in one server.
# beware running out of memory

# rsync -azh --delete -r ${BASE_DIR}/ einsx7@u17:${BASE_DIR}
# rsync -azh --delete -r ${BASE_DIR}/ einsx7@u18:${BASE_DIR}
# rsync -azh --delete -r ${BASE_DIR}/ einsx7@u15:${BASE_DIR}
# ssh u15 "cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u15.txt" &
# ssh u17 "cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u17.txt" &
# ssh u18 "cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u18.txt" &
cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u5.txt &
cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u15.txt &
cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u17.txt &
cd ${BASE_DIR}/parallel_run/ && parallel < parallel-place-all-u18.txt &

# fire all ILP anchor placement in one server
cd ${BASE_DIR}/ILP_anchor_placement_iter0 && parallel < parallel-ilp-placement-iter0.txt &
cd ${BASE_DIR}/opt_placement_iter0 && parallel < parallel-opt-placement-u5.txt &

wait

# get the clock route to all anchors surrounding a slot
python3.6 -m autoparallel.BE.Clock.SlotAnchorClockRouting ${HUB} ${BASE_DIR}
cd ${BASE_DIR}/slot_anchor_clock_routing && parallel < parallel-run-slot-clock-routing.txt

# route slots
cd ${BASE_DIR}/slot_routing && parallel < parallel-route-with-ooc-clock-u5.txt

python3.6 -m autoparallel.BE.SLRLevelStitch ${HUB} ${BASE_DIR}

cd ${BASE_DIR}/SLR_level_stitch && parallel < parallel_slr_stitch.txt
cd ${BASE_DIR}/top_stitch && VIV_VER=2020.1 vivado -mode gui -source stitch.tcl
