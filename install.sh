# exit when any command fails
set -e +x

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RAPID_STREAM_PATH=${SCRIPT_DIR}

sudo apt install -y git
sudo apt install -y python3-pip

# rapidstream
python3 -m pip install --editable ${RAPID_STREAM_PATH}/python

# autobridge
mkdir ${RAPID_STREAM_PATH}/autobridge
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

sudo apt install -y rsync
sudo apt install -y parallel
sudo apt install -y iverilog
sudo apt install -y default-jre
sudo apt install -y default-jdk
python3 -m pip install psutil

echo "\nFinished RapidStream installation"
echo "\nPlease update RAPID_STREAM_PATH in rapidstream_setup.sh"
echo "\nPlease Obtain a Gurobi license at https://www.gurobi.com/downloads/end-user-license-agreement-academic/"
echo "\nThen update GRB_LICENSE_FILE in rapidstream_setup.sh to point to your Gurobi license file"
