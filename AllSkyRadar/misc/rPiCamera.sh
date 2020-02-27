#!/bin/bash
# Read config
. ./ASR_Conf.py

cd ${BIN_FLDR}
mkdir -p ${TMP_FLDR}/WSC
mkdir -p ${TMP_FLDR}/WSC.tmp
sleep 1s
if ! [ -f ${TMP_FLDR}/tmpconfA ]  ; then cp ${CONF_FLDR}/tmpconfA ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf1A ] ; then cp ${CONF_FLDR}/tmpconf1A ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf2A ] ; then cp ${CONF_FLDR}/tmpconf2A ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf3A ] ; then cp ${CONF_FLDR}/tmpconf3A ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf9 ]  ; then cp ${CONF_FLDR}/tmpconf9 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf9X ] ; then cp ${CONF_FLDR}/tmpconf9X ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA2 ] ; then cp ${CONF_FLDR}/tmpconfA2 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA3 ] ; then cp ${CONF_FLDR}/tmpconfA3 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA4 ] ; then cp ${CONF_FLDR}/tmpconfA4 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA5 ] ; then cp ${CONF_FLDR}/tmpconfA5 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA6 ] ; then cp ${CONF_FLDR}/tmpconfA6 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA7 ] ; then cp ${CONF_FLDR}/tmpconfA7 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconfA8 ] ; then cp ${CONF_FLDR}/tmpconfA8 ${TMP_FLDR} ; fi

while true ; do 
    echo "START: "`date` 
    if [ -f ${TMP_FLDR}/WSC/exit ] ; then 
	rm ${TMP_FLDR}/WSC/exit
	exit
    fi
    sleep 2s
    python3 ${BIN_FLDR}/rPiCamera.py 
done
