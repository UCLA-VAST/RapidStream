#!/bin/bash
{

source ../rapidstream_setup.sh

# read arguments from command line
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --run-dir)
      RUN_DIR=$(readlink -f "$2")
      shift # past argument
      shift # past value
      ;;
    --front-end-result)
      HUB=$(readlink -f "$2")
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
    --server-list)
      read -r -a SERVER_LIST <<< "$2"
      shift # past argument
      shift # past value
      ;;
    --main-server)
      MAIN_SERVER="$2"
      shift # past argument
      shift # past value
      ;;
    --user-name)
      USER_NAME="$2"
      shift # past argument
      shift # past value
      ;;
    --opt-iter)
      OPT_ITER="$2"
      shift # past argument
      shift # past value
      ;;
    --use-rwroute-to-stitch)
      USE_RWROUTE_TO_STITCH=1
      shift # past argument
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
    --setup-only)
      SETUP_ONLY=1
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

echo "RUN_DIR                   = ${RUN_DIR}"
echo "HUB                       = ${HUB}"
echo "INVERT_ANCHOR_CLOCK       = ${INVERT_ANCHOR_CLOCK}"
echo "TARGET_PERIOD             = ${TARGET_PERIOD}"
echo "VIVADO_ANCHOR_PLACEMENT   = ${VIVADO_ANCHOR_PLACEMENT}"
echo "RANDOM_ANCHOR_PLACEMENT   = ${RANDOM_ANCHOR_PLACEMENT}"
echo "VIV_VER                   = ${VIV_VER}"
echo "SERVER_LIST               = ${SERVER_LIST[@]}"
echo "MAIN_SERVER               = ${MAIN_SERVER}"
echo "USER_NAME                 = ${USER_NAME}"
echo "SETUP_ONLY                = ${SETUP_ONLY[@]}"
echo "OPT_ITER                  = ${OPT_ITER}"
echo "USE_RWROUTE_TO_STITCH     = ${USE_RWROUTE_TO_STITCH}"

if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 "$1"
fi

PAUSE=15
echo "Waiting for ${PAUSE}s, please check..."
sleep ${PAUSE}

BASE_DIR=${RUN_DIR}/backend

####################################################################

echo $(date +"%T")
echo "Set up scripts..."
mkdir $BASE_DIR
cp ${HUB} $BASE_DIR
chmod -w $BASE_DIR/front_end_result.json

# start logging from here
{

# slot synth
python3.6 -m rapidstream.BE.SlotSynthesis \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
    --clock_period ${TARGET_PERIOD} \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}" \
    --orig_rtl_path ${RUN_DIR}/orig_rtl

# init slot placement
python3.6 -m rapidstream.BE.InitialSlotPlacement \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --clock_period ${TARGET_PERIOD} \
    --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}"

for iter in $(seq 0 ${OPT_ITER}); do
    # ILP anchor placement
    python3.6 -m rapidstream.BE.PairwiseAnchorPlacement \
        --hub_path $HUB \
        --base_dir $BASE_DIR \
        --option SETUP \
        --which_iteration ${iter} \
        --test_random_anchor_placement 0 \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"

    # test random anchor placement
    python3.6 -m rapidstream.BE.PairwiseAnchorPlacement \
        --hub_path $HUB \
        --base_dir $BASE_DIR \
        --option SETUP \
        --which_iteration ${iter} \
        --test_random_anchor_placement 1 \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"

    # baseline: vivado anchor placement
    python3.6 -m rapidstream.BE.Baseline.VivadoAnchorPlacement  \
        --hub_path ${HUB} \
        --base_dir ${BASE_DIR} \
        --vivado_version ${VIV_VER} \
        --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
        --which_iteration ${iter} \
        --clock_period ${TARGET_PERIOD} \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"

    # normal flow
    python3.6 -m rapidstream.BE.OptSlotPlacement \
        --hub_path ${HUB} \
        --base_dir ${BASE_DIR} \
        --vivado_version ${VIV_VER} \
        --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
        --which_iteration ${iter} \
        --run_mode 0 \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"

    # test vivado anchor placement
    python3.6 -m rapidstream.BE.OptSlotPlacement \
        --hub_path ${HUB} \
        --base_dir ${BASE_DIR} \
        --vivado_version ${VIV_VER} \
        --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
        --which_iteration ${iter} \
        --run_mode 1  \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"

    # test random anchor placement
    python3.6 -m rapidstream.BE.OptSlotPlacement \
        --hub_path ${HUB} \
        --base_dir ${BASE_DIR} \
        --vivado_version ${VIV_VER} \
        --invert_non_laguna_anchor_clock ${INVERT_ANCHOR_CLOCK} \
        --which_iteration ${iter} \
        --run_mode 2  \
        --user_name ${USER_NAME} \
        --server_list_in_str "${SERVER_LIST[*]}"
