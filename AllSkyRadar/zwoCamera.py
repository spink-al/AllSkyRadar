import threading
import time
import math
import datetime
from skycam import SkyCam
#import cv2
from PIL import Image, ImageStat, ImageFont, ImageDraw,ImageColor
import shutil
import os, errno
import cv2
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import ephem
from scipy.interpolate import interp1d
import ASR_Conf
import ZWO_Conf

my_lat = ASR_Conf.MY_LAT
my_lon = ASR_Conf.MY_LON
my_alt = ASR_Conf.MY_ALT

tmpfld = ASR_Conf.TMP_FLDR
miscfld = ASR_Conf.MISC_FLDR
tleFileName = ASR_Conf.TMP_FLDR+'/iss.tle'

# = ZWO_Conf.
w_resize = ZWO_Conf.w_resize
h_resize = ZWO_Conf.h_resize
q_resize = ZWO_Conf.q_resize
q_fullsize = ZWO_Conf.q_fullsize

#tmpconf8 atm
theta_corr  = ZWO_Conf.theta_corr
delay_between_captures = ZWO_Conf.delay_between_captures

crop_x = ZWO_Conf.crop_x
crop_y = ZWO_Conf.crop_y
crop_w = ZWO_Conf.crop_w
crop_h = ZWO_Conf.crop_h

overlay     = ZWO_Conf.overlay
spines_ovrl = ZWO_Conf.spines_ovrl
stars_ovrl  = ZWO_Conf.stars_ovrl
h_flip      = ZWO_Conf.h_flip
v_flip      = ZWO_Conf.v_flip
# = ZWO_Conf.

d_wb1       = ZWO_Conf.d_wb1
d_wb2       = ZWO_Conf.d_wb2
n_wb1       = ZWO_Conf.n_wb1
n_wb2       = ZWO_Conf.n_wb2

plot_adj_l       = ZWO_Conf.plot_adj_l
plot_adj_b       = ZWO_Conf.plot_adj_b
plot_adj_r       = ZWO_Conf.plot_adj_r
plot_adj_t       = ZWO_Conf.plot_adj_t



landmarks_ovrl = ZWO_Conf.landmarks_ovrl
iss_ovrl = ZWO_Conf.iss_ovrl
#calibration1_ovrl = ZWO_Conf.calibration1_ovrl
#calibration2_ovrl = ZWO_Conf.calibration2_ovrl
plot_trails = ZWO_Conf.plot_trails
alhablend_trails = ZWO_Conf.alhablend_trails

DataFileName0 = tmpfld+"/tmpconf"
DataFileName1 = tmpfld+"/tmpconf1"
DataFileName2 = tmpfld+"/tmpconf2"
DataFileName3 = tmpfld+"/tmpconf3"
DataFileName4 = tmpfld+"/tmpconf4"
DataFileName7 = tmpfld+"/tmpconf7"
DataFileName8 = tmpfld+"/tmpconf8"
DataFileName9B = tmpfld+"/tmpconf9B"
SkyCam.initialize( "./asi.so" )
issline=[]
#tleFileName='/tmp/iss.tle'
tlefile=open(tleFileName, 'r')
tledata=tlefile.readlines()
tlefile.close()
for i, line in enumerate(tledata):
    if "ISS" in line:
        for l in tledata[i:i+3]: issline.append(l.strip('\r\n').rstrip()),



#try:
my_camera = SkyCam('ZWO ASI178MC')

gatech = ephem.Observer()
gatech.lat = str(my_lat)
gatech.lon = str(my_lon)
gatech.elevation = int(my_alt)
deg = u'\xb0'
uus = u'\xb5s'
jups = u"\u2643"
mars = u"\u2642"
vens = u"\u2640"
sats = u"\u2644"
sols = u"\u2609"
luns = u"\u263d"


#except ValueError:
#    print("xxxxxx")
''' 
# nie dziaĹ‚a pod python 3
def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e
'''

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


def tstasi120(im):
    q0Ax = 150 ; q0Ay = 0
    q1Ax = 150 ; q1Ay = 930
    q2Ax = 1100 ; q2Ay = 930
    q3Ax = 1100 ; q3Ay = 0
    q4Ax = 250 ; q4Ay = 100

    img0A = im.crop((q0Ax, q0Ay, q0Ax+30, q0Ay+30))
    img1A = im.crop((q1Ax, q1Ay, q1Ax+30, q1Ay+30))
    img2A = im.crop((q2Ax, q2Ay, q2Ax+30, q2Ay+30))
    img3A = im.crop((q3Ax, q3Ay, q3Ax+30, q3Ay+30))
    img4A = im.crop((q4Ax, q4Ay, q4Ax+750, q4Ay+750))

    data0A = img0A.convert ('L')
    data1A = img1A.convert ('L')
    data2A = img2A.convert ('L')
    data3A = img3A.convert ('L')
    data4A = img4A.convert ('L')
    stat0A = ImageStat.Stat(data0A)
    stat1A = ImageStat.Stat(data1A)
    stat2A = ImageStat.Stat(data2A)
    stat3A = ImageStat.Stat(data3A)
    stat4A = ImageStat.Stat(data4A)
    print(int(stat0A.rms[0]), int(stat1A.rms[0]), int(stat2A.rms[0]), int(stat3A.rms[0]), int(stat4A.rms[0]))
    if (int(stat0A.rms[0]) > 30):  #> (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat1A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat2A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat3A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    return 0, int(stat4A.rms[0])

def col_test(fiol):
    q0Ax = 850 ; q0Ay = 850
    
    im = fiol[q0Ay:q0Ay+250, q0Ax:q0Ax+250]
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    
    lower = np.array([130,100,0])
    upper = np.array([180,255,255])
    
    # Threshold the HSV image to get only blue color
    mask = cv2.inRange(hsv, lower, upper)
    
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(im, im, mask=mask)
    res = cv2.medianBlur(res, 5)
    
    width, height, depth = res.shape
    maxValue = width * height * depth * 255
    imageValue = np.sum(res)
    m = interp1d([0,maxValue],[0,1])
    if (m(imageValue) > 0.05):
        print("FIOL:"+str(m(imageValue)))
        return 1
    else:
        print("FIOL:"+str(m(imageValue)))
        return 0


