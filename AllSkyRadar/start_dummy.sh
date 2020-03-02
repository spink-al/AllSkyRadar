#!/bin/bash
# Read config
. ./ASR_Conf.py
mkdir -p /tmp/AllSkyRadar/
sudo ln -sf /tmp/AllSkyRadar/dummy_1080p.jpg /var/www/html/dummy_1080p.jpg
sudo cp misc/dummy.html /var/www/html/ 
while true ; do 
    echo "START: "`date` 
    python3 ${BIN_FLDR}/dummy.py 
    sleep 2s

done
