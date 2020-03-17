#!/bin/bash
while true ; do 
    sudo rm /tmp/fw_restart
    nc -w 5 192.168.3.113 33333 | python3 flights_to_html.py
    #nc -w 30 localhost 33333 | python flights_to_html.py
    sleep 5s 
done