done

python3.6 -m rapidstream.BE.Clock.SlotAnchorClockRouting \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --is_invert_clock ${INVERT_ANCHOR_CLOCK} \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}"

# normal flow
python3.6 -m rapidstream.BE.SlotRouting \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}" \
    --main_server_name ${MAIN_SERVER}

# baseline: no clock locking
python3.6 -m rapidstream.BE.SlotRouting \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --do_not_fix_clock  \
    --user_name ${USER_NAME} \
    --server_list_in_str "${SERVER_LIST[*]}" \
    --main_server_name ${MAIN_SERVER}  

python3.6 -m rapidstream.BE._TestPairwiseRouteStitching ${HUB} ${BASE_DIR} ${VIV_VER}

python3.6 -m rapidstream.BE.SLRLevelStitch  \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER} \
    --clock_period ${TARGET_PERIOD} \
    --rw_stitch_setup_path ${RW_STITCH_SETUP_PATH} \
    --rw_route_setup_path ${RW_ROUTE_SETUP_PATH}

# baseline: vanilla vivado flow
python3.6 -m rapidstream.BE.Baseline.VivadoOrigFlow \
    --hub_path ${HUB} \
    --base_dir ${BASE_DIR} \
    --vivado_version ${VIV_VER}

# create scripts to distribute the workloads
SCRIPT_DIR=${BASE_DIR}/scripts
if [ ! -d  ${SCRIPT_DIR} ] ; then
    mkdir ${SCRIPT_DIR}
fi

declare -a steps=(
    "slot_synth" 
    "init_slot_placement" 
    "slot_anchor_clock_routing"
    "slot_routing"
    "baseline_slot_routing_do_not_fix_clock"
)
for i in $(seq 0 ${OPT_ITER}); do
    steps+=("ILP_anchor_placement_iter${i}") 
    steps+=("opt_placement_iter${i}") 
    steps+=("baseline_vivado_anchor_placement_iter${i}") 
    steps+=("baseline_vivado_anchor_placement_opt_iter${i}") 
    steps+=("baseline_random_anchor_placement_iter${i}") 
    steps+=("baseline_random_anchor_placement_opt_iter${i}") 
done

for step in "${steps[@]}"; do
    SCRIPT=${SCRIPT_DIR}/distributed_run_${step}.sh
    echo "# Start distrubuted run: ${step}" >> ${SCRIPT}

    for server in ${SERVER_LIST[*]} ; do
        echo "ssh ${server} \"source ${RAPID_STREAM_PATH}/rapidstream_setup.sh && cd ${BASE_DIR}/${step}/ && parallel < parallel_${step}_${server}.txt\" >> ${BASE_DIR}/backend_${step}.log 2>&1 &" >> ${SCRIPT}
    done
    echo "wait" >> ${SCRIPT}
    # at each server, create the done flag
    for server in ${SERVER_LIST[*]} ; do
        echo "ssh ${server} touch ${BASE_DIR}/${step}/done.flag" >> ${SCRIPT}
        echo "echo \"ssh ${server} touch ${BASE_DIR}/${step}/done.flag. Status: \$?\"" >> ${SCRIPT}
    done

    echo "# Finish distrubuted run: ${step}" >> ${SCRIPT}
    chmod +x ${SCRIPT}

    TRANSFER_SCRIPT=${SCRIPT_DIR}/transfer_${step}.sh
    for server in ${SERVER_LIST[*]} ; do
        echo "rsync -azh --delete -r ${BASE_DIR}/${step}/ ${USER_NAME}@${server}:${BASE_DIR}/${step} &" >> ${TRANSFER_SCRIPT}
    done
    echo "wait" >> ${TRANSFER_SCRIPT}
    chmod +x ${TRANSFER_SCRIPT}
done

KILL_SCRIPT=${SCRIPT_DIR}/kill.sh
echo "echo \"WARNING: All process with ${VIV_VER} in name will be killed in 10 seconds!\"" >> ${KILL_SCRIPT}
echo "sleep 10"  >> ${KILL_SCRIPT}
for server in ${SERVER_LIST[*]} ; do
    echo "ssh ${server} pkill -f ${VIV_VER}" >> ${KILL_SCRIPT}
    echo "ssh ${server} pkill -f system_utilization_tracker" >> ${KILL_SCRIPT}
done
chmod +x ${KILL_SCRIPT}

CEPF_WARMUP_SCRIPT=${SCRIPT_DIR}/cepf_warmup_vivado.sh
for server in ${SERVER_LIST[*]} ; do
    echo "ssh ${server} VIV_VER=${VIV_VER} vivado -mode batch" >> ${CEPF_WARMUP_SCRIPT}
done

