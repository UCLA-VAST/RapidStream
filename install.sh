# exit when any command fails
set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RAPID_STREAM_PATH=${SCRIPT_DIR}

# rapidstream
python3 -m pip install --editable ${RAPID_STREAM_PATH}/python

# autobridge
mkdir ${RAPID_STREAM_PATH}/autobridge
sudo apt install git
git clone https://github.com/Licheng-Guo/AutoBridge.git ${RAPID_STREAM_PATH}/autobridge

cd ${RAPID_STREAM_PATH}/autobridge
AUTOBRIDGE_STABLE_VERSION=91015d000
git checkout ${AUTOBRIDGE_STABLE_VERSION}
cd -

python3 -m pip install --editable ${RAPID_STREAM_PATH}/autobridge/in-develop/src

# rapidwright
RAPIDWRIGHT_JAR=https://github.com/Xilinx/RapidWright/releases/download/v2021.2.0-beta/rapidwright-2021.2.0-standalone-lin64.jar
wget ${RAPIDWRIGHT_JAR} -P ${RAPID_STREAM_PATH}/java/bin

# gurobi
mkdir ${RAPID_STREAM_PATH}/gurobi
wget https://packages.gurobi.com/9.5/gurobi9.5.0_linux64.tar.gz -P ${RAPID_STREAM_PATH}/gurobi
tar -xvf ${RAPID_STREAM_PATH}/gurobi/* -C ${RAPID_STREAM_PATH}/gurobi/

sudo apt install rsync
sudo apt install parallel
sudo apt install iverilog
sudo apt install default-jre
sudo apt install default-jdk
python3 -m pip install psutil

echo "Finished installation"
echo "Please update RAPID_STREAM_PATH in rapidstream_setup.sh"
echo "Please Obtain a Gurobi license at https://www.gurobi.com/downloads/end-user-license-agreement-academic/"
echo "Then update GRB_LICENSE_FILE in rapidstream_setup.sh to point to your Gurobi license file"
