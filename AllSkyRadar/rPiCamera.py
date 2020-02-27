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
import ASR_Conf

tmpfld = ASR_Conf.TMP_FLDR
miscfld = ASR_Conf.MISC_FLDR

print("START 0: "+str(datetime.datetime.now()))

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

maskaAntyFiol = cv2.imread(miscfld+"/_maska_20200225c720.png") # niezle na niebieskie niebo
#maskaAntyFiol = cv2.imread(miscfld+"/_maska_20200225d720.png")
maskaAntyFiol = maskaAntyFiol.astype(np.single)
op = 1.0

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

        # resize for on-the-fly mp4 
        imgHD = imim.resize((1280, 720), Image.LANCZOS)
        
        if self.mono == 0: 
            opencvImageHD = cv2.cvtColor(np.array(imgHD), cv2.COLOR_RGB2BGR)
            ocvi = opencvImageHD.astype(np.single)
        
            ocvi1 = op * (ocvi / 255) * (ocvi + ((2 * maskaAntyFiol) / 255) * (255 - ocvi)) + (1 - op) * ocvi
            cv2.imwrite(tmpfld+'/wsc_720p_tmp.jpg', ocvi1, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        else:
            imgHD.save(tmpfld+'/wsc_720p_tmp.jpg')
            
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


