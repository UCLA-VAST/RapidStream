# source /curr/einsx7/.bashrc
export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

cd /home/einsx7/auto-parallel/Peregrine/ && source setup.sh
cd -

python3.6 -m autoparallel.FE.Manager config.json
