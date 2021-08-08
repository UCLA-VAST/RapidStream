#!/bin/bash

# -------------------------------------------
VIV_VER="2021.1"

# test not using the RW-unlocked dcps
USE_UNIQUE_SYNTH_DCP=0

INVERT_ANCHOR_CLOCK=0

TARGET_PERIOD=2.5

SERVER_LIST=("u5" "u15" "u17" "u18")

#----------------------------------------------

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --base-dir)
      BASE_DIR=$(readlink -f "$2")
      shift # past argument
      shift # past value
      ;;
    --front-end-result)
      HUB=$(readlink -f "$2")
      shift # past argument
      shift # past value
      ;;
    --unique-synth-dcp-path)
      UNIQUE_SLOT_SYNTH_PATH=$(readlink -f "$2")
      USE_UNIQUE_SYNTH_DCP=1
      shift # past argument
      shift # past value
      ;;
    --invert-anchor-clock)
      INVERT_ANCHOR_CLOCK=1
      shift # past argument
      ;;
    --target-period)
      TARGET_PERIOD="$2"
      shift # past argument
      shift # past value
      ;;
    --vivado-ver)
      VIV_VER="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

echo "BASE_DIR                = ${BASE_DIR}"
echo "HUB                     = ${HUB}"
echo "USE_UNIQUE_SYNTH_DCP    = ${USE_UNIQUE_SYNTH_DCP}"
echo "UNIQUE_SLOT_SYNTH_PATH  = ${UNIQUE_SLOT_SYNTH_PATH}"
echo "INVERT_ANCHOR_CLOCK     = ${INVERT_ANCHOR_CLOCK}"
echo "TARGET_PERIOD           = ${TARGET_PERIOD}"
echo "VIV_VER                 = ${VIV_VER}"
echo "SERVER_LIST             = ${SERVER_LIST[@]}"

if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 "$1"
fi

echo "Waiting for 15s, please check..."
sleep 15

echo $(date +"%T")

# set up Gurobi
echo "Set up Gurobi env variables"
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

echo "Set up scripts..."
mkdir $BASE_DIR
cp ${HUB} $BASE_DIR
chmod -w $BASE_DIR/front_end_result.json

if [[ ${USE_UNIQUE_SYNTH_DCP} -eq 1 ]]; then
    echo "Copy unique synth.dcp to base directory..."
    cp -r ${UNIQUE_SLOT_SYNTH_PATH} $BASE_DIR/
else
    python3.6 -m autoparallel.BE.SlotSynthesis ${HUB} ${BASE_DIR} ${VIV_VER} ${INVERT_ANCHOR_CLOCK} ${TARGET_PERIOD}
fi

python3.6 -m autoparallel.BE.InitialSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER} ${USE_UNIQUE_SYNTH_DCP} 
python3.6 -m autoparallel.BE.PairwiseAnchorPlacement $HUB $BASE_DIR SETUP 0
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE.Clock.SlotAnchorClockRouting  ${HUB} ${BASE_DIR} ${VIV_VER} ${INVERT_ANCHOR_CLOCK}
python3.6 -m autoparallel.BE.SlotRouting ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE._TestPairwiseRouteStitching ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE.SLRLevelStitch ${HUB} ${BASE_DIR} ${VIV_VER}

echo "Distrube scripts to multiple servers..."
for server in ${SERVER_LIST[*]} ; do
    rsync -azh --delete -r ${BASE_DIR}/ einsx7@${server}:${BASE_DIR} &
done

wait

echo "Start running"
# synthesis
if [[ ${USE_UNIQUE_SYNTH_DCP} -eq 0 ]]; then
    for server in ${SERVER_LIST[*]} ; do
        ssh ${server} "cd ${BASE_DIR}/slot_synth/ && parallel < parallel-synth-${server}.txt" >> ${BASE_DIR}/backend_synth.log 2>&1 &
    done
fi

# placement
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/init_slot_placement/ && parallel < parallel-place-all-${server}.txt" >> ${BASE_DIR}/backend_slot_place.log 2>&1  &
done

# fire all ILP anchor placement in one server
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "source /home/einsx7/.bashrc && cd ${BASE_DIR}/ILP_anchor_placement_iter0/ && parallel < parallel-ilp-placement-iter0-${server}.txt" >> ${BASE_DIR}/backend_anchor_place.log 2>&1   &
done

for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/opt_placement_iter0/ && parallel < parallel-opt-placement-${server}.txt" >> ${BASE_DIR}/backend_slot_opt.log 2>&1   &
done

while :
do
    done_num=$(find ${BASE_DIR}/slot_synth -maxdepth 2 -type f -name *.dcp.done.flag | wc -w)
    total_num=$(find ${BASE_DIR}/slot_synth -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Synthesis: ${done_num}/${total_num} finished"

    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

while :
do
    done_num=$(find ${BASE_DIR}/init_slot_placement -maxdepth 2 -type f -name *.dcp.done.flag | wc -w)
    total_num=$(find ${BASE_DIR}/init_slot_placement -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Slot Placement: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

while :
do
    done_num=$(find ${BASE_DIR}/ILP_anchor_placement_iter0 -maxdepth 2 -type f -name *.done.flag | wc -w)
    total_num=$(find ${BASE_DIR}/ILP_anchor_placement_iter0 -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Anchor Placement: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

while :
do
    done_num=$(find ${BASE_DIR}/opt_placement_iter0 -maxdepth 2 -type f -name *post_placed_opt.dcp | wc -w)
    total_num=$(find ${BASE_DIR}/opt_placement_iter0 -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Slot Placement Opt: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done


echo $(date +"%T")

echo "Post-placement opt finished"
echo "Start routing anchor clocks..."
cd ${BASE_DIR}/slot_anchor_clock_routing && parallel < parallel-run-slot-clock-routing.txt >> ${BASE_DIR}/backend_slot_clock_routing.log 2>&1  
cd -

# routing
echo "Start slot routing..."
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} "cd ${BASE_DIR}/slot_routing/ && parallel < parallel-route-with-ooc-clock-${server}.txt" >> ${BASE_DIR}/backend_slot_routing.log 2>&1   &
done

while :
do
    done_num=$(find ${BASE_DIR}/slot_routing -maxdepth 2 -type f -name phys_opt_routed_with_ooc_clock.dcp | wc -w)
    total_num=$(find ${BASE_DIR}/slot_routing -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Slot Routing: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

echo "Finished"
echo $(date +"%T")
