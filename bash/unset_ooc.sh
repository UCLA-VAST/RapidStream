# hack an OOC checkpoint and mark it as non-OOC 

DCP=$1
WORK_DIR=unset_dcp_ooc
mkdir $WORK_DIR
cp $DCP $WORK_DIR
cd $WORK_DIR
unzip $DCP
rm $DCP
sed -i 's/OutOfContext Name=\"1\"/OutOfContext Name=\"0\"/g' dcp.xml
zip -r $DCP *