def tstasi178(im):
    q0Ax =  int(crop_x); q0Ay = int(crop_y)
    img0A = im.crop((q0Ax, q0Ay, q0Ax+int(crop_w), q0Ay+int(crop_h)))
    data0A = img0A.convert ('L')
    stat0A = ImageStat.Stat(data0A)
    #print(stat4A.rms[0])
    return 0, int(stat0A.rms[0]), img0A
    # badanie mniejszych fragmentow na razie nieaktywne, zrobie sprawdzanie pola w ktorym powinno byc Slonce/Ksiezyc
    '''
    q0Ax = 150 ; q0Ay = 0
    q1Ax = 150 ; q1Ay = 930
    q2Ax = 1100 ; q2Ay = 930
    q3Ax = 1100 ; q3Ay = 0
    q4Ax = 250 ; q4Ay = 100

    img0A = im.crop((q0Ax, q0Ay, q0Ax+30, q0Ay+30))
    img1A = im.crop((q1Ax, q1Ay, q1Ax+30, q1Ay+30))
    img2A = im.crop((q2Ax, q2Ay, q2Ax+30, q2Ay+30))
    img3A = im.crop((q3Ax, q3Ay, q3Ax+30, q3Ay+30))
    img4A = im.crop((q4Ax, q4Ay, q4Ax+750, q4Ay+750))

    data0A = img0A.convert ('L')
    data1A = img1A.convert ('L')
    data2A = img2A.convert ('L')
    data3A = img3A.convert ('L')
    data4A = img4A.convert ('L')
    stat0A = ImageStat.Stat(data0A)
    stat1A = ImageStat.Stat(data1A)
    stat2A = ImageStat.Stat(data2A)
    stat3A = ImageStat.Stat(data3A)
    stat4A = ImageStat.Stat(data4A)
    
    print(int(stat0A.rms[0]), int(stat1A.rms[0]), int(stat2A.rms[0]), int(stat3A.rms[0]), int(stat4A.rms[0]))
    if (int(stat0A.rms[0]) > 30):  #> (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat1A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat2A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    if (int(stat3A.rms[0]) > 30):  # > (int(stat0A.rms[0] + 10))):
        return 1, int(stat4A.rms[0])
    '''    

def cap(dataz, datay, flip):
    print("Capture start: ", dataz, datay)
    my_camera.configure(datay, dataz, 85, 65, 50, 50, flip, 1, [0, 0, 3096, 2080], 24, True, "picture" )
    arr = my_camera.capture()
    return arr

lasttest = 100
test2 = 100

