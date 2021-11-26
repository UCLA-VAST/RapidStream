
# About

- RapidStream takes in a Vivado HLS dataflow design, then generates a fully placed and routed checkpoint.

- RapidStream adopts a divide-and-conquer approach at the behavior level that achieves 5-7X speed up compared to the vanilla Vivado flow.

- The key insight of RapidStream is to utilize the fact that we can additionally pipeline the FIFO connections, which create additional flexibility for split placement and routing without timing degradation.

- More details could be found in our FPGA 2022 paper:
    - RapidStream: Fast HLS-to-Bitstream Timing Closure throughParallelized and Physical-Integrated Compilation

# Install

- RapidStream

```
git clone https://github.com/Licheng-Guo/RapidStream.git
python3 -m pip install --editable ./RapidStream/python
```

- AutoBridge
```
git clone https://github.com/Licheng-Guo/AutoBridge.git
python3 -m pip install --editable ./AutoBridge/in-develop/src
```

- RapidWright
```
https://www.rapidwright.io/docs/Automatic_Install.html#automatic-install
```
After installing, copy the checkpoint merger `java/mergeDCP.java` to `${RAPIDWRIGHT_HOME}/RapidWright/src/com/xilinx/rapidwright/examples/`, then compile the merger by `make` in the RapidWright home.

- Iverilog
```
sudo apt install iverilog
```

- The Gurobi solver

  - Register and download the `Gurobi Optimizer` at https://www.gurobi.com/downloads/gurobi-optimizer-eula/
  - Unzip the package to your desired directory
  - Obtain an academic license at https://www.gurobi.com/downloads/end-user-license-agreement-academic/
  - The environment variable `GUROBI_HOME` needs to point to the installation directory, so that Gurobi can be detected by AutoBridge.
    - `export GUROBI_HOME= [ where you install ]`
    - `export GRB_LICENSE_FILE= [ path to your license file ]`
    - `export PATH="${PATH}:${GUROBI_HOME}/bin"`
    - `export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"`

- Update the environment variables in `RapidStream/bash/setup.sh` according to your installment specifics.

- Xilinx Vivado HLS 2019.2 or 2020.1

- Xilinx Vivado 2021.1


# Examples

There are 6 examples to demonstrate the flow. Each one includes:

- The HLS source code and the HLS synthesis project

- A reference configuration file

- A one-click script to run the whole flow. 

- Note that you need to update the environment variables in the script.

In order to reproduce the results as in the paper, we include a reference floorplanning result as this step is non-deterministic. To re-run the Phase 1 floorplanning process from scratch, delete the "ResultReuse" field in the JSON configuration file.


# File Organizations

- `examples` provide six benchmarks and one-click script to run RapidStream.

- `python/rapidstream` contains the main implementation of RapidStream.
  - `python/rapidstream/FE` corresponds to the front end transformation on the HLS-generated RTL (Phase 1 in the paper)
  - `python/rapidstream/BE` corresponds to the back end parallel implementation (Phase 2, 3 in the paper)  

- `java/` contains tools implemented in RapidWright, including the checkpoint stitcher for Phase 3 (`java/mergeDCP.java`
)

- `bash/` include scripts to glue together various part of the flow. 
  - `bash/run_back_end.sh` is the main flow of Phase 2 and 3.

# Next Step

- Currently RapidStream results cannot run on board as we are not compatible with the Vitis workflow. 

- The next step is to develop a customized IO shell so that the RapidStream bitstream could communicate with the host.