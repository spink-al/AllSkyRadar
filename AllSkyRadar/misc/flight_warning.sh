#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py
cd ${FW_FLDR}

pwd
while true ; do 
    nc -w 30 localhost 33333 | python3 flight_warning_MLAT.py
    sleep 5s 
done


