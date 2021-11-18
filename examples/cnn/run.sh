# source /curr/einsx7/.bashrc
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

TARGET_DIR=/expr/cnn/13x14_3FF_double_reg_rerun_11_18

python3.6 -m autoparallel.FE.Manager cnn_13x14_config.json

/home/einsx7/auto-parallel/src/bash/run_back_end.sh \
    --base-dir ${TARGET_DIR} \
    --front-end-result ./front_end_result.json \
    --vivado-ver 2021.1 \
    --target-period 2.6 \
    --server-list "u5 u14 u17 u18"
 