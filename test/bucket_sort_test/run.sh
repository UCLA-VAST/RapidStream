export GUROBI_HOME="/home/einsx7/pr/solver/gurobi902/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
export GRB_LICENSE_FILE=/home/einsx7/gurobi.lic

export VIV_VER=2019.2
# export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

cd /home/einsx7/auto-parallel/Peregrine/ && source setup.sh
cd -

TOOL=vivado_hls

# step 1: run hls
${TOOL} -f step1-run-hls.tcl

# step 2: run rapidstream
python3.6 -m rapidstream.FE.Manager bucket_sort_config_2.json
if [ $? -ne 0 ]; then
  echo "RapidStream Front End Failed!"
  exit 1
fi
rm -f parse*

# step 3: verilator lint test of the generated wrappers
for wrapper in wrapper_rtl/*.v; do
  # disable warning-STMTDLY
  # disable warning-SYMRSVDWORD
  # make warning-IMPLICIT error
  verilator --lint-only ${wrapper} -I./wrapper_rtl -I./ip_interface_rtl -I./bucket_sort/solution/syn/verilog/ --Wno-fatal --Wno-STMTDLY --Wno-SYMRSVDWORD --Werror-IMPLICIT 2>&1 | grep ${wrapper}

  # grep should not find any occurrence of ${wrapper}
  if [ $? -eq 0 ]; then
    echo "CRITICAL WARNINIG: ${wrapper} failed verilator test"
    # exit 1
  else
    echo "${wrapper} passed verilator test!"
  fi
done

# step 4: run cosim
for wrapper in wrapper_rtl/*.v; do
  cat ${wrapper} >> bucket_sort_bucket_sort.v
done

mv bucket_sort_bucket_sort.v ./bucket_sort/solution/syn/verilog/

timeout 1000 ${TOOL} -f step3-cosim.tcl
if [ $? -ne 0 ]; then
  echo "cosim"
  exit 1
fi

echo "PASS!"
