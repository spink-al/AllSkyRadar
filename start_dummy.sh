#!/bin/bash
# Read config
. ./ASR_Conf.py
mkdir -p /tmp/AllSkyRadar/

wget -qr https://www.celestrak.com/NORAD/elements/stations.txt -O /tmp/AllSkyRadar/stations.txt
grep "ISS (ZARYA)" /tmp/AllSkyRadar/stations.txt -A 2 > /tmp/AllSkyRadar/iss.tle

sudo ln -sf /tmp/AllSkyRadar/dummy_1080p.jpg /var/www/html/dummy_1080p.jpg
sudo ln -sf /tmp/AllSkyRadar/dummy_1080p.jpg /var/www/html/html_wzzak_bak/dummy_1080p.jpg

#sudo cp www/dummy.html /var/www/html/
while true ; do
    sudo rm /tmp/dummy_restart
    echo "START: "`date`
    python3 ${BIN_FLDR}/dummy.py
    sleep 2s

done
