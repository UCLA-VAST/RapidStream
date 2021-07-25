export HUB=${PWD}/front_end_result.json
export BASE_DIR=/expr/mm/16x12_test_07_25/

export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

SERVER_LIST=("u5" "u15" "u17" "u18")

VIV_VER="2020.1"
ROUTE_VIV_VER="2020.2"

# test not using the RW-unlocked dcps
USE_UNIQUE_SYNTH_DCP=1
UNIQUE_SLOT_SYNTH_PATH="/expr/mm/16x12_test_07_24/unique_slot_synth"

mkdir $BASE_DIR

if [[ ${USE_UNIQUE_SYNTH_DCP} -eq 1 ]]; then
    cp -r ${UNIQUE_SLOT_SYNTH_PATH} $BASE_DIR/
else
    python3.6 -m autoparallel.BE.SlotSynthesis ${HUB} ${BASE_DIR} ${VIV_VER}
fi

python3.6 -m autoparallel.BE.InitialSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER} ${USE_UNIQUE_SYNTH_DCP}
python3.6 -m autoparallel.BE.PairwiseAnchorPlacement $HUB $BASE_DIR SETUP 0
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE.Clock.SlotAnchorClockRouting  ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE.SlotRouting ${HUB} ${BASE_DIR} ${ROUTE_VIV_VER}
python3.6 -m autoparallel.BE._TestPairwiseRouteStitching ${HUB} ${BASE_DIR} ${VIV_VER}

for server in ${SERVER_LIST[*]} ; do
    rsync -azh --delete -r ${BASE_DIR}/ einsx7@${server}:${BASE_DIR} &
done

wait

# synthesis
if [[ ${USE_UNIQUE_SYNTH_DCP} -eq 1 ]]; then
    for server in ${SERVER_LIST[*]} ; do
        ssh ${server} "cd ${BASE_DIR}/slot_synth/ && parallel < parallel-synth-${server}.txt" &
    done
fi

# placement
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/init_slot_placement/ && parallel < parallel-place-all-${server}.txt" &
done

# fire all ILP anchor placement in one server
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "source /home/einsx7/.bashrc && cd ${BASE_DIR}/ILP_anchor_placement_iter0/ && parallel < parallel-ilp-placement-iter0-${server}.txt" &
done

for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/opt_placement_iter0/ && parallel < parallel-opt-placement-${server}.txt" &
done

wait

cd ${BASE_DIR}/slot_anchor_clock_routing && parallel < parallel-run-slot-clock-routing.txt

# routing
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/slot_routing/ && parallel < parallel-route-with-ooc-clock-${server}.txt" &
done

wait
