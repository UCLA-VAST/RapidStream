HOSTNAME=$(hostname)
echo "Setting up on ${HOSTNAME}"

export RAPID_STREAM_PATH="/home/einsx7/auto-parallel/src"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

#####################################################################

# gurobi 
export GUROBI_HOME="${RAPID_STREAM_PATH}/gurobi/gurobi950/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export PATH="${PATH}:${RAPID_STREAM_PATH}/bash"

# rapidwright
export RAPIDWRIGHT_JAR_PATH=${RAPID_STREAM_PATH}/java/bin/rapidwright-2021.2.0-standalone-lin64.jar
export RW_ROUTE_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_rwroute/rapidwright.sh"

# default configurations for the flow
export VIV_VER="2021.1"
export INVERT_ANCHOR_CLOCK=0
export TARGET_PERIOD=2.5
export BASELINE_ANCHOR_PLACEMENT=0
export RUN_RWROUTE_TEST=0
export OPT_ITER=0
export PYTHONPATH=/home/einsx7/.local/lib/python3.6/site-packages/
