export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/pr/solver/gurobi902/gurobi.lic

export VIV_VER=2019.2
# export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
source /opt/tools/xilinx/Vitis/${VIV_VER}/settings64.sh
source /opt/xilinx/xrt/setup.sh

TOOL=vivado_hls

# step 1: run hls
${TOOL} -f step1-run-hls.tcl

# step 2: run autoparallel
python3.6 -m autoparallel.FE.Manager systolic_2x2_config.json
if [ $? -ne 0 ]; then
  echo "AutoParallel Front End Failed!"
  exit 1
fi
rm -f parse*

# step 3: verilator lint test of the generated wrappers
for wrapper in wrapper_rtl/*.v; do
  # disable warning-STMTDLY
  # disable warning-SYMRSVDWORD
  # make warning-IMPLICIT error
  verilator --lint-only ${wrapper} -I./wrapper_rtl -I./ip_interface_rtl -I./kernel0/solution/syn/verilog/ --Wno-fatal --Wno-STMTDLY --Wno-SYMRSVDWORD --Werror-IMPLICIT 2>&1 | grep ${wrapper}

  # grep should not find any occurrence of ${wrapper}
  if [ $? -eq 0 ]; then
    echo "${wrapper} failed verilator test"
    exit 1
  else
    echo "${wrapper} passed verilator test!"
  fi
done

# step 4: run cosim
for wrapper in wrapper_rtl/*.v; do
  cat ${wrapper} >> kernel0_kernel0.v
done

mv kernel0_kernel0.v ./kernel0/solution/syn/verilog/

timeout 300 ${TOOL} -f step3-cosim.tcl
if [ $? -ne 0 ]; then
  echo "cosim"
  exit 1
fi

echo "PASS!"