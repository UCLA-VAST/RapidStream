RAPID_STREAM_PATH=/home/einsx7/auto-parallel/src

source ${RAPID_STREAM_PATH}/rapidstream_setup.sh

export HLS_PROJECT_PATH="./13x14/kernel3_u250"
export SERVER_LIST=("u5" "u15" "u17" "u18")
export MAIN_SERVER="u18"
export RUN_DIR=/expr/cnn/13x14_3FF_double_reg_rerun_11_20

################################################

echo "[preparing] Unzip the pre-syntehsized HLS project..."
unzip -q cnn_13x14.zip

. ${RAPID_STREAM_PATH}/bash/prepare.sh

echo "[front end] Running the front end (phase 1)..."
python3.6 -m rapidstream.FE.Manager cnn_13x14_config.json

echo "[back end] Running the back end (phase 2 and 3)..."
${RAPID_STREAM_PATH}/bash/run_back_end.sh \
    --run-dir ${RUN_DIR} \
    --front-end-result ./front_end_result.json \
    --vivado-ver 2021.1 \
    --target-period 2.6 \
    --server-list "${SERVER_LIST[*]}" \
    --main-server ${MAIN_SERVER} \
    --user-name $USER