TRACKING_DIR=${BASE_DIR}/system_utilization_tracking
if [ ! -d  ${TRACKING_DIR} ] ; then
    mkdir ${TRACKING_DIR}
fi

########################################################

echo "Distribute scripts to multiple servers..."
for server in ${SERVER_LIST[*]} ; do
    rsync -azh --delete -r ${BASE_DIR}/ ${USER_NAME}@${server}:${BASE_DIR} &
done
wait

if [ -n "${SETUP_ONLY}" ]; then
    echo "Finish setup"
    exit
fi

echo "Loading Vivado ${VIV_VER} on all servers. This may take a while if running for the first time..."
parallel < ${CEPF_WARMUP_SCRIPT}

echo "Start system utilization trackers..."
TRACKER=${RAPID_STREAM_PATH}/utilities/system_utilization_tracker.py
SETUP_PYTHON_ENV="export PYTHONPATH=/home/${USER_NAME}/.local/lib/python3.6/site-packages/"
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} \
        PYTHONPATH=${PYTHONPATH} \
        python3.6 ${TRACKER} \
        --output_dir ${TRACKING_DIR} \
        --report_prefix ${server} \
        --time_out_hour 5 &
done

####################################################################

echo "Start running"

${SCRIPT_DIR}/distributed_run_slot_synth.sh &

${SCRIPT_DIR}/distributed_run_init_slot_placement.sh &

for i in $(seq 0 ${OPT_ITER}); do
    ${SCRIPT_DIR}/distributed_run_ILP_anchor_placement_iter${i}.sh &

    ${SCRIPT_DIR}/distributed_run_opt_placement_iter${i}.sh &
done

if [[ ${VIVADO_ANCHOR_PLACEMENT} -eq 1 ]]; then
    for i in $(seq 0 ${OPT_ITER}); do
        ${SCRIPT_DIR}/distributed_run_baseline_vivado_anchor_placement_iter${i}.sh &
        ${SCRIPT_DIR}/distributed_run_baseline_vivado_anchor_placement_opt_iter${i}.sh &
    done
fi

if [[ ${RANDOM_ANCHOR_PLACEMENT} -eq 1 ]]; then
    for i in $(seq 0 ${OPT_ITER}); do
        ${SCRIPT_DIR}/distributed_run_baseline_random_anchor_placement_iter${i}.sh &
        ${SCRIPT_DIR}/distributed_run_baseline_random_anchor_placement_opt_iter${i}.sh &
    done
fi

${SCRIPT_DIR}/distributed_run_slot_anchor_clock_routing.sh &

${SCRIPT_DIR}/distributed_run_slot_routing.sh &

####################################################################
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
    done_num=$(find ${BASE_DIR}/ILP_anchor_placement_iter0 -maxdepth 2 -type f -name *place_anchors.tcl.done.flag | wc -w)
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

while :
do
    done_num=$(find ${BASE_DIR}/slot_anchor_clock_routing -maxdepth 3 -type f -name set_anchor_clock_route.tcl | wc -w)
    total_num=$(find ${BASE_DIR}/slot_anchor_clock_routing -maxdepth 1 -type d -name CR* | wc -l)
    echo "[$(date +"%T")] Slot Anchor Clock Routing: ${done_num}/${total_num} finished"
    
    if (( ${done_num} == ${total_num} )); then
        break
    fi

    sleep 30
done

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
if [ -z "${USE_RWROUTE_TO_STITCH}" ]; then
    echo "By default, use Vivado to stitch the islands"
    STITCH_TOOL=vivado
else
    echo "Use RWRoute to stitch the islands"
    STITCH_TOOL=rwroute
fi
parallel < ${BASE_DIR}/SLR_level_stitch/${STITCH_TOOL}/parallel-route-slr.txt >> ${BASE_DIR}/backend_stitching_routing.log 2>&1 

# top-level stitching
echo "Start Top-level stitching..."
bash ${BASE_DIR}/SLR_level_stitch/${STITCH_TOOL}/top_stitch/stitch.sh

echo "Finished"
echo $(date +"%T")

# copy the remote tracking results back
for server in ${SERVER_LIST[*]} ; do
    rsync -a ${server}:${TRACKING_DIR}/ ${TRACKING_DIR}/
done

# terminate the system tracker
for server in ${SERVER_LIST[*]} ; do
    ssh ${server} pkill -f $TRACKER
done

# remove the temp storage on other servers
for server in ${SERVER_LIST[*]} ; do
  if [ $server != $MAIN_SERVER ]; then
    echo "rm ${BASE_DIR} from $server"
    ssh $server rm -rf ${BASE_DIR}
  fi  
done

# end logging from here
} 2>&1 | tee -a ${BASE_DIR}/rapid_stream.log 

# kill all child process, including the performance tracker
pkill -P $$

exit $?
}