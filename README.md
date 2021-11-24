
# About

- RapidStream takes in a Vivado HLS dataflow design, then generates a fully placed and routed checkpoint.

- RapidStream adopts a divide-and-conquer approach at the behavior level that achieves 5-7X speed up compared to the vanilla Vivado flow.

- The key insight of RapidStream is to utilize the fact that we can additionally pipeline the FIFO connections, which create additional flexibility for split placement and routing without timing degradation.

- Currently RapidStream results cannot run on board as we are not compatible with the Vitis infrastructure. The next step is to develop a customized IO shell so that the hardware accelerator could communicate with the host.

- More details could be found in our FPGA 2022 paper:
    - RapidStream: Fast HLS-to-Bitstream Timing Closure throughParallelized and Physical-Integrated Compilation

# Install

- RapidStream

```
git clone https://github.com/Licheng-Guo/AutoParallel.git
python3 -m pip install --editable ./AutoParallel/python
```

- AutoBridge
```
git clone https://github.com/Licheng-Guo/AutoBridge.git
python3 -m pip install --editable ./AutoBridge/in-develop/src
```

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

- Xilinx Vivado HLS 2019.2 or 2020.1

- Xilinx Vivado 2021.1

- Update the environment variables in `RapidStream/bash/setup.sh` according to your installment specifics.

# Examples

There are 6 examples to demonstrate the flow. Each one includes:

- The HLS source code and the HLS synthesis project

- A reference configuration file

- A one-click script to run the whole flow. Note that you need to update the environment variables in the script.

In order to reproduce the results as in the paper, we include a reference floorplanning result as this step is non-deterministic