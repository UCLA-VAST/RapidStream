# hack an OOC checkpoint and mark it as non-OOC 

DCP=$1
WORK_DIR=unset_dcp_hd_reconfigurable
mkdir $WORK_DIR
cp $DCP $WORK_DIR
cd $WORK_DIR
unzip $DCP
rm $DCP
sed -i 's/HDPlatform Name=\"1\"/HDPlatform Name=\"0\"/g' dcp.xml
sed -i '/<HDInfo Name="HD.RECONFIGURABLE"\/>/d' dcp.xml
sed -i '/set_property HD.RECONFIGURABLE true \[current_design\]/d' *.xdc
zip -r $DCP *