def plotting_1(imagCropHD1, vs, vm, vju, vsa, vma, vve, aktual_t_f, licznik_1, test2, min_br, max_br):
    if int(overlay) == 1:
        #print("meh", overlay)
        plt = Figure(figsize=(10.80, 10.80))
        plt.patch.set_alpha(0)
        canvas = FigureCanvasAgg(plt)
        ax = plt.add_subplot(111, projection='polar')
        ax.patch.set_alpha(0)
        
        if os.path.isfile('/tmp/out.txt'):
            DataFileName='/tmp/out.txt'
            datafile=open(DataFileName, 'r')
            dataz=datafile.readlines()
            datafile.close()
        else:
            dataz=''

        if not dataz:
            last_time_fw = 'N/A'

        if int(iss_ovrl) == 1:
            iss=ephem.readtle(issline[0], issline[1], issline[2])
            iss.compute(gatech)

            iss_azis=[]
            iss_elevis=[]
            ISS_PREDICT=[-180,-150,-120,-90,-60,-30,0,30,60,90,120,150,180,210,240,270,300,330,360,390,420,450,480,510,540,570,600]
            #ISS_PREDICT=[-180,-120,-90,-60,-30,0,30,60,90,120,180,240,300,360,420,480,540,600]
            for i in ISS_PREDICT:
                d_t1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=i) #+ datetime.timedelta(minutes=470)
                gatech.date = ephem.Date(d_t1)
                iss.compute(gatech)
                iss_azis.append(iss.az)
                iss_elevis.append(90-(round(math.degrees(iss.alt),1)))
                #print iss.az,round(math.degrees(iss.alt),1)
            ax.plot(iss_azis,iss_elevis,'--',markersize=10, color='white', lw=1, alpha=0.6)
            #d_t0 = datetime.datetime.utcnow() #+ datetime.timedelta(minutes=470)
            #gatech.date = ephem.Date(d_t0)

            #print(math.degrees(iss.alt),math.degrees(iss.az))
            info = gatech.next_pass(iss)
            print("Rise time: %s azimuth: %s" % (info[0], info[1]))

            if iss.eclipsed:
                fontX = {'color':  "darkgray", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                vert_alX=str('bottom') ; hori_alX=str('left')
            else:
                fontX = {'color':  "white", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
                vert_alX=str('bottom') ; hori_alX=str('left')

            ax.plot(iss.az,90-(round(math.degrees(iss.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor=fontX['color'], alpha=1)
            #ax.text(iss.az,90-(round(math.degrees(iss.alt),1)), ' ISS', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=1)
            ax.text(iss.az,90-(round(math.degrees(iss.alt),1)), ' \n ISS \n '+str(int(iss.range)/1000)+'km', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX, alpha=0.3)
        
        gatech.date = ephem.now() #RESET!

        if int(stars_ovrl) == 1:
            lista_s=['Phecda','Dubhe','Castor','Pollux','Mizar','Betelgeuse','Altair','Vega','Rigel','Diphda','Sirius','Deneb','Arcturus','Capella','Hamal','Alcyone','Aldebaran','Alphecca','Menkalinan','Menkar','Polaris','Procyon','Deneb','Sadr']
            fontX1 = {'color':  "white", 'size': 8, 'weight': 'normal', 'family': 'monospace', }
            for star in lista_s:
                v = ephem.star(star)
                v.compute(gatech)
                ax.plot(np.radians(float(round(math.degrees(v.az), 1))),90-(round(math.degrees(v.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.05)
                ax.text(np.radians(float(round(math.degrees(v.az), 1))),90-(round(math.degrees(v.alt),1)), ' \n'+str(star)+' \n ', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX1, alpha=0.3)

        if int(test2) > 90: 
            #pfff_minmax:
            white_1 = 'black'
        else:
            white_1 = 'white'
        fontb = {'color':  white_1, 'size': 16, 'weight': 'bold', 'family': 'monospace', }
        font_c = {'color':  white_1, 'size': 16, 'weight': 'bold', 'family': 'monospace', }

        ax.plot(vs.az,90-(round(math.degrees(vs.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#000000', alpha=1)
        ax.text(vs.az,90-(round(math.degrees(vs.alt),1)), ' '+sols, verticalalignment='bottom', horizontalalignment='left', fontdict=font_c, alpha=0.6)

        ax.plot(vm.az,90-(round(math.degrees(vm.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor=white_1, alpha=0.3)
        ax.text(vm.az,90-(round(math.degrees(vm.alt),1)), ' '+luns, verticalalignment='bottom', horizontalalignment='left', fontdict=font_c, alpha=0.6)

        ax.plot(vju.az,90-(round(math.degrees(vju.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
        ax.text(vju.az,90-(round(math.degrees(vju.alt),1)), ' '+jups, verticalalignment='bottom', horizontalalignment='left', fontdict=fontb, alpha=0.6)

        ax.plot(vsa.az,90-(round(math.degrees(vsa.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
        ax.text(vsa.az,90-(round(math.degrees(vsa.alt),1)), ' '+sats, verticalalignment='bottom', horizontalalignment='left', fontdict=fontb, alpha=0.6)

        ax.plot(vma.az,90-(round(math.degrees(vma.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='red', alpha=0.3)
        ax.text(vma.az,90-(round(math.degrees(vma.alt),1)), ' '+mars, verticalalignment='bottom', horizontalalignment='left', fontdict=fontb, alpha=0.6)

        ax.plot(vve.az,90-(round(math.degrees(vve.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
        ax.text(vve.az,90-(round(math.degrees(vve.alt),1)), ' '+vens, verticalalignment='bottom', horizontalalignment='left', fontdict=fontb, alpha=0.6)
        
        if int(landmarks_ovrl) == 1:
            '''        
            orientacyjne= [
            [12,    1.5     ],
            [27,    1.5     ],
            [64,    1.2     ],
            [112,   5       ],
            [189,   5       ],
            [164,   12      ],
            [162,   6       ],
            [251,   6       ],
            [293,   1.5     ],
            [320,   1.5     ],
            [329,   6       ],
            [341,   8       ],
            [354,   7.5     ]]

            for i in orientacyjne:

                x,y = math.radians(i[0]),   90-i[1]
                x1,y1 = math.radians(i[0]), 90
                ax.plot(x,y,'o',markersize=5, markerfacecolor='none', markeredgecolor='yellow', alpha=0.3)
                ax.plot([x,x1],[y,y1],'-',markersize=15, lw=2,color='yellow', alpha=0.3)
            '''
            orientacyjne= [
            [112,   5       ]]

            for i in orientacyjne:
                x,y = math.radians(i[0]),   90-i[1]
                x1,y1 = math.radians(i[0]), 90
                ax.plot(x,y,'o',markersize=5, markerfacecolor='none', markeredgecolor='red', alpha=0.9)
                ax.plot([x,x1],[y,y1],'-',markersize=15, lw=2,color='red', alpha=0.3)
                #ax.text(x, y, 'Hello path effects world!', verticalalignment='bottom', horizontalalignment='left', fontdict=fontb, alpha=0.6)#, path_effects=[path_effects.withSimplePatchShadow()])
        

        for i,line in enumerate(dataz):
            aktual_t1x = datetime.datetime.now()
            #print line
            plane_dict = line.split(',')
            #print flight
            #print plane_dict[1]
            #print (plane_dict[pentry][3])
            flight=str(plane_dict[1].strip())
            if flight == '':
                flight = str(plane_dict[0].strip())
            if is_int_try(str(plane_dict[4].strip())):
                meters=int(str(plane_dict[4].strip()))
            elif is_float_try(str(plane_dict[4].strip())):
                meters=int(float(str(plane_dict[4].strip())))
            else:
                meters=10000

            distance=float(plane_dict[5].strip())

            if is_int_try(str(plane_dict[11].strip())):
                track=float(360-(270-int(str(plane_dict[11].strip()))))
            else:
                track = 0
            azi=np.radians(float(plane_dict[6].strip()))
            aaz=float(plane_dict[6].strip())
            elev=90-float(plane_dict[7].strip())
            elunc=90-float(plane_dict[7].strip())
            #kolorek=str(plane_dict[pentry][8])
            kolorek='#ff0000'
            dziewiec=str(plane_dict[9].strip())
            dwana=str(plane_dict[12].strip())
            '''pos_age = int(float(str(plane_dict[29].strip())))
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
            '''
            alpha_age = 0.8
            alpha_ageB = 0.8

            ##################### to bylo aktywne
            loSep = -10
            hiSep = 10
            #if not plane_dict[22].strip() == '':
            if is_float_try(str(plane_dict[20].strip())):
                dist2mo1 = str(plane_dict[19].strip())
                deg_missed1 = float(str(plane_dict[20].strip()))
                if (loSep < float(deg_missed1) < hiSep):
                        moon_s=dist2mo1+'km '+sols+' '+str(deg_missed1)+deg+' \n '
                else:
                        #moon_s='X n/a \n'
                        moon_s=''
                        #dist2mo+' o '+str(deg_missed)+deg+' \n '
            else:
                        deg_missed1 = ''
                        #moon_s= 'X -- \n'
                        moon_s= ''

            if is_float_try(str(plane_dict[24].strip())):
            #if not plane_dict[26].strip() == '':
                dist2mo2 = str(plane_dict[23].strip())
                deg_missed2 = float(str(plane_dict[24].strip()))
                if (loSep < float(deg_missed2) < hiSep):
                        sun_s=dist2mo2+'km '+luns+' '+str(deg_missed2)+deg+' \n '
                else:
                        #moon_s='X n/a \n'
                        sun_s=''
                        #dist2mo+' o '+str(deg_missed)+deg+' \n '
            else:
                        deg_missed2 = ''
                        #sun_s= 'X -- \n'
                        sun_s= ''

            ##################### to bylo aktywne

            #print flight,dziewiec, dwana

            #########################
            #
            # marker_style = dict(linestyle=':', color='0.8', markersize=10,mfc="C0", mec="C0")
            # marker_style.update(mec="None", markersize=15)
            # marker = "$[$"+" "+"$]$"
            # ax.plot(azi,elev, marker=marker, markersize=5, markerfacecolor='none', markeredgecolor=str(kolorek))
            #
            #########################

            if aaz >= 0 and aaz < 90:
                vert_al=str('top') ; hori_al=str('left')
            elif aaz >= 90 and aaz < 180:
                vert_al=str('bottom') ; hori_al=str('left')
            elif aaz >= 180 and aaz < 270:
                vert_al=str('bottom') ; hori_al=str('right')
            elif aaz >= 270:
                vert_al=str('top') ; hori_al=str('right')

            #fonta = {'color':  "black", 'size': 12, 'weight': 'light', 'family': 'monospace', }
            #fontb = {'color':  "black", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
            #fontc = {'color':  "black", 'size': 12, 'weight': 'heavy', 'family': 'monospace', }
            fonta = {'color':  "black", 'size': 12, 'weight': 'light', 'family': 'monospace', }
            fontb = {'color':  "black", 'size': 12, 'weight': 'bold', 'family': 'monospace', }
            fontc = {'color':  "black", 'size': 12, 'weight': 'heavy', 'family': 'monospace', }
            #fonta['color'] = 'kupa'
            #print fonta
            
            #pfff_minmax = (int(min_br) + int(max_br))/2
            if int(test2) > 90: 
                #pfff_minmax:
                white_1 = 'black'
            else:
                white_1 = 'white'
                

            if meters < 5000:
                #fonta['color'] = '#ff9900' ; fonta['size'] = '12'
                fonta['color'] = str(white_1) ; fonta['size'] = '12'
                fontb['color'] = '#ff9900' ; fonta['size'] = '12'
            elif (dwana == 'WARNING' and dziewiec != "RECEDING") and (meters >= 5000):
                #fonta['color'] = '#ff0000'
                fonta['color'] = str(white_1)
                fontb['color'] = '#ff0000'
            elif (dwana == 'WARNING' and dziewiec == "RECEDING") and (meters >= 5000):
                #fonta['color'] = '#660000'
                fonta['color'] = str(white_1)
                fontb['color'] = '#660000'
            elif (dwana != 'WARNING' and dziewiec == "RECEDING") and (meters >= 5000):
                #fonta['color'] = '#8000ff'
                fonta['color'] = str(white_1)
                fontb['color'] = '#8000ff'
            else:
                #fonta['color'] = '#ff00ff'
                fonta['color'] = str(white_1)
                fontb['color'] = '#ff00ff'

            #moon_s='aaa'
            if meters < 5000:
                fonta['size'] = '12'
                fontc['size'] = '12'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center',rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, ' \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, ' \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)

            elif (distance > 60) and (meters >= 5000):
                fonta['size'] = '10'
                fontc['size'] = '10'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 60) and distance > 40 and (meters >= 5000):
                fonta['size'] = '10'
                fontc['size'] = '10'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 40) and distance > 20 and (meters >= 5000):
                fonta['size'] = '11'
                fontc['size'] = '11'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 20) and (meters >= 5000):
                fonta['size'] = '11'
                fontc['size'] = '11'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            else:
                fonta['size'] = '12'
                fontc['size'] = '12'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.3)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n  '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n  '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)



            
            azis        = []
            elevis      = []
            alphis      = []
            #azis.append(azi)
            #elevis.append(elev)
            ############################## tranzyty
            if is_float_try(str(deg_missed1)):
             if (loSep < float(deg_missed1) < hiSep):

                fut_alt = str(plane_dict[22].strip())
                fut_az  =float( str(plane_dict[21].strip()))
                #print fut_az, fut_alt
                if not fut_az == 0:
                    object1 = str(plane_dict[27].strip())
                    if not object1  == '':
                        if object1 == 'Moon':
                            v1 = ephem.Moon(gatech)
                        elif object1 == 'Sun':
                            v1 = ephem.Sun(gatech)
                        elif object1 == 'Mars':
                            v1 = ephem.Mars(gatech)
                        elif object1 == 'Jupiter':
                            v1 = ephem.Jupiter(gatech)
                        elif object1 == 'Saturn':
                            v1 = ephem.Saturn(gatech)
                        else:
                            v1 = ephem.star(object1)
                            v1.compute(gatech)

                    tst_x=[v1.az, math.radians(float(fut_az)), azi]
                    tst_y=[90-(round(math.degrees(v1.alt),1)), 90-float(fut_alt), elunc]
                    ax.plot(tst_x,tst_y,'--',markersize=10, color='yellow', lw=1,alpha=0.3)

            if is_float_try(str(deg_missed2)):
             if (loSep < float(deg_missed2) < hiSep):

                fut_alt = str(plane_dict[26].strip())
                fut_az  =float( str(plane_dict[25].strip()))
                #print fut_az, fut_alt
                if not fut_az == 0:
                    object2 = str(plane_dict[28].strip())
                    if not object2  == '':
                        if object2 == 'Moon':
                            v2 = ephem.Moon(gatech)
                        elif object2 == 'Sun':
                            v2 = ephem.Sun(gatech)
                        elif object2 == 'Mars':
                            v2 = ephem.Mars(gatech)
                        elif object2 == 'Jupiter':
                            v2 = ephem.Jupiter(gatech)
                        elif object2 == 'Saturn':
                            v2 = ephem.Saturn(gatech)
                        else:
                            v2 = ephem.star(object2)
                            v2.compute(gatech)

                    tst_x=[v2.az, math.radians(float(fut_az)), azi]
                    tst_y=[90-(round(math.degrees(v2.alt),1)), 90-float(fut_alt), elunc]
                    ax.plot(tst_x,tst_y,'--',markersize=10, color='blue', lw=1,alpha=0.2)

                #    tst_x=[vma.az, azi]
                #    tst_y=[90-(round(math.degrees(vma.alt),1)), elunc]
                #ax.plot(tst_x,tst_y,'--',markersize=10, color='white', lw=1,alpha=0.8)
            ############################## tranzyty

            #'''
            if int(plot_trails) == 1:
                tmp_i = 0 
                if not plane_dict[15].strip() == '':
                    words1 = plane_dict[15]
                    words2 = plane_dict[16]
                    plane_pos1 = words1.split(';')
                    plane_pos2 = words2.split(';')
                    plane_pos_len = len(plane_pos1)
                    for i,word in enumerate(plane_pos1):
                        if not plane_pos1[i].strip() == '':

                            aaz1a=np.radians(float(plane_pos1[i].strip()))
                            ele1a=90-float(plane_pos2[i].strip())
                            azis.append(aaz1a)
                            elevis.append(ele1a)

                            if ((plane_pos_len-1) > i > 0):
                                #    #alpha_hist = 0.6
                                #else:
                                #alpha_hist = round(float(1.0/float(i/5.0)),2)

                                alpha_hist = round(1/float(plane_pos_len/float(i)),2)
                                if int(alhablend_trails) == 1:
                                    ax.plot((azis[i-1],azis[i]),(elevis[i-1], elevis[i]),'-',markersize=10, color=fontb['color'], lw=1, alpha=(alpha_hist/2))

                            else:
                                alpha_hist = 1
                            alphis.append(alpha_hist)    
                            tmp_i = i
                    #for i in
                    #ax.plot((azis[0],azis[tmp_i]),(elevis[0], elevis[tmp_i]),'-',markersize=10, color=fontb['color'], lw=1, alpha=0.3) # , alpha=(alphis[tmp_i]/2))            
                    if not int(alhablend_trails) == 1:
                        ax.plot((azis[0:tmp_i+1]),(elevis[0:tmp_i+1]),'-',markersize=10, color=fontb['color'], lw=1, alpha=0.3) # , alpha=(alphis[tmp_i]/2))            

            #'''                
            aktual_t2x = datetime.datetime.now()
            bbbbX = datetime.timedelta.total_seconds(aktual_t2x-aktual_t1x)
            #print(str(flight), str(bbbbX), str(tmp_i))    

        #datafile8=open(DataFileName8, 'r')
        #dataz8=datafile8.readlines()
        #datafile8.close()
        #offset1 = float(dataz8[0])

        ax.set_theta_zero_location('N', offset=float(theta_corr))
        #ax.set_theta_zero_location('N', offset=offset1)

        ax.set_rlim(0,90)
        if int(spines_ovrl) == 1:
            ax.spines['polar'].set_color('red')
            ax.spines['polar'].set_visible(True)
        ax.tick_params(axis='x', which='both', labelsize=10, labelcolor='white',color='none', direction='out')
        ax.set_yticklabels([])
        ax.grid(False)

        #plt.subplots_adjust(left=-0.01, bottom=0.01, right=1.03, top=1.0)
        plt.subplots_adjust(left=float(plot_adj_l), bottom=float(plot_adj_b), right=float(plot_adj_r), top=float(plot_adj_t))

        s, (width, height) = canvas.print_to_buffer()
        foreground = Image.frombytes("RGBA", (width, height), s)#,alpha=1)
        #return foreground
        #plotting_1(imagCropHD1, vs, vm, vju, vsa, vma, vve, aktual_t_f, x)
        imagCropHD1.paste(foreground, (0, 0), foreground)

    opencvImageHD = cv2.cvtColor(np.array(imagCropHD1), cv2.COLOR_RGB2BGR)
    im_nameHD = tmpfld+"/ASR.tmp/imageHD_"+aktual_t_f+str(licznik_1)+".jpg"
    dst_tmp = tmpfld+'/zwo_tmp.jpg'
    cv2.imwrite(dst_tmp, opencvImageHD, [int(cv2.IMWRITE_JPEG_QUALITY), int(q_resize)])
    dst = tmpfld+'/zwo_1080p.jpg'
    shutil.copy( dst_tmp, im_nameHD)
    shutil.move( dst_tmp, dst)
    



class AsyncWrite(threading.Thread):  
  
    def __init__(self, arr, aktual_t_f, exposure, gain): 

        # calling superclass init 
        threading.Thread.__init__(self)  
        self.exposure = exposure 
        self.gain = gain 
        self.arr = arr 
        #self.min_br = min_br 
        #self.max_br = max_br 
        self.aktual_t_f = aktual_t_f
        #self.out = out 

    def run(self):
     
        aktual_t1 = datetime.datetime.now()        
        gatech.date = ephem.now() #'2018/2/27 02:57:00'
        vs = ephem.Sun(gatech)
        vm = ephem.Moon(gatech)
        vju = ephem.Jupiter(gatech)
        vsa = ephem.Saturn(gatech)
        vma = ephem.Mars(gatech)
        vve = ephem.Venus(gatech)
        str_vs  = "Sol:  "+str('{:> 6.1f}'.format((  round(math.degrees(vs.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vs.az ), 1))))+deg
        str_vm  = "Lun:  "+str('{:> 6.1f}'.format((  round(math.degrees(vm.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vm.az ), 1))))+deg
        str_vju = "Jup:  "+str('{:> 6.1f}'.format((  round(math.degrees(vju.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vju.az), 1))))+deg
        str_vsa = "Sat:  "+str('{:> 6.1f}'.format((  round(math.degrees(vsa.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vsa.az), 1))))+deg
        str_vma = "Mar:  "+str('{:> 6.1f}'.format((  round(math.degrees(vma.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vma.az), 1))))+deg
        str_vve = "Ven:  "+str('{:> 6.1f}'.format((  round(math.degrees(vve.alt), 1))))+deg+" "+str('{:> 6.1f}'.format((  round(math.degrees(vve.az), 1))))+deg


        '''
        datafile0=open(DataFileName0, 'r')
        dataz0=datafile0.readlines()
        datafile0.close()
    
        datafile1=open(DataFileName1, 'r')
        dataz1=datafile1.readlines()
        datafile1.close()
        '''
        datafile2=open(DataFileName2, 'r')
        dataz2=datafile2.readlines()
        datafile2.close()

        datafile3=open(DataFileName3, 'r')
        dataz3=datafile3.readlines()
        datafile3.close()

        datafile4=open(DataFileName4, 'r')
        dataz4=datafile4.readlines()
        datafile4.close()
        
        datafile7=open(DataFileName7, 'r')
        dataz7=datafile7.readlines()
        datafile7.close()
        
        min_br = dataz3[0]
        max_br = dataz2[0]
        
        #im = Image.frombuffer('RGB', (3096, 2080), self.arr, 'raw', 'BGR', 0, 0)
        imcv = cv2.cvtColor(self.arr,cv2.COLOR_BGR2RGB)
        #imcv = cv2.cvtColor(self.arr,cv2.COLOR_BGR2RGB)
        #lasttest = test2

        test3 = col_test(imcv)
        if (test3 > 0):
            imcv = cv2.cvtColor(self.arr, cv2.COLOR_BGR2GRAY)	
            imcv = cv2.cvtColor(imcv, cv2.COLOR_GRAY2BGR)
        elif (int(dataz7[0]) == 1):    
            imcv = cv2.cvtColor(self.arr, cv2.COLOR_BGR2GRAY)	
            imcv = cv2.cvtColor(imcv, cv2.COLOR_GRAY2BGR)

        im = Image.fromarray(imcv)
        test, test2, crop = tstasi178(im)

        draw = ImageDraw.Draw(crop)
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 24)
        draw.text((30,10 ),"AllSky v10.20200211"                            ,(100,100,100),font=font)
        draw.text((30,35  ),self.aktual_t_f				    ,(125,125,125),font=font)
        draw.text((30,60),"Exp:  "+str(int(self.exposure))+uus                         ,(125,125,125),font=font)
        draw.text((30,85),"Gain: "+self.gain                                ,(125,125,125),font=font)

        draw.text((30,110),"Min:  "+min_br	                            ,(125,125,125),font=font)
        draw.text((30,135),"Bri:  "+str(test2)	                            ,(125,125,125),font=font)
        draw.text((30,160),"Max:  "+max_br	                            ,(125,125,125),font=font)
        draw.text((30,1790),str_vs                                          ,(125,125,125),font=font)
        draw.text((30,1815),str_vm                                          ,(125,125,125),font=font)
        draw.text((30,1840),str_vju                                         ,(125,125,125),font=font)
        draw.text((30,1865),str_vsa                                         ,(125,125,125),font=font)
        draw.text((30,1890),str_vma                                         ,(125,125,125),font=font)
        draw.text((30,1915),str_vve                                         ,(125,125,125),font=font)
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 28)
        draw.text((100,1790),sols   ,(125,125,125),font=font)
        draw.text((100,1815),luns   ,(125,125,125),font=font)
        draw.text((100,1840),jups   ,(125,125,125),font=font)
        draw.text((100,1865),sats   ,(125,125,125),font=font)
        draw.text((100,1890),mars   ,(125,125,125),font=font)
        draw.text((100,1915),vens   ,(125,125,125),font=font)
        
        
        
        
        ##################################################################################################################
        #im_name = tmpfld+"/ASI/image_"+self.aktual_t_f+".png"
        im_name = tmpfld+"/ASI/image_"+self.aktual_t_f+".jpg"
        crop.save(im_name,"JPEG", quality=int(q_fullsize))

        #im.save(im_name)
        #im.save(dst_tmp)
        #imcv = cv2.cvtColor(img_new1,cv2.COLOR_BGR2RGB)
        #imagBIG = Image.fromarray(imcv)
    
        #im = Image.fromarray(arr)
        #b, g, r = arr.split()
        #im = arr.convert("RGBA")
        #im = arr.merge("RGB", (r, g, b))
        #im = Image.fromarray(arr, mode='BGR')
        
        #message = "Geeksforgeeks"
        
        #cv2.imwrite(dst_tmp, crop, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        #src = im_name
        
        #os.symlink(dst_tmp, dst)z


        if (int(self.exposure) >= 30000000):
            step = 10000000
        elif (int(self.exposure) >= 15000000):
            step = 2500000
        elif (int(self.exposure) >= 10000000):
            step = 1000000
        elif (int(self.exposure) >= 5000000):
            step = 500000
        elif (int(self.exposure) > 1000000):
            step = 100000
        elif (int(self.exposure) >= 400000):
            step = 50000
        elif (int(self.exposure) >= 250000):
            step = 25000
        elif (int(self.exposure) >= 100000):
            step = 10000
        elif (int(self.exposure) >= 50000):
            step = 5000
        elif (int(self.exposure) >= 10000):
            step = 1000
        elif (int(self.exposure) >= 5000):
            step = 250
        elif (int(self.exposure) >= 1000):
            step = 100
        elif (int(self.exposure) >= 500):
            step = 25
        elif (int(self.exposure) >= 400):
            step = 10
        elif (int(self.exposure) >= 356):
            step = 5
        else:
            step = 0

    
        if (test2 > int(dataz2[0])):
            print("exp > max")
            if (int(self.exposure) > 5000000):
                print("exp > 5s")
                if (int(self.exposure) <= 60000000):
                    print("exp < 60s")
                    with open(DataFileName0,'w') as tsttxt:
                        newdataz = int(self.exposure)-int(step)
                        tsttxt.write(str(newdataz)+"\n")
                else:
                    print("exp > ~60s - setting to = 60000000"+uus)
                    with open(DataFileName0,'w') as tsttxt:
                        newdataz = 60000000
                        tsttxt.write(str(newdataz)+"\n")
                        
            elif (5000000 >= int(self.exposure) > 1000):
                if (int(self.gain) == 1):
                    print("cZ")
                    with open(DataFileName0,'w') as tsttxt:
                        newdataz = int(self.exposure)-int(step)
                        tsttxt.write(str(newdataz)+"\n")
                
                elif (int(self.gain) >= 11):
                    print("e")
                    with open(DataFileName1,'w') as tsttxt:
                        newdataz1 = int(self.gain) - 10
                        tsttxt.write(str(newdataz1)+"\n")              
                else:
                    print("zzzz1")
                        
            elif (1000 >= int(self.exposure) > 900):
                gain_down1(self.gain, 850)
                print("a9")
            elif (900 >= int(self.exposure) > 800):
                gain_down1(self.gain, 750)
                print("a8")                
            elif (800 >= int(self.exposure) > 700):
                gain_down1(self.gain, 650)
                print("a7")                
            elif (700 >= int(self.exposure) > 600):
                gain_down1(self.gain, 550)
                print("a6")                
            elif (600 >= int(self.exposure) > 500):
                gain_down1(self.gain, 450)
                print("a5")                
            elif (500 >= int(self.exposure) > 355):
                gain_down2(self.gain, 355)
                print("a5")                
                #elif (355 >= int(self.exposure) > 200):
                #print("exp > 356"+uus)
                #f (100 > int(self.gain) > 11):
                #   print("100 > gain > 11")
                #   with open(DataFileName1,'w') as tsttxt:
                #       newdataz1 = int(self.gain) - 10
                #       tsttxt.write(str(newdataz1)+"\n")
                #lse:
                #   print("else od 100 > gain > 11")
                #   with open(DataFileName0,'w') as tsttxt:
                #       newdataz = int(self.exposure)-int(step)
                #       tsttxt.write(str(newdataz)+"\n")
                '''
                elif(int(self.exposure) <= 356):
                    print("exp <= 356"+uus)
                    if (int(self.gain) == 1):
                        print("gain == 11")
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = 355
                            tsttxt.write(str(newdataz)+"\n")
                        with open(DataFileName1,'w') as tsttxt:
                            newdataz1 = 60
                            tsttxt.write(str(newdataz1)+"\n")
                    elif (11 <= int(self.gain) <= 60):
                        print("11 <= gain <= 60")
                        with open(DataFileName1,'w') as tsttxt:
                            newdataz1 = int(self.gain) - 10
                            tsttxt.write(str(newdataz1)+"\n")
                    else:
                        print("a1")    
                '''
            else:
                print("cX")
                #    if (int(self.gain) == 1):
                #if (int(self.gain) > 0):
                #    print("d")
                #    with open(DataFileName0,'w') as tsttxt:
                #        newdataz = int(self.exposure)-int(step)
                #        tsttxt.write(str(newdataz)+"\n")       

                #elif (int(self.gain) >= 11):
                #    print("e")
                #    with open(DataFileName1,'w') as tsttxt:
                #        newdataz1 = int(self.gain) - 10
                #        tsttxt.write(str(newdataz1)+"\n")   
        elif (test2 < int(dataz3[0])):
            if (int(self.exposure) < int(dataz4[0])):
                print("exp < min")
                #### 526 - 551
                #####686 - 711
                ##### 888 -911
                if (1000 < int(self.exposure) < 5000000):
                    #print("z0x")
                    #elif (int(self.exposure) > 356):
                    print("z1")
                    if ((int(self.exposure)+int(step)) > 60):
                        print("z2")
                        if (test2 < 10):
                            step = step * 10
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = int(self.exposure)+int(step)
                            tsttxt.write(str(newdataz)+"\n")

                elif (1000 >= int(self.exposure) > 900):
                    gain_up1(self.gain, 1050)
                    print("b9")
                elif (900 >= int(self.exposure) > 800):
                    gain_up1(self.gain, 950)
                    print("b8")                
                elif (800 >= int(self.exposure) > 700):
                    gain_up1(self.gain, 850)
                    print("b7")                
                elif (700 >= int(self.exposure) > 600):
                    gain_up1(self.gain, 750)
                    print("b6")                
                elif (600 >= int(self.exposure) > 500):
                    gain_up1(self.gain, 650)
                    print("b5")                
                elif (500 >= int(self.exposure) > 400):
                    gain_up1(self.gain, 550)
                    print("b5")                
                elif (400 >= int(self.exposure) > 355):
                    gain_up1(self.gain, 450)
                    print("b4")                
                elif(int(self.exposure) < 356):
                    print("x0b")
                    if (int(self.gain) >= 50):
                        print("x")
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = 356
                            tsttxt.write(str(newdataz)+"\n")
                        with open(DataFileName1,'w') as tsttxt:
                            newdataz1 = 1
                            tsttxt.write(str(newdataz1)+"\n")
                    elif (1 <= int(self.gain) <= 50):
                        print("x1")

                        with open(DataFileName1,'w') as tsttxt:
                            newdataz1 = int(self.gain) + 10
                            tsttxt.write(str(newdataz1)+"\n")

                else:
                    print("x2")
                    if (int(self.gain) <= 141):
                        with open(DataFileName1,'w') as tsttxt:
                            newdataz1 = int(self.gain) + 10
                            tsttxt.write(str(newdataz1)+"\n")	
                    else:
                        with open(DataFileName0,'w') as tsttxt:
                            newdataz = int(self.exposure)+int(step)
                            tsttxt.write(str(newdataz)+"\n")

        aktual_t2 = datetime.datetime.now()
        aaaa = datetime.timedelta.total_seconds(aktual_t2-aktual_t1)
        #print(aktual_t2, (aktual_t2-aktual_t1), aaaa, dataz[0], datay[0])
        print("Saved big: ", self.aktual_t_f, "Br:", test2, "Time: ", aaaa)
        
        if (int(self.exposure) < 10000000):
            aktual_t3 = datetime.datetime.now()
            imagCropHD = crop.resize((int(w_resize), int(h_resize)),Image.LANCZOS)
            plotting_1(imagCropHD, vs, vm, vju, vsa, vma, vve, self.aktual_t_f, 0, test2, min_br, max_br)
            aktual_t4 = datetime.datetime.now()
            aaaa1 = datetime.timedelta.total_seconds(aktual_t4-aktual_t3)
            print("Saved 0: ", self.aktual_t_f, "Br:", test2, "Time: ", aaaa1)
        else:
            #licznik_1 = int(int(self.exposure)/10000000) 
            licznik_2 = round(float(int(self.exposure)/10000000))
            if (int(self.exposure) < 15000000):
                licznik_3 = int(self.exposure)/2
            else:
                licznik_3 = int(self.exposure)/licznik_2
            for x in range(licznik_2):
                aktual_t3 = datetime.datetime.now()
                imagCropHD = crop.resize((int(w_resize), int(h_resize)),Image.LANCZOS)
                imagCropHD1 = imagCropHD
                plotting_1(imagCropHD1, vs, vm, vju, vsa, vma, vve, self.aktual_t_f, x, test2, min_br, max_br)
                aktual_t4 = datetime.datetime.now()
                aaaa1 = datetime.timedelta.total_seconds(aktual_t4-aktual_t3)

                print("Saved  "+str(x)+":", self.aktual_t_f, "Br:", test2, "Time: ", aaaa1)
                print("Sub sleep: "+str((licznik_3/1000000)-aaaa1))
                time.sleep((licznik_3/1000000)-aaaa1)    

def gain_down1(gainX, exposureX):
    #print("exp <= 356"+uus)
    if (int(gainX) == 1):
        print("a1a")    

        with open(DataFileName0,'w') as tsttxt:
            newdataz = exposureX
            tsttxt.write(str(newdataz)+"\n")
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = 17
            tsttxt.write(str(newdataz1)+"\n")
    elif (3 <= int(gainX) <= 17):
        print("a1b")    
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = int(gainX) - 2
            tsttxt.write(str(newdataz1)+"\n")
    else:
        print("a1c")    

def gain_down2(gainX, exposureX):
    #print("exp <= 356"+uus)
    if (int(gainX) == 1):
        print("a1a")    

        with open(DataFileName0,'w') as tsttxt:
            newdataz = exposureX
            tsttxt.write(str(newdataz)+"\n")
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = 17
            tsttxt.write(str(newdataz1)+"\n")
    elif (3 <= int(gainX) <= 60):
        print("a1b")    
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = int(gainX) - 2
            tsttxt.write(str(newdataz1)+"\n")
    else:
        print("a1c")    

def gain_up1(gainX, exposureX):
    #print("exp <= 356"+uus)
    if (int(gainX) == 17):
        print("b1a")    

        with open(DataFileName0,'w') as tsttxt:
            newdataz = exposureX
            tsttxt.write(str(newdataz)+"\n")
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = 1
            tsttxt.write(str(newdataz1)+"\n")
    elif (1 <= int(gainX) <= 15):
        print("b1b")    
        with open(DataFileName1,'w') as tsttxt:
            newdataz1 = int(gainX) + 2
            tsttxt.write(str(newdataz1)+"\n")
    else:
        print("b1c")    

def read_conf():
    global w_resize
    global h_resize
    global q_resize
    global q_fullsize
    global theta_corr
    global delay_between_captures
    global crop_x
    global crop_y
    global crop_w
    global crop_h
    global overlay
    global spines_ovrl
    global stars_ovrl
    global h_flip
    global v_flip
    global d_wb1
    global d_wb2
    global n_wb1
    global n_wb2
    global landmarks_ovrl
    global iss_ovrl
    global issline
    global plot_trails
    global alhablend_trails
    global plot_adj_l
    global plot_adj_b
    global plot_adj_r
    global plot_adj_t
    plot_adj_l       = ZWO_Conf.plot_adj_l
    plot_adj_b       = ZWO_Conf.plot_adj_b
    plot_adj_r       = ZWO_Conf.plot_adj_r
    plot_adj_t       = ZWO_Conf.plot_adj_t

    #global calibration1_ovrl
    #global calibration2_ovrl
    
    importlib.reload(ZWO_Conf)

    w_resize = ZWO_Conf.w_resize
    h_resize = ZWO_Conf.h_resize
    q_resize = ZWO_Conf.q_resize
    q_fullsize = ZWO_Conf.q_fullsize
    theta_corr  = ZWO_Conf.theta_corr
    #cam_azimuth  = ZWO_Conf.cam_azimuth
    delay_between_captures = ZWO_Conf.delay_between_captures

    crop_x = ZWO_Conf.crop_x
    crop_y = ZWO_Conf.crop_y
    crop_w = ZWO_Conf.crop_w
    crop_h = ZWO_Conf.crop_h

    overlay     = ZWO_Conf.overlay
    spines_ovrl = ZWO_Conf.spines_ovrl
    stars_ovrl  = ZWO_Conf.stars_ovrl
    h_flip      = ZWO_Conf.h_flip
    v_flip      = ZWO_Conf.v_flip
    # = ZWO_Conf.

    d_wb1       = ZWO_Conf.d_wb1
    d_wb2       = ZWO_Conf.d_wb2
    n_wb1       = ZWO_Conf.n_wb1
    n_wb2       = ZWO_Conf.n_wb2
    landmarks_ovrl = ZWO_Conf.landmarks_ovrl
    iss_ovrl = ZWO_Conf.iss_ovrl
    calibration1_ovrl = ZWO_Conf.calibration1_ovrl
    calibration2_ovrl = ZWO_Conf.calibration2_ovrl
    plot_trails = ZWO_Conf.plot_trails
    alhablend_trails = ZWO_Conf.alhablend_trails

    if iss_ovrl == "1":
        issline=[]
        tleFileName = ASR_Conf.TMP_FLDR+'/iss.tle'
        tlefile=open(tleFileName, 'r')
        tledata=tlefile.readlines()
        tlefile.close()

        for i, line in enumerate(tledata):
            if "ISS" in line: 
                for l in tledata[i:i+3]: issline.append(l.strip('\r\n').rstrip()),
#pfff = True
def Main(): 
    global w_resize
    global h_resize
    global q_resize
    global q_fullsize
    global theta_corr
    global delay_between_captures
    global crop_x
    global crop_y
    global crop_w
    global crop_h
    global overlay
    global spines_ovrl
    global stars_ovrl
    global h_flip
    global v_flip
    global d_wb1
    global d_wb2
    global n_wb1
    global n_wb2
    global landmarks_ovrl
    global iss_ovrl
    global issline
    global plot_trails
    global alhablend_trails
    global plot_adj_l
    global plot_adj_b
    global plot_adj_r
    global plot_adj_t

    #global calibration1_ovrl
    #global calibration2_ovrl
    #global pfff
    #global dataz
    #global datay

    datafile0=open(DataFileName0, 'r')
    dataz0=datafile0.readlines()
    datafile0.close()

    datafile1=open(DataFileName1, 'r')
    dataz1=datafile1.readlines()
    datafile1.close()

    while True:
        aktual_t1 = datetime.datetime.now()
        print(aktual_t1)
    
        datafile0=open(DataFileName0, 'r')
        dataz0=datafile0.readlines()
        datafile0.close()
    
        datafile1=open(DataFileName1, 'r')
        dataz1=datafile1.readlines()
        datafile1.close()

        datafile9B=open(DataFileName9B, 'r')
        dataz9B=datafile9B.readlines()
        datafile9B.close()
        
        if int(dataz9B[0]) == 1:
            with open(DataFileName9B,'w') as tsttxt:
                newdataz = 0
                tsttxt.write(str(newdataz)+"\n")
                print("break")
                exit()
                #pfff = False
        
        
        else:
            exposure = dataz0[0]
            gain = dataz1[0]

            aktual_t = datetime.datetime.now()
            aktual_t_f = aktual_t.strftime("%Y%m%d_%H%M%S")
            ##configure( _gain, _exposure, _wb_b, _wb_r, _gamma, _brightness, _flip, _bin, _roi, _drange=8, _color, _mode )
            # only both flips via h_flip atm 
            if (str(h_flip) == "1"):
                flip = 3
                #print(flip)
            else:
                flip = 0
                #print(flip)
            arr = cap(int(dataz0[0]), int(dataz1[0]), int(flip))

            background = AsyncWrite(arr, aktual_t_f, exposure, gain) 
            background.start()

            exposure2 = int(dataz0[0])/1000000 
            if (exposure2 < int(delay_between_captures)):    
               diff1 = int(delay_between_captures)-exposure2
               print("Diff: "+str(diff1)+"s")
               time.sleep(diff1)

if __name__=='__main__': 
    Main() 

    
