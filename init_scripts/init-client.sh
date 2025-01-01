#!/bin/bash

# change if needed
NON_ROOT_USER="client"
MESSAGIST_PATH="/home/$NON_ROOT_USER/A61" # location of cloned repo

ENV_NAME="messagist"
ENV_FILE="$MESSAGIST_PATH/messagist/environment.yml"
PROTO_SCRIPT="$MESSAGIST_PATH/messagist/proto.sh"

export PATH="/home/$NON_ROOT_USER/miniconda/bin:$PATH"
if ! command -v conda &>/dev/null; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p /home/$NON_ROOT_USER/miniconda
    rm /tmp/miniconda.sh
fi
eval "$(/home/$NON_ROOT_USER/miniconda/bin/conda shell.bash hook)"

if ! conda env list | grep -q "$ENV_NAME"; then
    conda env create -f "$ENV_FILE"
fi

cd "$MESSAGIST_PATH/messagist"
conda run -n "$ENV_NAME" bash "$PROTO_SCRIPT"

conda init
