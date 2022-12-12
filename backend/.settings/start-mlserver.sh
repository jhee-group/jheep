#!/bin/bash

set -e

[ -z ${MLSERVER_MODELS_DIR+x} ] && MLSERVER_MODELS_DIR="/mnt/models"
[ -z ${MLSERVER_PATH+y} ] && MLSERVER_PATH="/home/kaiuser/mlserver"

reqfile="${MLSERVER_MODELS_DIR}/requirements.txt"
if [ -f ${reqfile} ]; then
  pip install --upgrade --user --no-cache-dir -r ${reqfile}
fi

cd ${MLSERVER_PATH}
mlserver start ${MLSERVER_MODELS_DIR}
