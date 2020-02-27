#!/bin/bash
# Read config
. ./ASR_Conf.py

#sleep 15s
while true ; do
    cd ${BIN_FLDR}
    #data="20200210"
    data=`date +%Y%m%d`
    ASI=ASI
    mkdir -p ${TMP_FLDR}/WSC
    mkdir -p ${TMP_FLDR}/WSC.tmp

    echo ${data} > ${TMP_FLDR}/tmpconf0

    cd ${TMP_FLDR}
    /usr/bin/ssh pi@${STORAGE_IP} 'mkdir -p /home/pi/work/arch/AS/_ASI/'${ASI}'/'${data}
    /usr/bin/ssh pi@${STORAGE_IP} 'ln -sfn /home/pi/work/arch/AS/_ASI/'${ASI}'/'${data}' /home/pi/work/arch/AS/_ASI/_'${ASI}
    while true  ; do
        if [ -f /tmp/AllSkyRadar/restart1 ] ; then 
	    rm /tmp/AllSkyRadar/restart1
	    /usr/bin/ssh pi@${STORAGE_IP} 'touch /home/pi/work/arch/AS/_ASI/'${ASI}'/'${data}'/exit'
	    break 
	fi 
	ile=`ls -1 ${ASI}/ | grep "jpg" | grep -v '~' | wc -l`
	if [ $ile -ge 1 ] ; then 
	    sleep 2s
	    for i in `ls -1 ${ASI}/ | grep "jpg"| grep -v '~' ` ; do 
		/usr/bin/scp ${ASI}/$i pi@${STORAGE_IP}:/home/pi/work/arch/AS/_ASI/${ASI}/${data}/ 
		if [ $? -eq 0 ] ; then
		    rm ${ASI}/$i
		fi
	    done
	fi 
	sleep 3s
    done
    echo "restart"
done

