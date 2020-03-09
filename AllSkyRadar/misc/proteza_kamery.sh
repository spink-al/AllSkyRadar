#!/bin/bash

# read conf, will it work via cron? :/

if [ -f /home/pi/flight_warning/flight_warning_Conf.py ] ; then
    . /home/pi/flight_warning/flight_warning_Conf.py
else
    near_airport_code="EPPO"
fi

curl -s http://awiacja.imgw.pl/rss/metar00.php?airport=${near_airport_code} | grep "METAR ${near_airport_code}" > /tmp/metar.txt
cat /tmp/metar.txt >> /tmp/metars.txt

noc=$1

if [ $noc == "1" ]; then
    if `cat /tmp/metar.txt | grep CAVOK` ; then
        echo "noc cavok"
        cp /home/pi/AllSkyRada/nite_cavok_1080p.jpg /tmp/AllSkyRadar/zwo_1080p.jpg
    else
        echo "noc beton"
        cp /home/pi/AllSkyRada/nite_beton_1080p.jpg /tmp/AllSkyRadar/zwo_1080p.jpg
    fi
else
    if `cat /tmp/metar.txt | grep CAVOK` ; then
        echo "dzien cavok"
        cp /home/pi/AllSkyRada/day_cavok_1080p.jpg /tmp/AllSkyRadar/zwo_1080p.jpg
    else
        echo "dzien beton"
        cp /home/pi/AllSkyRada/day_beton_1080p.jpg /tmp/AllSkyRadar/zwo_1080p.jpg
    fi
fi
