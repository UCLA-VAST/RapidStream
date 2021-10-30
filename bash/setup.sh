HOSTNAME=$(hostname)
echo "Setting up on ${HOSTNAME}"

export RAPID_STREAM_PATH="/home/einsx7/auto-parallel/src"
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic
export PATH="${PATH}:${RAPID_STREAM_PATH}/bash"
export RW_BRIDGE_ROOT_DIR="/home/einsx7/auto-parallel/src"
export RW_STITCH_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_07_30/rapidwright.sh"
export RW_ROUTE_SETUP_PATH="/home/einsx7/rapidwright/rapidwright_rwroute/rapidwright.sh"