HOSTNAME=$(hostname)
echo "Setting up on ${HOSTNAME}"

export RAPID_STREAM_PATH="/home/einsx7/auto-parallel/src"

# gurobi 
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic
export PATH="${PATH}:${RAPID_STREAM_PATH}/bash"

# rapidwright
export RW_STITCH_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_07_30/rapidwright.sh"
export RW_ROUTE_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_rwroute/rapidwright.sh"

# default configurations for the flow
export VIV_VER="2021.1"
export INVERT_ANCHOR_CLOCK=0
export TARGET_PERIOD=2.5
export BASELINE_ANCHOR_PLACEMENT=0
export RUN_RWROUTE_TEST=0
export OPT_ITER=0
export PYTHONPATH=/home/einsx7/.local/lib/python3.6/site-packages/