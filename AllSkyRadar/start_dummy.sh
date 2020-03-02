#!/bin/bash
# Read config
. ./ASR_Conf.py

while true ; do 
    echo "START: "`date` 
    python3 ${BIN_FLDR}/dummy.py 
    sleep 2s

done
