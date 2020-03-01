# AllSkyRadar



# Requirements 
rPi4 Raspbian Buster Linux rPi4 4.19.97-v7l+ #1294 (2020-02-05 or 2020-02-13?) 

https://github.com/spink-al/picamera

https://github.com/spink-al/zwo-skycam

for use of misc/_schedule.sh you need sunwait and a line in crontab:

6 0 * * * /bin/bash /home/pi/AllSkyRadar/misc/_schedule.sh

https://github.com/risacher/sunwait

sudo pip3 install opencv-python==3.4.6.27

sudo pip3 install opencv-contrib-python==3.4.6.27

sudo apt install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

sudo pip3 install matplotlib

sudo pip3 install Pillow

sudo pip3 install ephem

sudo pip3 install zwoasi

sudo pip3 install scipy

sudo apt install tmux

sudo apt install screen
