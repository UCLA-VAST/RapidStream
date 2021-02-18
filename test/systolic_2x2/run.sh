# step 1: run hls
VIV_VER=2020.1 vivado_hls -f step1-run-hls.tcl

# step 2: run autoparallel
python3.6 -m autoparallel.FE.Manager systolic_2x2_config.json
if [ $? -ne 0 ]; then
  echo "AutoParallel Front End Failed!"
  exit 1
fi

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

echo "TEST PASSED!"