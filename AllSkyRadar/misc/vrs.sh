#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py

cd ${VRS_FLDR}
mono VirtualRadar.exe -nogui
