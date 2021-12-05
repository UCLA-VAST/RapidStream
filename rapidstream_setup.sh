# point to your Gubori license
export GRB_LICENSE_FILE=""

#####################################################################
HOSTNAME=$(hostname)
echo "Setting up on ${HOSTNAME}"

if [ ! -f ${GRB_LICENSE_FILE} ]; then
  echo "ERROR: Gurobi license not found"
  exit
fi

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export RAPID_STREAM_PATH="${SCRIPT_DIR}"

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
