export RUN_DIR=[where-to-run]
export HLS_PROJECT_PATH="./13x14/kernel3_u250"
export SERVER_LIST=("IP_SERVER_1" "IP_SERVER_2" "IP_SERVER_3" "IP_SERVER_4")  # any number of servers will work
export MAIN_SERVER="IP_SERVER_1"  # the one where you launch the run

################################################

if [ -z "${RAPID_STREAM_PATH}" ]; then
    echo "ERROR: need to export RAPID_STREAM_PATH first"
    exit
else
    source ${RAPID_STREAM_PATH}/rapidstream_setup.sh
fi

if [ -d "${RUN_DIR}" ]; then
    echo "ERROR: the RUN_DIR already exists: ${RUN_DIR}"
    exit
fi

###############################################

echo "[preparing] Unzip the pre-syntehsized HLS project..."
unzip -qn cnn_13x14.zip

. ${RAPID_STREAM_PATH}/bash/prepare.sh

echo "[front end] Running the front end (phase 1)..."
python3 -m rapidstream.FE.Manager cnn_13x14_config.json

echo "[back end] Running the back end (phase 2 and 3)..."
${RAPID_STREAM_PATH}/bash/run_back_end.sh \
    --run-dir ${RUN_DIR} \
    --front-end-result ./front_end_result.json \
    --vivado-ver 2021.1 \
    --target-period 2.6 \
    --server-list "${SERVER_LIST[*]}" \
    --main-server ${MAIN_SERVER} \
    --user-name $USER \
    # --invert-anchor-clock \
    # --use-rwroute-to-stitch
