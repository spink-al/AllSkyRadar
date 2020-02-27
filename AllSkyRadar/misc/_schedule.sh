#!/bin/bash

cp /tmp/tmpconf* /home/pi/AllSkyRadar/config/

sleep 1s
echo 'echo "5" > /tmp/AllSkyRadar/tmpconf3'     | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)
echo 'echo "40" > /tmp/AllSkyRadar/tmpconf2'    | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)

echo 'echo "40" > /tmp/AllSkyRadar/tmpconf3'    | at $(date --date="+`/usr/local/bin/sunwait -v sun up +20` min" +%H:%M)
echo 'echo "70" > /tmp/AllSkyRadar/tmpconf2'    | at $(date --date="+`/usr/local/bin/sunwait -v sun up +20` min" +%H:%M)


echo 'echo "50" > /tmp/AllSkyRadar/tmpconf3'    | at $(date --date="+`/usr/local/bin/sunwait -v sun down -20` min" +%H:%M)
echo 'echo "110" > /tmp/AllSkyRadar/tmpconf2'   | at $(date --date="+`/usr/local/bin/sunwait -v civ down` min" +%H:%M)

echo 'echo "90" > /tmp/AllSkyRadar/tmpconf3'    | at $(date --date="+`/usr/local/bin/sunwait -v naut down -20` min" +%H:%M)
echo 'echo "110" > /tmp/AllSkyRadar/tmpconf2'   | at $(date --date="+`/usr/local/bin/sunwait -v naut down -20` min" +%H:%M)


echo 'echo "5" > /tmp/AllSkyRadar/tmpconf3A'    | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)
echo 'echo "70" > /tmp/AllSkyRadar/tmpconf2A'   | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)

echo 'echo "90" > /tmp/AllSkyRadar/tmpconf3A'   | at $(date --date="+`/usr/local/bin/sunwait -v sun up +20` min" +%H:%M)
echo 'echo "130" > /tmp/AllSkyRadar/tmpconf2A'  | at $(date --date="+`/usr/local/bin/sunwait -v sun up +20` min" +%H:%M)

echo 'echo "75" > /tmp/AllSkyRadar/tmpconf3A'   | at $(date --date="+`/usr/local/bin/sunwait -v sun down -20` min" +%H:%M)
echo 'echo "105" > /tmp/AllSkyRadar/tmpconf2A'  | at $(date --date="+`/usr/local/bin/sunwait -v sun down -20` min" +%H:%M)

echo 'echo "65" > /tmp/AllSkyRadar/tmpconf3A'   | at $(date --date="+`/usr/local/bin/sunwait -v civ down` min" +%H:%M)
echo 'echo "180" > /tmp/AllSkyRadar/tmpconf2A'  | at $(date --date="+`/usr/local/bin/sunwait -v civ down` min" +%H:%M)

echo 'echo "85" > /tmp/AllSkyRadar/tmpconf3A'   | at $(date --date="+`/usr/local/bin/sunwait -v naut down -20` min" +%H:%M)
echo 'echo "125" > /tmp/AllSkyRadar/tmpconf2A'  | at $(date --date="+`/usr/local/bin/sunwait -v naut down -20` min" +%H:%M)


echo 'echo "1" > /tmp/AllSkyRadar/tmpconfA2'    | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)
echo 'echo "0" > /tmp/AllSkyRadar/tmpconfA3'    | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)
echo 'echo "1" > /tmp/AllSkyRadar/tmpconf9'     | at $(date --date="+`/usr/local/bin/sunwait -v naut up +1` min" +%H:%M)


echo 'echo "0" > /tmp/AllSkyRadar/tmpconfA2'    | at $(date --date="+`/usr/local/bin/sunwait -v naut down +10` min" +%H:%M)
echo 'echo "1" > /tmp/AllSkyRadar/tmpconfA3'    | at $(date --date="+`/usr/local/bin/sunwait -v naut down +10` min" +%H:%M)
echo 'echo "1" > /tmp/AllSkyRadar/tmpconf9'     | at $(date --date="+`/usr/local/bin/sunwait -v naut down +11` min" +%H:%M)

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v naut up` min" +%H:%M)
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v naut up +5` min" +%H:%M)

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v sun up +60` min" +%H:%M)
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v sun up +65` min" +%H:%M)

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v sun down -65` min" +%H:%M)
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v sun down -60` min" +%H:%M)

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v naut down -5` min" +%H:%M)
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'   | at $(date --date="+`/usr/local/bin/sunwait -v naut down` min" +%H:%M)

echo 'touch /tmp/AllSkyRadar/WSC.tmp/restart'   | at 12:00
echo 'touch /tmp/AllSkyRadar/ASR.tmp/restart'   | at 12:05

touch /tmp/AllSkyRadar/restart1
#touch /tmp/AllSkyRadar/restart2 # inactive asr direct into mp4 without sending to storage
touch /tmp/AllSkyRadar/restart3

wget -qr https://www.celestrak.com/NORAD/elements/stations.txt -O /tmp/AllSkyRadar/stations.txt
grep "ISS (ZARYA)" /tmp/AllSkyRadar/stations.txt -A 2 > /tmp/AllSkyRadar/iss.tle # here ?
grep "ISS (ZARYA)" /tmp/AllSkyRadar/stations.txt -A 2 > /tmp/iss.tle # or here?
