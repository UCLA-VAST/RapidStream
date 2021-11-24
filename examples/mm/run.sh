RAPID_STREAM_PATH=/home/einsx7/auto-parallel/src

source ${RAPID_STREAM_PATH}/bash/setup.sh

export HLS_PROJECT_PATH="./16x12/mm_16x12"
export SERVER_LIST=("u5" "u15" "u17" "u18")
export USER_NAME=einsx7
export RUN_DIR=/expr/mm/16x12_3FF_double_reg_rerun_11_20

################################################

echo "[preparing] Unzip the pre-syntehsized HLS project..."
unzip -q mm_16x12.zip

. ${RAPID_STREAM_PATH}/bash/prepare.sh

echo "[front end] Running the front end (phase 1)..."
python3.6 -m rapidstream.FE.Manager mm_16x12_config.json

echo "[back end] Running the back end (phase 2 and 3)..."
${RAPID_STREAM_PATH}/bash/run_back_end.sh \
    --run-dir ${RUN_DIR} \
    --front-end-result ./front_end_result.json \
    --vivado-ver 2021.1 \
    --target-period 2.7 \
    --server-list "${SERVER_LIST[*]}" \
    --user-name ${USER_NAME}
