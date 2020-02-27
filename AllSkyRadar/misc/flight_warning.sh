#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py
cd ${FW_FLDR}

pwd
while true ; do 
    nc -w 30 localhost 33333 | python flight_warning_M_CLEAN_CORR_MERGE2_nowrite.py
    sleep 5s 
done


