#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py

DATE=`date +%Y%m%d_%H%M%S`
mv ~/.local/share/VirtualRadar/SavedPlots/Receiver.json ~/.local/share/VirtualRadar/SavedPlots/Receiver.${DATE}
if [ $? == 0 ] ; then
    echo "Old plot saved as ~/.local/share/VirtualRadar/SavedPlots/Receiver."${DATE}
else
    echo "No existing plot?"
fi
