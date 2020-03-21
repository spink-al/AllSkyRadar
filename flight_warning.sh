#!/bin/bash
near_airport_code="EPPO"
while true ; do 
    mkdir /tmp/AllSkyRadar
    echo "" > /tmp/AllSkyRadar/highlight
    sudo chown -R www-data:www-data /tmp/AllSkyRadar/highlight
    
    curl -s http://awiacja.imgw.pl/rss/metar00.php?airport=${near_airport_code} | grep "METAR ${near_airport_code}" > /tmp/metar.txt
    cat /tmp/metar.txt >> /tmp/metars.txt

    sudo rm /tmp/fw_restart
    nc -w 5 192.168.3.113 33333 | python3 flights_to_html.py
    #nc -w 30 localhost 33333 | python flights_to_html.py
    sleep 5s 
done


