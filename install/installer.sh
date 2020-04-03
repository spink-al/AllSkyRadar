#!/bin/bash

sudo mkdir /etc/raspap
sudo mkdir /var/www/html/html_wzzak_bak



sudo cp -R etc/* /etc/raspap
sudo cp -R html /var/www
sudo cp -R html_wzzak_bak/* /var/www/html/html_wzzak_bak

sudo chown -R www-data:www-data /etc/raspap/
sudo chown -R www-data:www-data /var/www/html/

sudo apt update
#sudo pip3 install opencv-python==3.4.6.27
#sudo pip3 install opencv-contrib-python==3.4.6.27
#sudo apt install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test
sudo pip3 install matplotlib
sudo pip3 install Pillow
sudo pip3 install ephem
#sudo pip3 install zwoasi
#sudo pip3 install scipy
#sudo apt install tmux
#sudo apt install screen
sudo apt install -y netcat


sudo apt install -y lighttpd php-cgi
sudo lighty-enable-mod fastcgi-php
sudo systemctl force-reload lighttpd.service
sudo systemctl restart lighttpd.service


sudo ln -sf /tmp/AllSkyRadar/dummy_1080p.jpg /var/www/html/dummy_1080p.jpg
sudo ln -sf /tmp/AllSkyRadar/dummy_1080p.jpg /var/www/html/html_wzzak_bak/dummy_1080p.jpg

sudo ln -sf /tmp/out6.html /var/www/html/out6.html
sudo ln -sf /tmp/out6.html /var/www/html/html_wzzak_bak/out6.html

sudo ln -sf /tmp/out7.html /var/www/html/out7.html
sudo ln -sf /tmp/out7.html /var/www/html/html_wzzak_bak/out7.html

