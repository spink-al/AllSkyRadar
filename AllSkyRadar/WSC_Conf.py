# Do not use spaces between var name and "=" or after "=",
# *conf.py files are used also by bash scripts, and this will creep them out!

# Need reset lvl 1
# size of jpg's with overlay
w_resize="1920"
h_resize="1080"

# resized jpg quality
q_resize="85"
q_fullsize="85"

# Where the camera is pointing
cam_azimuth="261"
delay_between_captures="5"
# Crop fullsize (camera.resolution) 3104x2304 to 3104x1746 starting at x=0, y=0
crop_x="0"
crop_y="0"
crop_w="3104"
crop_h="1746"

# plot enabled/disabled
overlay="1"
# plot frame:
spines_ovrl="1"
# aside from sun/moon/planets: 
stars_ovrl="0"
iss_ovrl="1"

# horizon calibration layer
calibration1_ovrl="1"
# distortion grid, etc. Use 10s instead of 5s delay_between_captures, it is time consuming
calibration2_ovrl="0"

# still inactive, todo
calibration3_ovrl="1" #todo
calibration4_ovrl="1" #todo?

#plot landmarks
landmarks_ovrl="1"

# trails disabled in rPiCamera.py atm
plot_trails="0" # todo

# time costly but eyecandy plane trails:
alhablend_trails="1" #todo


# Hardware flips need script reset lvl2
h_flip="1"
v_flip="1"

# White Balance d_=day n_=night
d_wb1="1.7"
d_wb2="1.4"
n_wb1="1.2"
n_wb2="2.0"
