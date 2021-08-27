#!/bin/bash
{

# -------------------------------------------
RW_BRIDGE_ROOT_DIR="/home/einsx7/auto-parallel/src"

VIV_VER="2021.1"
RW_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_07_30/rapidwright.sh"
INVERT_ANCHOR_CLOCK=0
TARGET_PERIOD=2.5
USER_NAME="einsx7"
SERVER_LIST=("u5" "u15" "u17" "u18")
BASELINE_ANCHOR_PLACEMENT=0
RUN_RWROUTE_TEST=0

export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic
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
    --unique-synth-dcp-dir)
      UNIQUE_SYNTH_DCP_DIR=$(readlink -f "$2")
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
    --test-vivado-anchor-placement)
      VIVADO_ANCHOR_PLACEMENT=1
      shift # past argument
      ;;
    --test-random-anchor-placement)
      RANDOM_ANCHOR_PLACEMENT=1
      shift # past argument
      ;;
    --test-rwroute)
      RUN_RWROUTE_TEST=1
      shift # past argument
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      echo "Unknown parameter: $1"
      exit
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

echo "BASE_DIR                  = ${BASE_DIR}"
echo "HUB                       = ${HUB}"
echo "UNIQUE_SYNTH_DCP_DIR      = ${UNIQUE_SYNTH_DCP_DIR}"
echo "INVERT_ANCHOR_CLOCK       = ${INVERT_ANCHOR_CLOCK}"
echo "TARGET_PERIOD             = ${TARGET_PERIOD}"
echo "VIVADO_ANCHOR_PLACEMENT   = ${VIVADO_ANCHOR_PLACEMENT}"
echo "RANDOM_ANCHOR_PLACEMENT   = ${RANDOM_ANCHOR_PLACEMENT}"
echo "VIV_VER                   = ${VIV_VER}"
echo "SERVER_LIST               = ${SERVER_LIST[@]}"

if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 "$1"
fi

PAUSE=15
echo "Waiting for ${PAUSE}s, please check..."
sleep ${PAUSE}


####################################################################

echo $(date +"%T")
echo "Set up scripts..."
mkdir $BASE_DIR
cp ${HUB} $BASE_DIR
chmod -w $BASE_DIR/front_end_result.json

# slot synth
if [ -z "${UNIQUE_SYNTH_DCP_DIR}" ]; then
    python3.6 -m autoparallel.BE.SlotSynthesis \
        --hub_path ${HUB} \
        --base_dir ${BASE_DIR} \
        --vivado_version ${VIV_VER} \
        --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
        --clock_period ${TARGET_PERIOD} \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"
fi

# init slot placement
python3.6 -m autoparallel.BE.InitialSlotPlacement \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --path_to_reuse_synth_dcp ${UNIQUE_SYNTH_DCP_DIR} \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}"

# ILP anchor placement
python3.6 -m autoparallel.BE.PairwiseAnchorPlacement \
    --hub_path $HUB \
    --base_dir $BASE_DIR \
    --option SETUP \
    --which_iteration 0 \
    --test_random_anchor_placement 0 \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}"

# test random anchor placement
python3.6 -m autoparallel.BE.PairwiseAnchorPlacement \
    --hub_path $HUB \
    --base_dir $BASE_DIR \
    --option SETUP \
    --which_iteration 0 \
    --test_random_anchor_placement 1 \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}"

python3.6 -m autoparallel.BE.Baseline.VivadoAnchorPlacement ${HUB} ${BASE_DIR} ${VIV_VER} ${TARGET_PERIOD}  # vivado anchor placement
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER} 0  # normal flow
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER} 1  # test vivado anchor placement
python3.6 -m autoparallel.BE.OptSlotPlacement ${HUB} ${BASE_DIR} ${VIV_VER} 2  # test random anchor placement
python3.6 -m autoparallel.BE.Clock.SlotAnchorClockRouting  ${HUB} ${BASE_DIR} ${VIV_VER} ${INVERT_ANCHOR_CLOCK}
python3.6 -m autoparallel.BE.SlotRouting ${HUB} ${BASE_DIR} ${VIV_VER} 0 ${RUN_RWROUTE_TEST}  # normal flow
python3.6 -m autoparallel.BE.SlotRouting ${HUB} ${BASE_DIR} ${VIV_VER} 1 ${RUN_RWROUTE_TEST}  # baseline: no clock locking
python3.6 -m autoparallel.BE._TestPairwiseRouteStitching ${HUB} ${BASE_DIR} ${VIV_VER}
python3.6 -m autoparallel.BE.SLRLevelStitch ${HUB} ${BASE_DIR} ${VIV_VER} ${RW_SETUP_PATH}

# create scripts to distribute the workloads
SCRIPT_DIR=${BASE_DIR}/scripts
if [ ! -d  ${SCRIPT_DIR} ] ; then
    mkdir ${SCRIPT_DIR}
fi

