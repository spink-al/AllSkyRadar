import time
import picamera
from time import sleep
#from fractions import Fraction
import datetime
import shutil
import numpy as np
import cv2
import io
#import picamera.array
import threading
from PIL import Image, ImageStat, ImageFont, ImageDraw,ImageColor
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import math
import ephem
import os
import ASR_Conf


my_lat = ASR_Conf.MY_LAT
my_lon = ASR_Conf.MY_LON
my_alt = ASR_Conf.MY_ALT

print("START 0: "+str(datetime.datetime.now()))

gatech = ephem.Observer()
gatech.lat = float(my_lat)
gatech.lon = float(my_lon)
gatech.elevation = int(my_alt)

issline=[]

tlefile=open(tleFileName, 'r')
tledata=tlefile.readlines()
tlefile.close()

for i, line in enumerate(tledata):
    if "ISS" in line: 
        for l in tledata[i:i+3]: issline.append(l.strip('\r\n').rstrip()),

#print(tledata)
deg = u'\xb0'
uus = u'\xb5s'
jups = u"\u2643"
mars = u"\u2642"
vens = u"\u2640"
sats = u"\u2644"
sols = u"\u2609"
luns = u"\u263d"

# Exposure
DataFileName0 = tmpfld+"/tmpconfA"
# Analog Gain
DataFileName1 = tmpfld+"/tmpconf1A"
# Max brightness
DataFileName2 = tmpfld+"/tmpconf2A"
# Min brightness
DataFileName3 = tmpfld+"/tmpconf3A"
# Reread exp/gains
DataFileName9 = tmpfld+"/tmpconf9"
# Exit script
DataFileName9X = tmpfld+"/tmpconf9X"
# Switch day/night WB
DataFileNameA2 = tmpfld+"/tmpconfA2"
# Switch BW/Color
DataFileNameA3 = tmpfld+"/tmpconfA3"
# Read 1WB setings *inactive because of DataFileNameA2 atm
DataFileNameA4 = tmpfld+"/tmpconfA4"
# Read 2WB setings *inactive because of DataFileNameA2 atm
DataFileNameA5 = tmpfld+"/tmpconfA5"
# Lens shading options for tests *maskaAntyFiol is a working solution atm
DataFileNameA6 = tmpfld+"/tmpconfA6"
# anti lens shading mask
DataFileNameA7 = "/tmp/tmpconfA7"
DataFileNameA8 = "/tmp/tmpconfA8"

center_lim = 0 # wrong place for this var
lewy_lim = 61 # wrong place for this var
prawy_lim = 61 # wrong place for this var
in_center = 0 # wrong place for this var

datafileA7=open(DataFileNameA7, 'r')
datazA7=datafileA7.readlines()
datafileA7.close()

datafileA8=open(DataFileNameA8, 'r')
datazA8=datafileA8.readlines()
datafileA8.close()

maska_str = str(datazA8[0])
print(miscfld+"/"+str(maska_str))
maskaAntyFiol0 = cv2.imread(miscfld+"/"+str(maska_str)) 
maskaAntyFiol0 = maskaAntyFiol0.astype(np.single)
op = float(datazA7[0])

