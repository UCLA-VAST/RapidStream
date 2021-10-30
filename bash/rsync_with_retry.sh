#!/bin/bash

# Trap interrupts and exit instead of continuing the loop
trap "echo Exited!; exit;" SIGINT SIGTERM

MAX_RETRIES=5

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --dir-to-sync)
      DIR_TO_SYNC=$(readlink -f "$2")
      if [ -z ${DIR_TO_SYNC} ]; then
        echo "Incorrect address: ${DIR_TO_SYNC}"
        exit
      fi
      shift # past argument
      shift # past value
      ;;
    --target-server)
      TARGET_SERVER="$2"
      shift # past argument
      shift # past value
      ;;
    --user-name)
      USER_NAME="$2"
      shift # past argument
      shift # past value
      ;;
    --max-retry)
      MAX_RETRIES="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      echo "Unknown parameter: $1"
      exit
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

if [ -z ${USER_NAME} ]; then
  echo "No user name entered"
  exit
fi

if [ -z ${TARGET_SERVER} ]; then
  echo "No target server entered"
  exit
fi

COMMAND="rsync -azhv --delete -r --progress ${DIR_TO_SYNC}/ ${USER_NAME}@${TARGET_SERVER}:${DIR_TO_SYNC}/"
echo "Transfer from $(hostname) to ${TARGET_SERVER}: ${COMMAND}"

i=0
false # Set the initial return value to failure
while [ $? -ne 0 -a $i -lt ${MAX_RETRIES} ]; do
  i=$(($i+1))
  echo "Rsync attempt ${i}..."
  eval ${COMMAND}
done

if [ $i -eq ${MAX_RETRIES} ]; then
  echo "ERROR: Rsync has hit the maximum number of retries, giving up."
  exit
fi

echo "Transfer succeed!"