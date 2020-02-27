#!/bin/bash
# Read config
. /home/pi/AllSkyRadar/ASR_Conf.py

cd ${BIN_FLDR}

tmux -L myapp -f /home/pi/AllSkyRadar/other/.tmux.conf new-session -s AllSkyRadar \; \
split-window -v -p 70 \; \
select-pane -t 0 \; \
split-window -h -p 50 \; \
select-pane -t 0 \; \
send-keys '/bin/bash '${MISC_FLDR}'/copy_loop_wsc.sh' C-m  \; \
split-window -v -p 50 \; \
send-keys '/bin/bash '${BIN_FLDR}'/start_wsc_cam.sh' C-m  \; \
select-pane -t 3 \; \
send-keys '/bin/bash '${MISC_FLDR}'/run_screen.sh' C-m  \; \
select-pane -t 2 \; \
send-keys '/bin/bash '${MISC_FLDR}'/vrs.sh' C-m  \; \
select-pane -t 2 \; \
split-window -v -p 50 \; \
send-keys 'cd '${BIN_FLDR} C-m  \; \
select-pane -t 4 \; \
split-window -v -p 30 \; \
send-keys 'htop' C-m  \; 
select-pane -t 3 \; \