def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def is_int_try(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def rotate_around_point_highperf(in_center, x,y, radians, origin=(0, 0)):
    #global in_center
    #global prawy_lim
    #global lewy_lim

    #x, y = x,y
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy

def distorsXY1(in_center,x,y):
     # needs to be removed probably
    """
    xdoa1 = []
    ydob1 = []
    ###########################################################
    if((x < float(in_center)-30) or (x > float(in_center)+30)) or y > 30:        
        # if y > 20:        
        x1,y1 = distorsXY2(x,y)
        y1 = y1
        x1 = x1 #round((k),1),round((j),1)
    else:
        if (inner_lock == 0):
            x1,y1 = distorsXY2(x,y)
            y1 = y1
            x1 = x        
        else:
            x1,y1 = distorsXY2(x,y)
            y1 = y1
            x1 = x1

    ###########################################################
    if (x1 > 0):
        # x1,y1 = f0a(x1, y1,midX)
        if upit == 1:
            x1,y1 = f0a(x1, y1)
        else:
            x1,y1 = x1, y1
    elif (x1 < -0):
        # xa,ya = f0a(x1, y1,midX)
        if upit == 1:
            x1,y1 = f0a(x1, y1)
        else:
            x1,y1 = x1, y1
    else:
        x1,y1 = x1, y1
    ###########################################################
    xdoa1.append(x)
    xdoa1.append(x1)
    # xdoa1.append(srcX)
    ydob1.append(y)
    ydob1.append(y1)	
    ax.plot(xdoa1,ydob1, '--',markersize=10, color='yellow', lw=1,alpha=.2)
    """
    x1,y1 = distorsXY2(in_center,x,y)
    return x1,y1	

def distorsXY1a(x,y):
    # unused
    global in_center
    global prawy_lim
    global lewy_lim
    """
    xdoa1 = []
    ydob1 = []
    ###########################################################
    if((x < float(in_center)-30) or (x > float(in_center)+30)) or y > 30:        
        # if y > 20:        
        x1,y1 = distorsXY2(x,y)
        y1 = y1
        x1 = x1 #round((k),1),round((j),1)
    else:
        if (inner_lock == 0):
            x1,y1 = distorsXY2(x,y)
            y1 = y1# +0.0001
            x1 = x        
        else:
            x1,y1 = distorsXY2(x,y)
            y1 = y1
            x1 = x1

    ###########################################################
    if (x1 > 0):
        # x1,y1 = f0a(x1, y1,midX)
        if upit == 1:
            x1,y1 = f0a(x1, y1)
            # print "A: ",x1, y1
        else:
            x1,y1 = x1, y1
    elif (x1 < -0):
        # xa,ya = f0a(x1, y1,midX)
        if upit == 1:
            x1,y1 = f0a(x1, y1)
            # print "B: ",x1, y1
        else:
            x1,y1 = x1, y1
    else:
        x1,y1 = x1, y1
        # print "C: ",x1, y1        	
    ###########################################################
    xdoa1.append(x)
    xdoa1.append(x1)
    # xdoa1.append(srcX)
    ydob1.append(y)
    ydob1.append(y1)	
    ax.plot(xdoa1,ydob1, '-',markersize=10, color='red', lw=1,alpha=0.3)
    """
    x1,y1 = distorsXY2(in_center,x,y)
    return x1,y1


def distorsXY2(in_center,x,y):
    #global in_center
    #global prawy_lim
    #global lewy_lim
    initX 	=	lewy_lim # should be passed like in_center?!
    initY 	= 	20 
    finalX 	= 	prawy_lim # should be passed like in_center?!
    finalY 	= 	0 

    midX 	= 	float(finalX - initX) /2
    midY 	= 	float(finalY - initY) /2
    midX 	= 	midX + initX
    midY 	= 	midY + initY
    midY 	= 	0 ## !!!
    
    # distorsion arguments trial and error
    k3 		= 	-0.000015
    Sy 		= 	-0.08
    Sx 		= 	0.03
    #pD1 	= 	1.
    #pD2 	= 	10
    W1 		= 	0.00004
    W2  	=	-0.0001
    
    # corrections for unleveled axis of rotation
    # T1 = angle for which data should be rotated around virtual center of image 
    if (45 < int(in_center) <= 90):
        T1              =       -1.25
        V1              =       0.0006
    elif (90 < int(in_center) <= 135):
        T1              =       -2.5
        V1              =       0.0007
    elif (135 < int(in_center) <= 160):
        T1              =       0.25
        V1              =       0.0006
    elif (160 < int(in_center) <= 200):
        T1              =       -0.0 # 1.5 # 20190206
        V1              =       0.0006
    elif (200 < int(in_center) <= 225):
        T1              =       0.25 ## z 1.5 20190206
        V1              =       0.0006
    elif (225 < int(in_center) <= 270):
        T1              =       0.5
        V1              =       0.0006
    elif (270 < int(in_center) <= 315):
        T1              =       -0.5
        V1              =       0.0008
    elif (315 < int(in_center) <= 360):
        T1              =       -1.0
        V1              =       0.0006
    elif (0 <= int(in_center) <= 45):
        T1              =       -0.0
        V1              =       0.0008
    else:
        T1              =       0.0
        V1              =       0.0009
    #print(int(in_center), T1)
    #V1 = 0.0008 ########## <<<<<<<<<<<-------------- V1 V1 V1
    
            
    nX = x - midX
    nY = y - midY
    
    Y_2 = nY**2
    X_2 = nX**2
    
    # some crazy math: 
    # https://www.youtube.com/watch?v=PPAlDNlb2lw  
    # https://www.youtube.com/watch?v=ppATGESg-Bw  
    rSrcY =  k3*nY*((X_2) + (Y_2)) + Sy*nY + ((X_2)*(V1)) + ((X_2)*(W1/(1/(nY+0.0001))))
    rSrcX =  k3*nX*((X_2) + (Y_2)) + Sx*nX +		    ((Y_2)*(W2/(1/(nX+0.0001))))

    srcY = (midY + (rSrcY + nY)) 
    srcX = (midX + (rSrcX + nX)) 
    radians_r = math.radians(T1)#75)
    srcX, srcY = rotate_around_point_highperf(in_center, srcX, srcY, radians_r, origin=(midX, midY))

    return srcX, srcY


def read_status():
    datafile0=open(DataFileName9, 'r')
    dataz0=datafile0.readlines()
    datafile0.close()
    return dataz0[0]

def read_status9X():
    datafile9X=open(DataFileName9X, 'r')
    dataz0=datafile9X.readlines()
    datafile9X.close()
    return dataz0[0]

def read_status1a():
    datafile1=open(DataFileName1, 'r')
    dataz1=datafile1.readlines()
    datafile1.close()
    return str(dataz1[0])


stream = io.BytesIO()

aktual_t = datetime.datetime.now()
aktual_t_f = aktual_t.strftime("%Y%m%d_%H%M%S")
aktual_t1 = aktual_t

def testBrightness(im):
    # crop brightness
    #q0Ax = 0 ; q0Ay = 0
    #img0A = im.crop((q0Ax, q0Ay, q0Ax+3104, q0Ay+1440))
    
    # or Full Pic Brightness
    data0A = im.convert ('L')
    stat0A = ImageStat.Stat(data0A)
    return int(stat0A.rms[0])

def npz_w(npz, arr):
    with open(tmpfld+"/npz"+str(arr)+".txt",'w') as tsttxt:
        tsttxt.write("")
    with open(tmpfld+"/npz"+str(arr)+".txt",'a') as tsttxt:
        for i in npz[arr]:
            data=''
            for j in i:
                data += str(j)+","
            #print(str(j), end = '')
            data += "\n"
            #print(str(data)+"\n")
            tsttxt.write(str(data))

def cap_d():
    # a bit lower resolution than max, because @max likes to hang
    camera = picamera.PiCamera(resolution=(3104, 2304), sensor_mode=3)
    #camera.isp_blocks -= {'gamma'}
    camera.framerate_range=(0.1, 15)
    datafileA6=open(DataFileNameA6, 'r')
    datazA6=datafileA6.readlines()
    datafileA6.close()
    zerocust = int(str(datazA6[0]))
    
    # lens shading, don't touch, using mask atm
    if zerocust == -1:
        pass
    
    elif zerocust == -2:
        lst_shape = camera._lens_shading_table_shape()
        lst = np.zeros(lst_shape, dtype=np.uint8)
        lst[...] = 32 # NB 32 corresponds to unity gain
        camera.lens_shading_table=lst
    
    elif zerocust == -3:
        npzloaded1 = np.loadtxt('ls0.txt', dtype=np.uint8, delimiter=', ')
        npzloaded2 = np.loadtxt('ls1.txt', dtype=np.uint8, delimiter=', ')
        npzloaded3 = np.loadtxt('ls2.txt', dtype=np.uint8, delimiter=', ')
        npzloaded3 = np.loadtxt('ls3.txt', dtype=np.uint8, delimiter=', ')
        npzloadedfull = np.array([npzloaded1, npzloaded2, npzloaded3, npzloaded4])
        camera.lens_shading_table=npzloadedfull
    
    elif zerocust == -4:
        lst_shape = camera._lens_shading_table_shape()
        lst = np.zeros(lst_shape, dtype=np.uint8)
        lst[...] = 32 # NB 32 corresponds to unity gain
        camera.lens_shading_table=lst
        
    elif zerocust == 0:
        npz = np.load("lens_shading_table.npy") 
        npz[1][...] = 32 #npz[1]-1
        npz[2][...] = 32 #npz[1]-1
        #'''
        rr = npz[0] - 20
        rr = np.maximum(rr, 32)
        rr = np.minimum(rr, 40)
        #aa = np.uint8(npz[0]-5)
        #npz[0] = rr
        npz[0][...] = 32
        
        #gg1 = npz[1] -10
        #gg1 = np.maximum(gg1, 32)
        #gg1 = np.minimum(gg1, 40)
        ##aa = np.uint8(npz[0]-5)
        #npz[1] = gg1
        
        #gg2 = npz[2] -10
        #gg2 = np.maximum(gg2, 32)
        #gg2 = np.minimum(gg2, 40)
        ##aa = np.uint8(npz[0]-5)
        #npz[2] = gg2

        bb = npz[3] - 10
        bb = np.maximum(bb, 32)
        bb = np.minimum(bb, 40)
        npz[3] = bb

        camera.lens_shading_table=npz
        for i in range(4):
            npz_w(npz, i)

    elif zerocust >= 0:        
        lst_shape = camera._lens_shading_table_shape()
        lst = np.zeros(lst_shape, dtype=np.uint8)
        lst[...] = zerocust # NB 32 corresponds to unity gain
        #lst[1][...] = 32
        #lst[2][...] = 32
        lst[0][...] = 30
        camera.lens_shading_table=lst
        
    while True:
        # exposure read from file
        datafile0=open(DataFileName0, 'r')
        dataz0=datafile0.readlines()
        datafile0.close()

        # isday read from file
        datafileA2=open(DataFileNameA2, 'r')
        datazA2=datafileA2.readlines()
        datafileA2.close()
        isday = int(str(datazA2[0]))

        # bw/col read from file
        datafileA3=open(DataFileNameA3, 'r')
        datazA3=datafileA3.readlines()
        datafileA3.close()
        
        mono = int(str(datazA3[0]))
        if mono > 0:
            camera.color_effects = (128,128)
        else:
            camera.color_effects = None 
    	    
        exposure1 = int(str(dataz0[0]))
        exposure2 = exposure1/1000000

        # framerate inactive, framerate_range(0.1, 15) is in power
        if (int(exposure1) >= 1000000):
            framerate1 = 1/(exposure1/1000000)
        elif (int(exposure1) >= 33250):
            framerate1 = 1.0
        else:
            framerate1 = 30.0

        camera.hflip=1
        camera.vflip=1

        camera.shutter_speed = exposure1
        datafile1=open(DataFileName1, 'r')
        dataz1=datafile1.readlines()
        datafile1.close()
        
        iso1 = float(str(dataz1[0]))
        #print(iso1)
        #camera.iso = 0 #???????
        camera._set_analog_gain(iso1)
        camera._set_digital_gain(1.0)

        picamera.PiCamera.CAPTURE_TIMEOUT = 160
        camera.exposure_mode = 'off'
        camera.awb_mode = 'off'

        # wb1 read from file        
        datafileA4=open(DataFileNameA4, 'r')
        datazA4=datafileA4.readlines()
        datafileA4.close()

        # wb2 read from file        
        datafileA5=open(DataFileNameA5, 'r')
        datazA5=datafileA5.readlines()
        datafileA5.close()
        
        # inactive, below isday 0/1 overrides
        camera.awb_gains = (float(datazA4[0]), float(datazA5[0]))
        
        #print("a")
        
        if isday > 0:
            camera.awb_gains = (1.7, 1.4)
            print("awb day")
        else:
            camera.awb_gains = (1.2, 2.0)
            print("awb nite")
        #camera.awb_gains = (1.7, 1.7)

        try:
            while True:
                stream.truncate()
                stream.seek(0)

                camera.capture(stream, format='jpeg')
                aktual_t = datetime.datetime.now()
                aktual_t_f = aktual_t.strftime("%Y%m%d_%H%M%S")
                data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                background = AsyncWrite(data, aktual_t_f, exposure1, iso1, str(datazA4[0]), str(datazA5[0]), mono)
                background.start()
                print("S: ", str(datetime.datetime.now()), str(exposure1), str(iso1))
                
                if (exposure2 < 5):
                    diff1 = 5-exposure2
                    print("Diff: "+str(diff1)+"s")                
                    time.sleep(diff1)

                datafile0=open(DataFileName0, 'r')
                dataz0=datafile0.readlines()
                datafile0.close()
                if not (int(dataz0[0]) == exposure1):
                    break

                datafile1=open(DataFileName1, 'r')
                dataz1=datafile1.readlines()
                datafile1.close()
                if not (float(dataz1[0]) == iso1):
                    break

    
                status1 = read_status()
                if int(status1) == 1:
                    with open(DataFileName9,'w') as tsttxt:
                        newdataz = 0
                        tsttxt.write(str(newdataz)+"\n")
                    break


        finally:
            status1 = read_status()
            if int(status1) == 1:
                with open(DataFileName9,'w') as tsttxt:
                    newdataz = 0
                    tsttxt.write(str(newdataz)+"\n")

            status9X = read_status9X()
            if int(status9X) == 1:
                with open(DataFileName9X,'w') as tsttxt:
                    newdataz = 0
                    tsttxt.write(str(newdataz)+"\n")
                camera.framerate = 1
                camera.close()
                print("END  3: "+str(datetime.datetime.now()))
                break



class AsyncWrite(threading.Thread):
    def __init__(self, data, aktual_t_f, exposure, iso, a4, a5, mono):
        threading.Thread.__init__(self)
        self.data = data
        self.iso = iso # analog gain float
        self.mono = int(mono)
        self.a4 = float(a4)
        self.a5 = float(a5)        
        self.exposure = exposure
        self.aktual_t_f = aktual_t_f

    def run(self):
        global mniej
        global wiecej
        global maska_str
        global maskaAntyFiol0
        global op
        
        global center_lim
        global prawy_lim
        global lewy_lim

        datafile2=open(DataFileName2, 'r')
        dataz2=datafile2.readlines()
        datafile2.close()

        datafile2=open(DataFileName2, 'r')
        dataz2=datafile2.readlines()
        datafile2.close()

        datafile3=open(DataFileName3, 'r')
        dataz3=datafile3.readlines()
        datafile3.close()

        aktual_t1 = datetime.datetime.now()
        image = cv2.imdecode(self.data, 1)
        #image = image[:, :, ::-1]
        
        # flip img here with ls tests
        #imagef = cv2.flip(image, -1)
        
        # crop via cv2 to 16:9 upper part of the image from 3104x2308 -> 3104x1746 bigger
        q0Ax = 0 ; q0Ay = 0
        im = image[q0Ax:q0Ax+1746, q0Ay:q0Ay+3104]
        
        
        #ocvi = im.astype(np.single)
        #ocvi1 = (ocvi / 255) * (ocvi + ((2 * maskaAntyFiol) / 255) * (255 - ocvi))
        
        imcv = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        imim = Image.fromarray(imcv)
        
        #imim = Image.fromarray(imcv)
        #a_channel = Image.new('L', (3104, 1746), 255)   # 'L' 8-bit pixels, black and white
        #imim.putalpha(a_channel)

        # crop via PIL
        #im = self.data
        #q0Ax = 0 ; q0Ay = 0
        #imim = im.crop((q0Ax, q0Ay, q0Ax+3104, q0Ay+1746))

        test_br = testBrightness(imim)
        draw = ImageDraw.Draw(imim)
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 24)
        draw.rectangle(((10,1650,950,1735   ))                                          ,(0,0,0,10))

        draw.text((15,1650 ), "WideSky v10.20200221"                                    ,(100,100,100),font=font)
        draw.text((410,1650      ), str(self.exposure/1000000)+"s"                      ,(100,100,100),font=font)
        draw.text((410,1675 ), str(self.exposure)+uus                                   ,(100,100,100),font=font)
        
        draw.text((15,1675 ), str(self.aktual_t_f)                                      ,(100,100,100),font=font)
        draw.text((15,1700 ), "ag: "+str(self.iso)+" dg: "+"1,0*"                       ,(100,100,100),font=font)
        draw.text((410,1700 ), "wb "+str(self.a4)+" "+str(self.a5)                      ,(100,100,100),font=font)

        draw.text((660,1650 ), " Min: "+str(dataz3[0])                                  ,(100,100,100),font=font)
        draw.text((660,1675 ), " Br: "  +str(test_br)                                     ,(100,100,100),font=font)
        draw.text((660,1700 ), " Max: " +str(dataz2[0])                                 ,(100,100,100),font=font)
        
        #imcv2 = cv2.cvtColor(imim, cv2.COLOR_BGRA2BGR)
        #cv2.imwrite(tmpfld+'/img1.jpg', imcv, [int(cv2.IMWRITE_JPEG_QUALITY), 85])

        # resize for on-the-fly h264 compression
        imgHD = imim.resize((1280, 720), Image.LANCZOS)


        ###############################################################################################################
        if os.path.isfile('/tmp/out.txt'):
            DataFileName='/tmp/out.txt'
            datafile=open(DataFileName, 'r')
            dataz=datafile.readlines()
            datafile.close()
        else:
            dataz=''

        if not dataz:
            last_time_fw = 'N/A'

        overlay = "1" # 0 will disable overlay
        spines_ovrl="1" 
        stars_ovrl="0" # usefull for calibration of distortion
        if (overlay == "1"):
            alfa_trail=0.25
            in_center = 260 # azimuth in center of image
            center_lim=float(in_center)
        
            #print center_lim


            top_lim=25 ##35 ##40 ##45
            bott_lim= -10 ##-5 ##0 ##5

            lewy_lim=61 # probably redundant
            prawy_lim=61 # probably redundant
            #lewy_lim=konw_a(center_lim)-lewy_lim+23
            #prawy_lim=konw_a(center_lim)+prawy_lim-23
            #axll=lewy_lim-24
            #axrl=prawy_lim+21
            #print in_center,dirname,filename
            #
            def konw_a(azimuth):
                # there was a reason why def in here :/
                global center_lim
                #lon=335;
                lewy_lim=55
                prawy_lim=55

                if (center_lim+prawy_lim) < 360 and (center_lim-lewy_lim) > 0:
                    konw_azi=azimuth
                else:
                    konw_azi=np.mod(azimuth - 180.0, 360.0) - 180.0
                return konw_azi

            lewy_lim=konw_a(center_lim)-lewy_lim
            prawy_lim=konw_a(center_lim)+prawy_lim
            axll=lewy_lim #+2
            axrl=prawy_lim

            #plt.ioff()
            ##########################################################################
            #### ax = matplotlib.pyplot.figure(figsize=(12.0, 3.95))
            #### ax = matplotlib.pyplot.figure(figsize=(19.20, 10.40))
            #### add to .config/matplotlib/matplotlibrc line backend : Agg !!! ###
            ##########################################################################
            #ax = plt(figsize=(19.20, 10.40))
            
            plt = Figure(figsize=(12.80, 7.20)) # 1280x720px
            plt.patch.set_alpha(0)
            canvas = FigureCanvasAgg(plt)
            ax = plt.add_subplot(111)#, facecolor='#ff0000')  # create figure & 1 axis
            ax.patch.set_alpha(0)


            # correction up/down for unleveled axis of rotation
            if (45 < int(in_center) <= 90):
                axtl=-1.5 ##-3
                axbl=52.25 ##58
            elif (90 < int(in_center) <= 135):
                axtl= -2.0 #-2.5  ##-3
                axbl= 51.75 #52.25 ##58
            elif (135 < int(in_center) <= 160):
                axtl=-2.75 ##-3
                axbl=54.0 ##
            elif (160 < int(in_center) <= 200):
                axtl=-1.75 ##-3
                axbl=52.50 ##58
            elif (200 < int(in_center) <= 225):
                axtl=-2.75 ##-3
                axbl=54.0 ##58
            elif (245 < int(in_center) <= 270):
                axtl= -1.0 # -3.5 ##-3
                axbl= 53.5 # 54.25 ##58
            elif (270 < int(in_center) <= 315):
                axtl=-0.5 ##-3
                axbl=53.25 ##58
            elif (315 < int(in_center) <= 360):
                axtl=-2.0 ##-3
                axbl=54.75 ##58
            elif (0 <= int(in_center) <= 45):
                axtl=-1.5 ##-3
                axbl=53.25 ##58
            else:
                axtl=-3.5 ##-3
                axbl=54.25 ##58

            ax.set_xlim(axll,axrl)
            ax.set_ylim(axtl,axbl)
            


            #lewy_lim=konw_a(center_lim)-lewy_lim+23
            #prawy_lim=konw_a(center_lim)+prawy_lim-23
            #ax.set_xlim(lewy_lim-24,prawy_lim+24)        
            #ax.set_ylim(-3,58)

            
            fontX = {'color':  "white", 'size': 12, 'weight': 'bold', 'family': 'monospace', }        
            vert_alX=str('top') ; hori_alX=str('center')    
            for x in range(int(lewy_lim-30),int(prawy_lim+31),10):
                x1,y1 = distorsXY1(in_center,x,0)
                ax.plot(x1,y1,"+",markersize=15, markerfacecolor='red', markeredgecolor='red', alpha=1)
                ax.text(x1,y1, ' \n'+str(x)+' \n ', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=1)
        
            #dol‚-gora limity
            #ax.set_ylim(0,55)        
            #ax.set_xticks([0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180])
            #ax.set_yticks([0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180])
            
            #te dzialajo
            #plt.tick_params(axis='y', which='major', labelsize=8, labelcolor='none',color='none')#,direction='in')
            
            
            if (spines_ovrl == "1"):
                    ax.spines['bottom'].set_color('darkred')
                    ax.spines['top'].set_color('darkred') 
                    ax.spines['right'].set_color('darkred')
                    ax.spines['left'].set_color('darkred')
                    ax.tick_params(axis='y', which='major', labelsize=8, labelcolor='white',color='none')#,direction='in')
                    ax.tick_params(axis='x', which='major', labelsize=8, labelcolor='white',color='none')#,direction='in')

            elif (spines_ovrl == "0"):
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['top'].set_visible(False) 
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.tick_params(axis='y', which='major', labelsize=8, labelcolor='none',color='none')#,direction='in')
                    ax.tick_params(axis='x', which='major', labelsize=8, labelcolor='none',color='none')#,direction='in')
            #plt.tick_params(axis='y', which='major', labelsize=8, labelcolor='#ffffff',direction='in')
            #plt.tick_params(axis='x', which='major', labelsize=8, labelcolor='#ffffff',direction='in')
            #plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=14)
            #plt.setp(ax.get_xticklabels(), fontsize=14)
        
            #ax.tick_params(axis='y', labelcolor='#ff0000')
            #ax.set_yticklabels('y')
            #ax.set_yticklabels(ax.get_yticks()[::-1])
            #ax.spines['polar'].set_visible(False) #wylacza zewn krawedz
            
            #ax.set_yticklabels([])
            #ax.grid(True)
            ax.grid(False)
            fontX = {'color':  "white", 'size': 10, 'weight': 'normal', 'family': 'monospace', }
            vert_alX=str('top') ; hori_alX=str('left')
            
            
            #######
            if (stars_ovrl == "1"):
                #lista_s=['Alpheratz','Algenib','Scheat','Sadalmelik','Markab','Enif','Arneb','Elnath','Mirzam','Saiph','Bellatrix','Alhena','Polaris','Phecda','Dubhe','Castor','Pollux','Mizar','Betelgeuse','Altair','Vega','Rigel','Diphda','Sirius','Arcturus','Capella','Hamal','Alcyone','Aldebaran','Alphecca','Menkalinan','Menkar','Procyon','Deneb','Sadr','Regulus']
                lista_s=['Acamar', 'Achernar', 'Acrux', 'Adara', 'Adhara', 'Agena', 'Albereo', 'Alcaid', 'Alcor', 'Alcyone', 'Aldebaran', 'Alderamin', 'Alfirk', 'Algenib', 'Algieba', 'Algol', 'Alhena', 'Alioth', 'Alkaid', 'Almach', 'Alnair', 'Alnilam', 'Alnitak', 'Alphard', 'Alphecca', 'Alpheratz', 'Alshain', 'Altair', 'Ankaa', 'Antares', 'Arcturus', 'Arkab Posterior', 'Arkab Prior', 'Arneb', 'Atlas', 'Atria', 'Avior', 'Bellatrix', 'Betelgeuse', 'Canopus', 'Capella', 'Caph', 'Castor', 'Cebalrai', 'Deneb', 'Denebola', 'Diphda', 'Dubhe', 'Electra', 'Elnath', 'Eltanin', 'Enif', 'Etamin', 'Fomalhaut', 'Formalhaut', 'Gacrux', 'Gienah', 'Gienah Corvi', 'Hadar', 'Hamal', 'Izar', 'Kaus Australis', 'Kochab', 'Maia', 'Markab', 'Megrez', 'Menkalinan', 'Menkar', 'Menkent', 'Merak', 'Merope', 'Miaplacidus', 'Mimosa', 'Minkar', 'Mintaka', 'Mirach', 'Mirfak', 'Mirzam', 'Mizar', 'Naos', 'Nihal', 'Nunki', 'Peacock', 'Phecda', 'Polaris', 'Pollux', 'Procyon', 'Rasalgethi', 'Rasalhague', 'Regulus', 'Rigel', 'Rigil Kentaurus', 'Rukbat', 'Sabik', 'Sadalmelik', 'Sadr', 'Saiph', 'Scheat', 'Schedar', 'Shaula', 'Sheliak', 'Sirius', 'Sirrah', 'Spica', 'Suhail', 'Sulafat', 'Tarazed', 'Taygeta', 'Thuban', 'Unukalhai', 'Vega', 'Vindemiatrix', 'Wezen', 'Zaurak', 'Zubenelgenubi']
                for star in lista_s:
                    v = ephem.star(star)
                    v.compute(gatech)
                        #ax.plot(konw_a(round(math.degrees(v.az), 1)),round(math.degrees(v.alt),1),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3) 
                    #ax.text(konw_a(round(math.degrees(v.az), 1)),(round(math.degrees(v.alt), 1)), ' \n'+str(star)+' \n ', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
            
                    if ( konw_a(round(math.degrees(v.az))) > (lewy_lim-50)) and (konw_a(round(math.degrees(v.az))) < (prawy_lim+50)) and (math.degrees(v.alt) > -10) and (math.degrees(v.alt) < 65):
                        x,y = distorsXY1(in_center, konw_a(round(math.degrees(v.az),1)),math.degrees(v.alt))
                        #print str(star),"         ",konw_a(round(math.degrees(v.az), 1)),round(math.degrees(v.alt),1),"        ",round(x, 1), round(y,1) 
                        #ax.plot(konw_a(round(math.degrees(v.az), 1)),round(math.degrees(v.alt),1),'o',markersize=5, markerfacecolor='none', markeredgecolor='yellow', alpha=0.2) 
                        ax.plot(x,y,'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=.1) 
                        ax.text(x,y, ' \n'+str(star)+' \n ', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)

            
            ###########
        
            #print str(round(math.degrees(v.az), 1))+' '+str(round(math.degrees(v.alt),1))
            #print str(konw_a(round(math.degrees(v.az), 1)))+' '+str(konw_a(round(math.degrees(v.alt),1)))
            #print"--"
            vert_alX=str('bottom') ; hori_alX=str('left')    
            fontX = {'color':  "white", 'size': 18, 'weight': 'bold', 'family': 'monospace', }
            fontX_c = {'color':  "black", 'size': 18, 'weight': 'bold', 'family': 'monospace', }
            
            vs = ephem.Sun(gatech)
            vm = ephem.Moon(gatech)
            vju = ephem.Jupiter(gatech)
            vsa = ephem.Saturn(gatech)
            vma = ephem.Mars(gatech)
            vve = ephem.Venus(gatech)

        
        
            if ( konw_a(round(math.degrees(vs.az))) > (lewy_lim-30)) and (konw_a(round(math.degrees(vs.az))) < (prawy_lim+30)) and (math.degrees(vs.alt) > -30) and (math.degrees(vs.alt) < 75):
                vsx,vsy = distorsXY1(in_center, konw_a(round(math.degrees(vs.az),1)),math.degrees(vs.alt))
                ax.plot(vsx,vsy,'o',markersize=15, markerfacecolor='none', markeredgecolor='#000000', alpha=1)
                ax.text(vsx,vsy, ' \n '+sols, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX_c, alpha=0.3)
                ax.plot(vsx,0,'.',markersize=5, markerfacecolor='none', markeredgecolor='#ffffff', alpha=1) 
            if ( konw_a(round(math.degrees(vm.az))) > (lewy_lim-40)) and (konw_a(round(math.degrees(vm.az))) < (prawy_lim+40)) and (math.degrees(vm.alt) > -30) and (math.degrees(vm.alt) < 75):
                vmx,vmy = distorsXY1(in_center, konw_a(round(math.degrees(vm.az),1)),math.degrees(vm.alt))
                ax.plot(vmx,vmy,'o',markersize=15, markerfacecolor='none', markeredgecolor='#000000', alpha=0.3)
                ax.text(vmx,vmy, ' \n '+luns, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX_c, alpha=0.3)
            if ( konw_a(round(math.degrees(vju.az))) > (lewy_lim-30)) and (konw_a(round(math.degrees(vju.az))) < (prawy_lim+30)) and (math.degrees(vju.alt) > -30) and (math.degrees(vju.alt) < 75):
                vjux,vjuy = distorsXY1(in_center, konw_a(round(math.degrees(vju.az),1)),math.degrees(vju.alt))
                ax.plot(vjux,vjuy,'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
                ax.text(vjux,vjuy, ' \n '+jups, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
            if ( konw_a(round(math.degrees(vsa.az))) > (lewy_lim-30)) and (konw_a(round(math.degrees(vsa.az))) < (prawy_lim+30)) and (math.degrees(vsa.alt) > -30) and (math.degrees(vsa.alt) < 75):
                vsax,vsay = distorsXY1(in_center, konw_a(round(math.degrees(vsa.az),1)),math.degrees(vsa.alt))
                ax.plot(vsax,vsay,'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
                ax.text(vsax,vsay, ' \n '+sats, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
            if ( konw_a(round(math.degrees(vma.az))) > (lewy_lim-30)) and (konw_a(round(math.degrees(vma.az))) < (prawy_lim+30)) and (math.degrees(vma.alt) > -30) and (math.degrees(vma.alt) < 75):
                vmax,vmay = distorsXY1(in_center, konw_a(round(math.degrees(vma.az),1)),math.degrees(vma.alt))
                ax.plot(vmax,vmay,'o',markersize=15, markerfacecolor='none', markeredgecolor='red', alpha=0.3)
                ax.text(vmax,vmay, ' \n '+mars, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
            if ( konw_a(round(math.degrees(vve.az))) > (lewy_lim-30)) and (konw_a(round(math.degrees(vve.az))) < (prawy_lim+30)) and (math.degrees(vve.alt) > -30) and (math.degrees(vve.alt) < 75):
                vvex,vvey = distorsXY1(in_center, konw_a(round(math.degrees(vve.az),1)),math.degrees(vve.alt))
                ax.plot(vvex,vvey,'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
                ax.text(vvex,vvey, ' \n '+vens, verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)

            alfa_cali=0.5
            fontX = {'color':  "white", 'size': 10, 'weight': 'normal', 'family': 'monospace', }

            vert_alX=str('top') ; hori_alX=str('left')
            #ax.plot(konw_a(112),3,'o',markersize=15, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3) 
            #ax.plot(konw_a(81),3,'o',markersize=15, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3) 
            #ax.plot(konw_a(112),3,'o',markersize=35, markerfacecolor='gray', markeredgecolor='none', alpha=0.3) 
            #ax.plot(konw_a(113.3),2.4,'o',markersize=15, markerfacecolor='none', markeredgecolor='black', alpha=0.3) 
            # My orientation points on horizon, chimneys, cranes, etc. for calibration:
            orientacyjne= [
            [12,        1.5        ],
            [27,	1.5	],
            [65,	1.2	],
            [113,	3.4	],
            [189,	5	],
            [164,	12	],
            [162,	6	],
            [253,	6	],
            [295.5,	1.5	],
            [320,	1.5	],
            [329,	6	],
            [341, 	8	],
            [354,	7.5	]]
            
            for i in orientacyjne:
                if ( konw_a(i[0]) > (lewy_lim-30)) and (konw_a(i[0]) < (prawy_lim+30)) and (i[1] > -30) and (i[1] < 75):
                    x,y = distorsXY1(in_center, konw_a(i[0]),i[1])
                    x1,y1 = distorsXY1(in_center, konw_a(i[0]),(0))
                    #ax.plot(konw_a(i[0]),i[1],'o',markersize=15, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3)
                    ax.plot(konw_a(x),y,'o',markersize=5, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3)
                    ax.plot([konw_a(x),konw_a(x1)],[y,y1],'-',markersize=15, lw=2,color='yellow', alpha=0.3)
                    
            #print i
            
            plt.subplots_adjust(left=0.0, bottom=0.13, right=1.0, top=1.0)

        
            for i,line in enumerate(dataz):
                #print line
                plane_dict = line.split(',')
                
                #print flight
                #print plane_dict[1]
                #print (plane_dict[pentry][3])
                
                flight=str(plane_dict[1].strip())
                if flight == '':
                    flight = str(plane_dict[0].strip())
                    
                #meters=int(str(plane_dict[4].strip()))
                if is_int_try(str(plane_dict[4].strip())):
                        meters=int(str(plane_dict[4].strip()))
                elif is_float_try(str(plane_dict[4].strip())):
                        meters=int(float(str(plane_dict[4].strip())))
                else:
                    meters=10000
                    
                distance=float(plane_dict[5].strip())
                
                #track=float(360-(270-float(plane_dict[11].strip())))
                #    azi=np.radians(float(plane_dict[6].strip()))
                azi=konw_a(float(plane_dict[6].strip()))
                aaz=konw_a(float(plane_dict[6].strip()))
                elev=float(plane_dict[7].strip())
                elunc=float(plane_dict[7].strip())
                #kolorek=str(plane_dict[pentry][8])
                kolorek='#ff0000'
                dziewiec=str(plane_dict[9].strip())
                dwana=str(plane_dict[12].strip())
                if i == 0:
                    if not plane_dict[18].strip() == '':
                        last_time_fw=str(plane_dict[18].strip())
                
                pos_age = int(float(str(plane_dict[29].strip())))
                if pos_age > 30:
                    alpha_age = 0.1
                elif pos_age > 20:
                    alpha_age = 0.2
                elif pos_age > 15:
                    alpha_age = 0.3
                elif pos_age > 10:
                    alpha_age = 0.4
                else:
                    alpha_age = 0.6
                    ##################### to bylo aktywne
                loSep = -10
                hiSep = 10
                #if not plane_dict[22].strip() == '':
                if is_float_try(str(plane_dict[20].strip())):
                    dist2mo1 = str(plane_dict[19].strip())
                    deg_missed1 = float(str(plane_dict[20].strip()))
                    if (loSep < float(deg_missed1) < hiSep):
                        #moon_s=dist2mo1+'km @'+str(deg_missed1)+deg+' \n '+str(plane_dict[27].strip())+'\n'
                        moon_s=dist2mo1+'km '+sols+' '+str(deg_missed1)+deg+' \n'
                    else:
                        #moon_s='X n/a '+str(plane_dict[27].strip())+'\n'
                        #moon_s='X1 n/a '+'\n'
                        moon_s=''
                        #dist2mo+' o '+str(deg_missed)+deg+' \n '
                else:
                    deg_missed1 = ''
                    #moon_s= 'X -- '+str(plane_dict[27].strip())+'\n'
                    #moon_s= 'X1 -- '+'\n'
                    moon_s= ''
                    #if float(deg_missed) < 90:
                
                
                #if not plane_dict[26].strip() == '':
                if is_float_try(str(plane_dict[24].strip())):
                    dist2mo2 = str(plane_dict[23].strip())
                    deg_missed2 = float(str(plane_dict[24].strip()))
                    if (loSep < float(deg_missed2) < hiSep):
                        #sun_s=dist2mo2+'km @'+str(deg_missed2)+deg+'  '+str(plane_dict[28].strip())+'\n'
                        sun_s=dist2mo2+'km '+luns+' '+str(deg_missed2)+deg+' \n'
                    else:
                        #sun_s='X n/a '+str(plane_dict[28].strip())+'\n'
                        #sun_s='X2 n/a '+'\n'
                        sun_s=''
                        #dist2mo+' o '+str(deg_missed)+deg+' \n '
                else:
                    deg_missed2 = ''
                    #sun_s= 'X -- '+str(plane_dict[28].strip())+'\n'
                    #sun_s= 'X2 -- '+'\n'
                    sun_s= ''
                    #if float(deg_missed) < 90:
                            
                    #print flight,dziewiec, dwana
                
                ##################### to bylo aktywne
                    
                #########################    
                #
                # marker_style = dict(linestyle=':', color='0.8', markersize=10,mfc="C0", mec="C0")
                # marker_style.update(mec="None", markersize=15)
                # marker = "$[$"+" "+"$]$"
                # ax.plot(azi,elev, marker=marker, markersize=5, markerfacecolor='none', markeredgecolor=str(kolorek)) 
                #
                #########################
        
                #if aaz >= 0 and aaz < 90:
                    #        vert_al=str('top') ; hori_al=str('left')
                #elif aaz >= 90 and aaz < 180:
                    #        vert_al=str('bottom') ; hori_al=str('left')
                #elif aaz >= 180 and aaz < 270:
                    #        vert_al=str('bottom') ; hori_al=str('right')
                #elif aaz >= 270:
                    #        vert_al=str('top') ; hori_al=str('right')
                vert_al=str('bottom') ; hori_al=str('right')
                fonta = {'color':  "black", 'size': 12, 'weight': 'normal', 'family': 'monospace', }
                fontb = {'color':  "black", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                fontc = {'color':  "black", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                #fonta['color'] = 'kupa'
                #print fonta    
                
                if meters < 5000:
                    fonta['color'] = '#ff9900' ; fonta['size'] = '12' 
                    fontb['color'] = '#ff9900' ; fonta['size'] = '12'
                    fontc['color'] = '#ff9900' ; fonta['size'] = '12'
                elif (dwana == 'WARNING' and dziewiec != "RECEDING") and (meters >= 5000):
                    fonta['color'] = '#ff0000' 
                    fontb['color'] = '#ff0000'
                    fontc['color'] = '#ffffff'
                elif (dwana == 'WARNING' and dziewiec == "RECEDING") and (meters >= 5000):
                    fonta['color'] = '#660000' 
                    fontb['color'] = '#660000'
                    fontc['color'] = '#ffffff'
                elif (dwana != 'WARNING' and dziewiec == "RECEDING") and (meters >= 5000):
                    fonta['color'] = '#8000ff' 
                    fontb['color'] = '#8000ff'
                    fontc['color'] = '#ffffff'
                else: 
                    fonta['color'] = '#ff00ff' 
                    fontb['color'] = '#ff00ff' 
                    fontc['color'] = '#ffffff' 
                #moon_s='aaaa'
                if aaz > lewy_lim-23 and aaz < prawy_lim+23: 
                        aazx,eluncy = distorsXY1(in_center, konw_a(aaz),elunc)
                        if meters < 5000:
                            fonta['size'] = '12' 
                            fonta['size'] = '12'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, ' \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment='bottom', horizontalalignment=hori_al, fontdict=fontc,alpha=(alpha_age+0.2))
                        elif (distance > 60) and (meters >= 5000):
                            fonta['size'] = '10' 
                            fonta['size'] = '10'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment='bottom', horizontalalignment=hori_al, fontdict=fontc,alpha=alpha_age )
                        elif (distance <= 60) and distance > 40 and (meters >= 5000):
                            fonta['size'] = '10' 
                            fonta['size'] = '10'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc,alpha=alpha_age )
                        elif (distance <= 40) and distance > 20 and (meters >= 5000):
                            fonta['size'] = '11' 
                            fonta['size'] = '11'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc,alpha=alpha_age )
                        elif (distance <= 20) and (meters >= 5000):
                            fonta['size'] = '11' 
                            fonta['size'] = '11'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc,alpha=alpha_age )
                        else:
                            fonta['size'] = '12' 
                            fonta['size'] = '12'
                            ax.plot(aazx,eluncy,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'],alpha=0.3) 
                            ax.text(aazx,eluncy, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n  '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc,alpha=alpha_age )

                        aazs        = []
                        elevis        = []
                        #aazs.append(aazx)
                        #elevis.append(eluncy)
                        ############################## tranzyty
                        if is_float_try(str(deg_missed1)):
                             if (loSep < float(deg_missed1) < hiSep):
                                #if not plane_dict[41].strip() == '':
                                fut_alt = float(plane_dict[22].strip())
                                fut_az  = float(str(plane_dict[21].strip()))
                                #moon_s=dist2mo+' X '+moon_miss_by+' \n '
                                #aazx,eluncy
                                if not fut_az == 0:
                                    object1 = str(plane_dict[27].strip())
                                    if not object1  == '':
                                        if object1 == 'Moon':
                                            v = ephem.Moon(gatech)
                                        elif object1 == 'Sun':
                                            v = ephem.Sun(gatech)
                                        elif object1 == 'Mars':
                                            v = ephem.Mars(gatech)
                                        elif object1 == 'Jupiter':
                                            v = ephem.Jupiter(gatech)
                                        elif object1 == 'Saturn':
                                            v = ephem.Saturn(gatech)
                                        else:
                                            v = ephem.star(object1)
                                            v.compute(gatech)

                                    vsx,vsy = distorsXY1(in_center, konw_a(round(math.degrees(v.az),1)),math.degrees(v.alt))
                                    fut_az,fut_alt = distorsXY1(in_center, float(fut_az), float(fut_alt))
                                    tst_x=[vsx, float(fut_az), aazx]
                                    tst_y=[vsy, float(fut_alt) ,eluncy]

                                    #print fut_az, fut_alt 
                                    #tst_x=[vmax, aazx]
                                    #tst_y=[vmay ,eluncy]
                                    ax.plot(tst_x,tst_y,'--',markersize=10, color='yellow', lw=1,alpha=0.3)

                        if is_float_try(str(deg_missed2)):
                            if (loSep < float(deg_missed2) < hiSep):
                                #if not plane_dict[41].strip() == '':
                                fut_alt = float(plane_dict[26].strip())
                                fut_az  = konw_a(float(str(plane_dict[25].strip())))

                                #moon_s=dist2mo+' X '+moon_miss_by+' \n '
                                #aazx,eluncy
                                if not fut_az == 0:
                                    object2 = str(plane_dict[28].strip())
                                    if not object2  == '':
                                        if object2 == 'Moon':
                                            v = ephem.Moon(gatech)
                                        elif object2 == 'Sun':
                                            v = ephem.Sun(gatech)
                                        elif object2 == 'Mars':
                                            v = ephem.Mars(gatech)
                                        elif object2 == 'Jupiter':
                                            v = ephem.Jupiter(gatech)
                                        elif object2 == 'Saturn':
                                            v = ephem.Saturn(gatech)
                                        else:
                                            v = ephem.star(object2)
                                            v.compute(gatech)

                                    vsx,vsy = distorsXY1(in_center, konw_a(round(math.degrees(v.az),1)),math.degrees(v.alt))
                                    fut_az,fut_alt = distorsXY1(in_center, float(fut_az),float(fut_alt))
                                    tst_x=[vsx, float(fut_az), aazx]
                                    tst_y=[vsy, float(fut_alt) ,eluncy]

                                    #print fut_az, fut_alt 
                                    #tst_x=[vmax, aazx]
                                    #tst_y=[vmay ,eluncy]
                                    ax.plot(tst_x,tst_y,'--',markersize=10, color='blue', lw=1,alpha=0.2)
                        ############################## tranzyty koniec ###
                        ######### start traili 
                        tmp_i = 0
                        if not plane_dict[15].strip() == '':
                            words1 = plane_dict[15]
                            words2 = plane_dict[16]
                            plane_pos1 = words1.split(';')
                            plane_pos2 = words2.split(';')        
                            plane_pos_len = len(plane_pos1)
                            for i,word in enumerate(plane_pos1):
                                #print plane_pos1[i]
                                #print plane_pos2[i]
                                if not plane_pos1[i].strip() == '':
                                    aaz1=konw_a(float(plane_pos1[i].strip()))
                                    ele1=float(plane_pos2[i].strip())
                                    aaz1a,ele1a = distorsXY1(in_center,aaz1,ele1)
                                    aazs.append(aaz1a)
                                    elevis.append(ele1a)
                                    if ((plane_pos_len-1) > i > 0):
                                        if aazs[i] > lewy_lim-23 and aazs[i] < prawy_lim+23: 
                                            alpha_hist = round(1/float(plane_pos_len/float(i)),2)
                                            # this is cool with blending trails, but time cost is crazy with ax.plot in loop
                                            #ax.plot((aazs[i-1],aazs[i]),(elevis[i-1], elevis[i]),'-',markersize=10, color=fontb['color'], lw=1, alpha=(alpha_hist/2))
                                    else:
                                        alpha_hist = 1
                                    tmp_i = i
                            #ax.plot(aaz1a,ele1a,'o',markersize=3, color=fontb['color'],alpha=alfa_trail)
                            # this is less cool, because I can't pass alpha as array, but much faster:
                            ax.plot((aazs[0:tmp_i+1]),(elevis[0:tmp_i+1]),'-',markersize=10, color=fontb['color'], lw=1, alpha=0.6)

                        #ax.plot(aazs,elevis,'o',markersize=5, color=fontb['color'], lw=1.5,alpha=0.3) 
                        #ax.plot(aazs,elevis,'-',markersize=5, color='white', lw=1.5,alpha=0.3) 
                        #ax.plot(aazs,elevis,'-',markersize=5, color=fontb['color'], lw=1,alpha=0.3) 
                        #########koniec traili 
            iss=ephem.readtle(issline[0], issline[1], issline[2])
            iss.compute(gatech)
            #print math.degrees(iss.alt),math.degrees(iss.az)
            #info = gatech.next_pass(iss)
            #print("Rise time: %s azimuth: %s" % (info[0], info[1]))
            if iss.eclipsed:
                fontX = {'color':  "darkgray", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                vert_alX=str('bottom') ; hori_alX=str('left')
            else:
                    fontX = {'color':  "white", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                    vert_alX=str('bottom') ; hori_alX=str('left')
            if round(math.degrees(iss.alt),1) > 0:

                issaz,issele = distorsXY1(in_center, konw_a(round(math.degrees(iss.az), 1)),round(math.degrees(iss.alt), 1))
                ax.plot(issaz,issele,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontX['color'], alpha=1) 
                #ax.text(konw_a(round(math.degrees(iss.az), 1)),(round(math.degrees(iss.alt), 1)), ' ISS', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
                ax.text(issaz,issele, ' \n ISS \n '+str(int(iss.range)/1000)+'km', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.9)

            iss_azis=[]
            iss_elevis=[]
            ISS_PREDICT=[-180,-150,-120,-90,-60,-30,30,60,90,120,150,180,210,240,270,300,330,360,390,420,450,480,510,540,570,600]
            for i in ISS_PREDICT:
                d_t1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=i)#+ datetime.timedelta(minutes=35)
                gatech.date = ephem.Date(d_t1)
                iss.compute(gatech)
                if round(math.degrees(iss.alt),1) > 0:
                    issaz,issele = distorsXY1(in_center, konw_a(round(math.degrees(iss.az), 1)),round(math.degrees(iss.alt), 1))
                    ax.plot(issaz,issele,'o',markersize=4, markerfacecolor=fontX['color'], markeredgecolor=fontX['color'], alpha=0.6)
                    iss_azis.append(issaz)
                    iss_elevis.append(issele)
                ####print iss.az,round(math.degrees(iss.alt),1)

            #ax.plot(iss_azis,iss_elevis,'--',markersize=10, color='white', lw=1, alpha=0.6) 
            ####print iss_elevis
        
            gatech.date = ephem.now() #RESET!
            #ax.plot(float(in_center),15,'+',markersize=5, color='darkgreen', alpha=1)
            '''
            ax.plot(float(in_center),50,'+',markersize=15, color='darkgreen', alpha=1)
            ax.plot(float(in_center)+55,50,'+',markersize=15, color='darkgreen', alpha=1)
            ax.plot(float(in_center)-55,50,'+',markersize=15, color='darkgreen', alpha=1)
            ax.plot(float(in_center)+55,0,'+',markersize=15, color='darkgreen', alpha=1)
            ax.plot(float(in_center)-55,0,'+',markersize=15, color='darkgreen', alpha=1)
            '''
            kalib= [
            [float(in_center),	        15	],
            [float(in_center),	        50	],
            [float(in_center)+55,       50	],
            [float(in_center)-55,       50	],
            [float(in_center)+55,       25	],
            [float(in_center)-55,       25	],
            [float(in_center)+55,       0	],
            [float(in_center)-55,       0	]]
            
            '''
            [float(in_center),		],
            [float(in_center),	6	],
            [float(in_center),	6	],
            [float(in_center),	1.5	],
            [float(in_center),	1.5	],
            [float(in_center),	6	],
            [float(in_center), 	8	],
            [float(in_center),	7.5	]]
            '''
            '''
            for i in kalib:
                    if ( konw_a(i[0]) > (lewy_lim-30)) and (konw_a(i[0]) < (prawy_lim+30)) and (i[1] > -30) and (i[1] < 75):
                    x,y = distorsXY1(in_center, konw_a(i[0]),i[1])
                    ax.plot(konw_a(i[0]), i[1],'+',markersize=15, color='green', alpha=1)
                    ax.plot(konw_a(x), y,'+',markersize=15, color='white', alpha=1)
                    #x1,y1 = distorsXY1(in_center, konw_a(i[0]),(0))
                    #ax.plot(konw_a(i[0]),i[1],'o',markersize=15, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3)
                    #ax.plot(konw_a(x),y,'o',markersize=5, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3)
                    ax.plot([konw_a(x),konw_a(i[0])],[y,i[1]],'-',markersize=15, lw=2,color='yellow', alpha=0.3)        
            '''
            '''
            for x in range(int(lewy_lim-30),int(prawy_lim+31),5):
                xdoa3 = []
                ydob3 = []
                for y in range(-0,61,10):
                    x1,y1 = distorsXY1a(x,y)
                    ax.plot(x,y,"*",markersize=2, markerfacecolor='none', markeredgecolor='red')
                    ax.plot(x1,y1,'o',markersize=5, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3) 
                    # xdoa3.append(x)
                    xdoa3.append(x1)
                    # ydob3.append(y)
                    ydob3.append(y1)        
                ax.plot(xdoa3,ydob3, '-',markersize=10, color='red', lw=1,alpha=.4)
                # print x,x1,"                ",y,y1

            for y in range(-0,61,10):        
                xdoa3 = []
                ydob3 = []
                    for x in range(int(lewy_lim-30),int(prawy_lim+31),10):
                    x1,y1 = distorsXY1a(x,y)
                    xdoa3.append(x1)
                    ydob3.append(y1)        
                ax.plot(xdoa3,ydob3, '-',markersize=10, color='red', lw=1,alpha=.4)

            '''
            #gatech.date = ephem.now()
            testtime = datetime.datetime.now().strftime('%H:%M:%S')
            fontX = {'color':  "white", 'size': 10, 'weight': 'normal', 'family': 'monospace', }
            time_pl = float(in_center) + 30

            ax.text(int(time_pl),-2., str('Plot_t:  '+testtime), fontdict=fontX, alpha=1)
            ax.text(int(time_pl)+15,-2, str('Radar_t: '+last_time_fw), fontdict=fontX, alpha=1)
            
            s, (width, height) = canvas.print_to_buffer()
            foreground = Image.frombytes("RGBA", (width, height), s)#,alpha=1)
            imgHD.paste(foreground, (0, 0), foreground)

            opencvImageHD = cv2.cvtColor(np.array(imgHD), cv2.COLOR_RGB2BGR)

            ###############################################################################################################

        datafileA7=open(DataFileNameA7, 'r')
        datazA7=datafileA7.readlines()
        datafileA7.close()


        datafileA8=open(DataFileNameA8, 'r')
        datazA8=datafileA8.readlines()
        datafileA8.close()
        
        if self.mono == 0: 
            opencvImageHD = cv2.cvtColor(np.array(imgHD), cv2.COLOR_RGB2BGR)
            ocvi = opencvImageHD.astype(np.single)
            if not float(op) == float(datazA7[0]):
                op = float(datazA7[0])
            if not str(maska_str) == str(datazA8[0]):
                print(miscfld+"/"+str(maska_str)+" -> /home/pi/zwo-skycam/"+str(datazA8[0]))
                maska_str = str(datazA8[0])
                maskaAntyFiol0 = cv2.imread(miscfld+"/"+str(maska_str)) 
                maskaAntyFiol0 = maskaAntyFiol0.astype(np.single)        
            ocvi1 = op * (ocvi / 255) * (ocvi + ((2 * maskaAntyFiol0) / 255) * (255 - ocvi)) + (1 - op) * ocvi
            cv2.imwrite(tmpfld+'/wsc_720p_tmp.jpg', ocvi1, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        else:
            ocvi1 = opencvImageHD
            cv2.imwrite(tmpfld+'/wsc_720p_tmp.jpg', ocvi1, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            #imgHD.save(tmpfld+'/wsc_720p_tmp.jpg')

        shutil.copy( tmpfld+'/wsc_720p_tmp.jpg', tmpfld+"/WSC.tmp/"+self.aktual_t_f+".jpg")
        shutil.move( tmpfld+'/wsc_720p_tmp.jpg', tmpfld+'/wsc_720p.jpg')
        #imim.save(tmpfld+'/wsc_fullsize.jpg',"JPEG", quality=95)
        imim.save(tmpfld+'/wsc_fullsize_tmp.jpg')
        #imcv2.save(tmpfld+'/wsc_720p.jpg')
        #shutil.copy( tmpfld+'/wsc_720p.jpg', tmpfld+"/WSC/"+self.aktual_t_f+".jpg")
        shutil.move( tmpfld+'/wsc_fullsize_tmp.jpg', tmpfld+"/WSC/"+self.aktual_t_f+".jpg")
        #shutil.move( tmpfld+'/wsc_720p.jpg', tmpfld+'/img.jpg')
        aktual_t2 = datetime.datetime.now()
        took_t = datetime.timedelta.total_seconds(aktual_t2-aktual_t1)

        if (int(self.exposure) >= 1000000):
            step = 250000
        elif (int(self.exposure) >= 400000):
            step = 50000 #
        elif (int(self.exposure) >= 250000):
            step = 25000 #ok
        elif (int(self.exposure) >= 100000):
            step = 10000 # niby 10k ok 0225_1753
        elif (int(self.exposure) >= 50000):
            step = 5000 # za wolno 5000 moze ???
        elif (int(self.exposure) >= 10000):
            step = 1000
        elif (int(self.exposure) >= 5000):
            step = 250
        elif (int(self.exposure) >= 1000):
            step = 100
        elif (int(self.exposure) >= 500):
            step = 50
        else:
            step = 25

        if ( test_br > 200 ):
            step = step * 5
            #if (14.0 >= float(self.iso) >= 3.0):
            #    istep = 2.0
            #else:
            #    istep = 0.5

            print("x")
        elif ( test_br < 20 ):
            step = step * 5
            #if (12.0 >= float(self.iso) >= 1.0):
            #    istep = 2.0
            #else:
            #    istep = 0.5
            print("u")
            #else:
            #istep = 0.5
        # gain step
        istep = 0.5

        #else:
        #    iStep = 0.5


        max_gain = 14.0
        st_iso_dla_min = 9900000
        st_iso_dla_max = 11000000
        #st_iso_dla_min = 4500000
        #st_iso_dla_max = 5500000

        if (test_br < int(dataz3[0])):
            if mniej >= 1:
                mniej = 0
                print("<"+str(int(dataz3[0])))
                if ((int(self.exposure) >= st_iso_dla_min and int(self.exposure) <= st_iso_dla_max) and (float(self.iso) >= 1 and ((float(self.iso)+float(istep)) <= max_gain))):
                    with open(DataFileName1,'w') as tsttxt:
                        newdataz = float(self.iso)+float(istep) #0.5 #1.0
                        tsttxt.write(str(newdataz)+"\n")
                else:
                    if ((int(self.exposure)+int(step)) < 10000000):
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = int(self.exposure)+int(step)
                            tsttxt.write(str(newdataz)+"\n")
                    else:
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = 10000000
                            tsttxt.write(str(newdataz)+"\n")
            else:
                mniej = mniej + 1
        elif (test_br > int(dataz2[0])):
            if wiecej >= 1:
                wiecej = 0
                print(">"+str(int(dataz2[0])))
                if ((int(self.exposure) >= st_iso_dla_min and int(self.exposure) <= st_iso_dla_max) and ((float(self.iso)-float(istep)) >= 1 and (float(self.iso) <= max_gain))):
                    print("b>"+str(int(dataz2[0])))
                    with open(DataFileName1,'w') as tsttxt:
                        newdataz = float(self.iso)-float(istep) #0.5 #1.0
                        tsttxt.write(str(newdataz)+"\n")
                elif (int(self.exposure) >= 150):
                    if ((int(self.exposure)-int(step)) > 150):
                        print("a>"+str(int(dataz2[0])))
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = int(self.exposure)-int(step)
                            tsttxt.write(str(newdataz)+"\n")
                    else:
                        pass
            else:
                wiecej = wiecej + 1
            
        print("Saved: "+str(self.aktual_t_f)+" Br: "+str(test_br)+" T: "+str(took_t)+"s")

def Main():
    global mniej 
    global wiecej 
    mniej = 0
    wiecej = 0
    cap_d()
    
if __name__=='__main__':
    Main()


