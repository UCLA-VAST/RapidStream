#!/bin/bash

# create the working directory on every server
for server in ${SERVER_LIST[*]} ; do
    echo "[preparing] Creating working directory on ${server}..."
    ssh ${USER}@${server} mkdir -p ${RUN_DIR}
done

echo "[preparing] Distribute the source HLS project to all servers..."
cp -r ${HLS_PROJECT_PATH}/solution*/syn/verilog ${RUN_DIR}/orig_rtl
for server in ${SERVER_LIST[*]} ; do
    rsync -azh --delete -r ${RUN_DIR}/ ${USER}@${server}:${RUN_DIR} &
done
wait
