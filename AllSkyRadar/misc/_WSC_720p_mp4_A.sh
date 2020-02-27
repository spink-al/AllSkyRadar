#!/bin/bash
# Read config 
. /home/pi/AllSkyRadar/ASR_Conf.py

i=0
DATEIN=`date +%Y%m%d_%H%M%S`
cd ${TMP_FLDR}/WSC.tmp/

inotifywait -m -e close_write -q --format '%f' ${TMP_FLDR}/WSC.tmp/ | \
while read f ; do 
    if [ ${f} == "exit" ] ; then
        if [ ${i} -gt 5 ] ; then
	    rm ${TMP_FLDR}/WSC.tmp/exit
    	    exit
    	fi
    elif [ ${f} == "restart" ] ; then
        if [ ${i} -gt 5 ] ; then
    	    echo "bash "${MISC_FLDR}"/_WSC_720p_mp4_A.sh" | at -M now
	    rm ${TMP_FLDR}/WSC.tmp/
    	    exit
    	fi
    fi
    
    rm $last_f 
    if echo ${f} | grep "jpg" > /dev/null ; then
        cat ${f}
    fi
    last_f=$f
    i=$[i+1]
done | ffmpeg -y -f image2pipe -framerate 60 -i - -c:v libx264 -r 60 ${TMP_FLDR}/WSC_${DATEIN}.mp4
DATEOUT=`date +%Y%m%d_%H%M%S`
mv ${TMP_FLDR}/WSC_${DATEIN}.mp4 ${TMP_FLDR}/WSC_${DATEIN}-${DATEOUT}.mp4
/usr/bin/scp ${TMP_FLDR}/WSC_${DATEIN}-${DATEOUT}.mp4 pi@${STORAGE_IP}:${STORAGE_FLDR}/WSC/
if [ $? -eq 0 ] ; then
    rm ${TMP_FLDR}/WSC_${DATEIN}-${DATEOUT}.mp4
fi
