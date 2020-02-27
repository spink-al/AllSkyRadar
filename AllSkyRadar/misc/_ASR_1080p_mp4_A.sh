#!/bin/bash
# Read config 
. /home/pi/AllSkyRadar/ASR_Conf.py

i=0
DATEIN=`date +%Y%m%d_%H%M%S`
cd ${TMP_FLDR}/ASR.tmp/

inotifywait -m -e close_write -q --format '%f' ${TMP_FLDR}/ASR.tmp/ | \
while read f ; do 
    if [ ${f} == "exit" ] ; then
        if [ ${i} -gt 5 ] ; then
	    rm ${TMP_FLDR}/ASR.tmp/exit
    	    exit
    	fi
    elif [ ${f} == "restart" ] ; then
        if [ ${i} -gt 5 ] ; then
    	    echo "bash "${MISC_FLDR}"/_ASR_720p_mp4_A.sh" | at -M now
	    rm ${TMP_FLDR}/ASR.tmp/
    	    exit
    	fi
    fi
    
    rm $last_f 
    if echo ${f} | grep "jpg" > /dev/null ; then
        cat ${f}
    fi
    last_f=$f
    i=$[i+1]
done | ffmpeg -y -f image2pipe -framerate 15 -i - -c:v libx264 -r 15 ${TMP_FLDR}/ASR_${DATEIN}.mp4
DATEOUT=`date +%Y%m%d_%H%M%S`
mv ${TMP_FLDR}/ASR_${DATEIN}.mp4 ${TMP_FLDR}/ASR_${DATEIN}-${DATEOUT}.mp4
/usr/bin/scp ${TMP_FLDR}/ASR_${DATEIN}-${DATEOUT}.mp4 pi@${STORAGE_IP}:${STORAGE_FLDR}/ASR/
if [ $? -eq 0 ] ; then
    rm ${TMP_FLDR}/ASR_${DATEIN}-${DATEOUT}.mp4
fi
