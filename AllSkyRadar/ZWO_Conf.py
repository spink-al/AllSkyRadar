# Do not use spaces between var name and "=" or after it,
# *conf.py files are used also by bash scripts, and this will creep them out!

# Need reset lvl 1
# size of jpg's with overlay
w_resize="1080"
h_resize="1080"

# resized jpg quality
q_resize="85"
q_fullsize="95"

# Where the camera is pointing
#cam_azimuth="261"
# theta azimuth correction  (rotation of plot)
# but something strange happens when less then -8.0
theta_corr="-7.0"
# horizon calibration layer (plot borders down/up/left/right vs image)
#top_

delay_between_captures="10"
# Crop fullsize (camera.resolution) 3104x2304 to 3104x1746 starting at x=0, y=0
crop_x="678"
crop_y="57"
crop_w="2010"
crop_h="2010"

# plot enabled/disabled
overlay="1"
# plot frame:
spines_ovrl="1"
# aside from sun/moon/planets: 
stars_ovrl="0"
star_names="0" # todoz
iss_ovrl="1"

#plot landmarks
landmarks_ovrl="1"

# trails disabled in rPiCamera.py atm
plot_trails="1"

# time costly but eyecandy plane trails:
alhablend_trails="0" #todo

# Hardware flips need script reset lvl2
# both flips at once via h_flip atm
h_flip="1"
v_flip="1"

# White Balance d_=day n_=night 
# not used for ZWO atm
d_wb1="1.7"
d_wb2="1.4"
n_wb1="1.2"
n_wb2="2.0"

plot_adj_l="-0.01"
plot_adj_b="0.01"
plot_adj_r="1.03"
plot_adj_t="1.0"

