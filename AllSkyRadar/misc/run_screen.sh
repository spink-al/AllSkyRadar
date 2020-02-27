#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py


screen -x flight_warning
if [ $? == 1 ] ; then
    screen -S flight_warning -c ${MISC_FLDR}/.flight_warning
fi
