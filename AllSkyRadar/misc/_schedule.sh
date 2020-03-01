#!/bin/bash

# Change lat/lon
my_lat="51.1234N"
my_lon="15.1234E"

# Check paths! todo

##############################################################################################
# !!! offset [MM|HH:MM] Time interval (+ve towards noon) to adjust twilight calculation. !!! #
##############################################################################################

cp /tmp/tmpconf* /home/pi/AllSkyRadar/config/
sleep 1s

echo echo 'echo "5" > /tmp/AllSkyRadar/tmpconf3'     | at $(sunwait list naut up    offset 0 ${my_lat} ${my_lon})
echo echo 'echo "40" > /tmp/AllSkyRadar/tmpconf2'    | at $(sunwait list naut up    offset 0 ${my_lat} ${my_lon})

echo echo 'echo "40" > /tmp/AllSkyRadar/tmpconf3'    | at $(sunwait list sun up     offset +20 ${my_lat} ${my_lon})
echo echo 'echo "70" > /tmp/AllSkyRadar/tmpconf2'    | at $(sunwait list sun up     offset +20 ${my_lat} ${my_lon})

echo 'echo "50" > /tmp/AllSkyRadar/tmpconf3'         | at $(sunwait list sun down   offset +20 ${my_lat} ${my_lon})
echo 'echo "110" > /tmp/AllSkyRadar/tmpconf2'        | at $(sunwait list civil down offset 0 ${my_lat} ${my_lon})

echo 'echo "90" > /tmp/AllSkyRadar/tmpconf3'         | at $(sunwait list naut down  offset +20 ${my_lat} ${my_lon})
echo 'echo "110" > /tmp/AllSkyRadar/tmpconf2'        | at $(sunwait list naut down  offset +20 ${my_lat} ${my_lon})

echo 'echo "5" > /tmp/AllSkyRadar/tmpconf3A'         | at $(sunwait list naut up    offset 0 ${my_lat} ${my_lon})
echo 'echo "70" > /tmp/AllSkyRadar/tmpconf2A'        | at $(sunwait list naut up    offset 0 ${my_lat} ${my_lon})

echo 'echo "90" > /tmp/AllSkyRadar/tmpconf3A'        | at $(sunwait list sun up     offset +20 ${my_lat} ${my_lon})
echo 'echo "130" > /tmp/AllSkyRadar/tmpconf2A'       | at $(sunwait list sun up     offset +20 ${my_lat} ${my_lon})

echo 'echo "75" > /tmp/AllSkyRadar/tmpconf3A'        | at $(sunwait list sun down   offset +20  ${my_lat} ${my_lon})
echo 'echo "105" > /tmp/AllSkyRadar/tmpconf2A'       | at $(sunwait list sun down   offset +20  ${my_lat} ${my_lon})

echo 'echo "65" > /tmp/AllSkyRadar/tmpconf3A'        | at $(sunwait list civil down offset 0 ${my_lat} ${my_lon})
echo 'echo "180" > /tmp/AllSkyRadar/tmpconf2A'       | at $(sunwait list civil down offset 0 ${my_lat} ${my_lon})

echo 'echo "85" > /tmp/AllSkyRadar/tmpconf3A'        | at $(sunwait list naut down  offset +20 ${my_lat} ${my_lon})
echo 'echo "125" > /tmp/AllSkyRadar/tmpconf2A'       | at $(sunwait list naut down  offset +20 ${my_lat} ${my_lon})

echo 'echo "1" > /tmp/AllSkyRadar/tmpconfA2'         | at $(sunwait list naut up    offset 0  ${my_lat} ${my_lon})
echo 'echo "0" > /tmp/AllSkyRadar/tmpconfA3'         | at $(sunwait list naut up    offset 0  ${my_lat} ${my_lon})
echo 'echo "1" > /tmp/AllSkyRadar/tmpconf9'          | at $(sunwait list naut up    offset +1 ${my_lat} ${my_lon})

echo 'echo "0" > /tmp/AllSkyRadar/tmpconfA2'         | at $(sunwait list naut down  offset -10 ${my_lat} ${my_lon})
echo 'echo "1" > /tmp/AllSkyRadar/tmpconfA3'         | at $(sunwait list naut down  offset -10 ${my_lat} ${my_lon})
echo 'echo "1" > /tmp/AllSkyRadar/tmpconf9'          | at $(sunwait list naut down  offset -11 ${my_lat} ${my_lon})

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'        | at $(sunwait list naut up    offset 0 ${my_lat} ${my_lon})
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'        | at $(sunwait list naut up    offset +5 ${my_lat} ${my_lon})

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'        | at $(sunwait list sun up     offset +60 ${my_lat} ${my_lon})
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'        | at $(sunwait list sun up     offset +65 ${my_lat} ${my_lon})

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'        | at $(sunwait list sun down   offset +65 ${my_lat} ${my_lon})
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'        | at $(sunwait list sun down   offset +60 ${my_lat} ${my_lon})

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'        | at $(sunwait list naut down  offset -5 ${my_lat} ${my_lon})
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'        | at $(sunwait list naut down  offset 0 ${my_lat} ${my_lon})

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'        | at 12:00
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'        | at 12:05

touch /tmp/AllSkyRadar/restart1
#touch /tmp/AllSkyRadar/restart2 # inactive asr direct into mp4 without sending to storage
touch /tmp/AllSkyRadar/restart3

wget -qr https://www.celestrak.com/NORAD/elements/stations.txt -O /tmp/AllSkyRadar/stations.txt
grep "ISS (ZARYA)" /tmp/AllSkyRadar/stations.txt -A 2 > /tmp/AllSkyRadar/iss.tle # here ?
grep "ISS (ZARYA)" /tmp/AllSkyRadar/stations.txt -A 2 > /tmp/iss.tle # or here?

##############################################################################################
########################################## END  ##############################################
##############################################################################################

