#!/bin/bash
. ./ASR_Conf.py

cd ${BIN_FLDR}
mkdir -p ${TMP_FLDR}/ASI
mkdir -p ${TMP_FLDR}/ASI.tmp
mkdir -p ${TMP_FLDR}/ASR.tmp

sleep 1s
if ! [ -f ${TMP_FLDR}/tmpconf   ] ; then cp ${CONF_FLDR}/tmpconf ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf1  ] ; then cp ${CONF_FLDR}/tmpconf1 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf2  ] ; then cp ${CONF_FLDR}/tmpconf2 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf3  ] ; then cp ${CONF_FLDR}/tmpconf3 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf9B ] ; then cp ${CONF_FLDR}/tmpconf9B ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf4  ] ; then cp ${CONF_FLDR}/tmpconf4 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf7  ] ; then cp ${CONF_FLDR}/tmpconf7 ${TMP_FLDR} ; fi
if ! [ -f ${TMP_FLDR}/tmpconf8  ] ; then cp ${CONF_FLDR}/tmpconf8 ${TMP_FLDR} ; fi


sleep 1s
while true ; do
    if [ -f ${TMP_FLDR}ASI/exit ] ; then
        rm ${TMP_FLDR}/ASI/exit
        exit
    fi

    echo "START XX"
    python3 ${BIN_FLDR}/zwoCamera.py
    sleep 1s
done