declare -a steps=(
    "slot_synth" 
    "init_slot_placement" 
    "ILP_anchor_placement_iter0" 
    "opt_placement_iter0"
    "baseline_vivado_anchor_placement"
    "baseline_vivado_anchor_placement_opt"
    "baseline_random_anchor_placement"
    "baseline_random_anchor_placement_opt"
    "slot_routing"
    "baseline_slot_routing_do_not_fix_clock"
)
for step in "${steps[@]}"; do
    SCRIPT=${SCRIPT_DIR}/distributed_run_${step}.sh
    
    for server in ${SERVER_LIST[*]} ; do
        echo "ssh ${server} \"cd ${BASE_DIR}/${step}/ && parallel < parallel_${step}_${server}.txt\" >> ${BASE_DIR}/backend_${step}.log 2>&1 &" >> ${SCRIPT}
    done
    echo "wait" >> ${SCRIPT}
    chmod +x ${SCRIPT}

    TRANSFER_SCRIPT=${SCRIPT_DIR}/transfer_${step}.sh
    for server in ${SERVER_LIST[*]} ; do
        echo "rsync -azh --delete -r ${BASE_DIR}/${step}/ einsx7@${server}:${BASE_DIR}/${step} &" >> ${TRANSFER_SCRIPT}
    done
    echo "wait" >> ${TRANSFER_SCRIPT}
    chmod +x ${TRANSFER_SCRIPT}
done

KILL_SCRIPT=${SCRIPT_DIR}/kill.sh
for server in ${SERVER_LIST[*]} ; do
    echo "ssh ${server} pkill -f vivado" >> ${KILL_SCRIPT}
    echo "ssh ${server} pkill -f system_utilization_tracker" >> ${KILL_SCRIPT}
done
chmod +x ${KILL_SCRIPT}

echo "Distrube scripts to multiple servers..."
for server in ${SERVER_LIST[*]} ; do
    rsync -azh --delete -r ${BASE_DIR}/ einsx7@${server}:${BASE_DIR} &
done
wait

echo "Start system utilization trackers..."
TRACKER=${RW_BRIDGE_ROOT_DIR}/utilities/system_utilization_tracker.py
SETUP_PYTHON_ENV="export PYTHONPATH=/home/einsx7/.local/lib/python3.6/site-packages/"
TRACKING_DIR=${BASE_DIR}/system_utilization_tracking
if [ ! -d  ${TRACKING_DIR} ] ; then
    mkdir ${TRACKING_DIR}
fi
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} \
        ${SETUP_PYTHON_ENV} && \
        python3.6 ${TRACKER} \
        --output_dir ${TRACKING_DIR} \
        --report_prefix ${server} \
        --time_out_hour 5 &
done

####################################################################

echo "Start running"

if [ -z "${UNIQUE_SYNTH_DCP_DIR}" ]; then
    ${SCRIPT_DIR}/distributed_run_slot_synth.sh &
fi

${SCRIPT_DIR}/distributed_run_init_slot_placement.sh &

${SCRIPT_DIR}/distributed_run_ILP_anchor_placement_iter0.sh &

${SCRIPT_DIR}/distributed_run_opt_placement_iter0.sh &

if [[ ${VIVADO_ANCHOR_PLACEMENT} -eq 1 ]]; then
    ${SCRIPT_DIR}/distributed_run_baseline_vivado_anchor_placement.sh &
    ${SCRIPT_DIR}/distributed_run_baseline_vivado_anchor_placement_opt.sh &
fi

if [[ ${RANDOM_ANCHOR_PLACEMENT} -eq 1 ]]; then
    ${SCRIPT_DIR}/distributed_run_baseline_random_anchor_placement.sh &
    ${SCRIPT_DIR}/distributed_run_baseline_random_anchor_placement_opt.sh &
fi

####################################################################
if [ -z "${UNIQUE_SYNTH_DCP_DIR}" ]; then
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
fi

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

####################################################################

echo $(date +"%T")

echo "Post-placement opt finished"
echo "Start routing anchor clocks..."
parallel < ${BASE_DIR}/slot_anchor_clock_routing/parallel-run-slot-clock-routing.txt >> ${BASE_DIR}/backend_slot_clock_routing.log 2>&1  

# routing
echo "Start slot routing..."
${SCRIPT_DIR}/distributed_run_slot_routing.sh &

####################################################################

while :
do
    done_num=$(find ${BASE_DIR}/slot_routing -maxdepth 3 -type f -name phys_opt_routed_with_ooc_clock.dcp | wc -w)
    total_num=$(find ${BASE_DIR}/slot_routing -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Slot Routing: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

# stitching
echo "Start SLR-level stitching..."
parallel < ${BASE_DIR}/SLR_level_stitch/vivado/parallel-route-slr.txt >> ${BASE_DIR}/backend_stitching_routing.log 2>&1 

# top-level stitching
echo "Start Top-level stitching..."
bash ${BASE_DIR}/SLR_level_stitch/vivado/top_stitch/stitch.sh

echo "Finished"
echo $(date +"%T")

# terminate the system tracker
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} pkill -f $TRACKER
done

# kill all child process, including the performance tracker
pkill -P $$

exit $?
}