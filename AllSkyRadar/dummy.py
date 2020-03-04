import threading
import time
import math
import datetime
#from skycam import SkyCam
#import cv2
from PIL import Image, ImageStat, ImageFont, ImageDraw,ImageColor
import shutil
import os, errno
#import cv2
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import ephem
#from scipy.interpolate import interp1d
import ASR_Conf
import Dummy_Conf

my_lat = ASR_Conf.MY_LAT
my_lon = ASR_Conf.MY_LON
my_alt = ASR_Conf.MY_ALT

tmpfld = ASR_Conf.TMP_FLDR
miscfld = ASR_Conf.MISC_FLDR
tleFileName = ASR_Conf.TMP_FLDR+'/iss.tle'

# = Dummy_Conf.
w_resize = Dummy_Conf.w_resize
h_resize = Dummy_Conf.h_resize
q_resize = Dummy_Conf.q_resize
#q_fullsize = Dummy_Conf.q_fullsize

#tmpconf8 atm
theta_corr  = Dummy_Conf.theta_corr
delay_between_captures = Dummy_Conf.delay_between_captures

#crop_x = Dummy_Conf.crop_x
#crop_y = Dummy_Conf.crop_y
#crop_w = Dummy_Conf.crop_w
#crop_h = Dummy_Conf.crop_h

overlay     = Dummy_Conf.overlay
spines_ovrl = Dummy_Conf.spines_ovrl
stars_ovrl  = Dummy_Conf.stars_ovrl
bg_color = Dummy_Conf.bg_color

plot_adj_l       = Dummy_Conf.plot_adj_l
plot_adj_b       = Dummy_Conf.plot_adj_b
plot_adj_r       = Dummy_Conf.plot_adj_r
plot_adj_t       = Dummy_Conf.plot_adj_t



landmarks_ovrl = Dummy_Conf.landmarks_ovrl
iss_ovrl = Dummy_Conf.iss_ovrl
#calibration1_ovrl = Dummy_Conf.calibration1_ovrl
#calibration2_ovrl = Dummy_Conf.calibration2_ovrl
plot_trails = Dummy_Conf.plot_trails
alhablend_trails = Dummy_Conf.alhablend_trails


DataFileName9D = tmpfld+"/tmpconf9D"

issline=[]
#tleFileName='/tmp/iss.tle'
tlefile=open(tleFileName, 'r')
tledata=tlefile.readlines()
tlefile.close()
for i, line in enumerate(tledata):
    if "ISS" in line:
        for l in tledata[i:i+3]: issline.append(l.strip('\r\n').rstrip()),



#try:

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



def plotting_1(imagCropHD1, vs, vm, vju, vsa, vma, vve, aktual_t_f):
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
                ax.plot(np.radians(float(round(math.degrees(v.az), 1))),90-(round(math.degrees(v.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor='#ffffff', alpha=0.3)
                ax.text(np.radians(float(round(math.degrees(v.az), 1))),90-(round(math.degrees(v.alt),1)), ' \n'+str(star)+' \n ', verticalalignment=vert_alX, horizontalalignment=hori_alX, fontdict=fontX1, alpha=0.3)

        #if int(test2) > 90: 
        #    #pfff_minmax:
        #    white_1 = 'black'
        #else:
        white_1 = 'white'
        fontb = {'color':  white_1, 'size': 16, 'weight': 'bold', 'family': 'monospace', }
        font_c = {'color':  white_1, 'size': 16, 'weight': 'bold', 'family': 'monospace', }

        ax.plot(vs.az,90-(round(math.degrees(vs.alt),1)),'o',markersize=15, markerfacecolor='none', markeredgecolor=white_1, alpha=1)
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
            #if int(test2) > 90: 
            #    #pfff_minmax:
            #    white_1 = 'black'
            #else:
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
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.6)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center',rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, ' \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, ' \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)

            elif (distance > 60) and (meters >= 5000):
                fonta['size'] = '10'
                fontc['size'] = '10'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.5)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 60) and distance > 40 and (meters >= 5000):
                fonta['size'] = '10'
                fontc['size'] = '10'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.6)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 40) and distance > 20 and (meters >= 5000):
                fonta['size'] = '11'
                fontc['size'] = '11'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.6)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            elif (distance <= 20) and (meters >= 5000):
                fonta['size'] = '11'
                fontc['size'] = '11'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.6)
                ax.text(azi,elunc, '    ---', verticalalignment='center', horizontalalignment='center', rotation=track,fontdict=fontb, alpha=0.6)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fontc, alpha=alpha_ageB)
                ax.text(azi,elunc, '  \n '+str(flight)+' \n '+str(meters)+'m'+' \n '+str(distance)+'km \n '+moon_s+sun_s, verticalalignment=vert_al, horizontalalignment=hori_al, fontdict=fonta, alpha=alpha_age)
            else:
                fonta['size'] = '12'
                fontc['size'] = '12'
                ax.plot(azi,elunc,'o',markersize=15, markerfacecolor='none', markeredgecolor=fontb['color'], alpha=0.6)
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
                    ax.plot(tst_x,tst_y,'--',markersize=10, color='yellow', lw=1,alpha=0.4)

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
                    ax.plot(tst_x,tst_y,'--',markersize=10, color='blue', lw=1,alpha=0.4)

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
                        ax.plot((azis[0:tmp_i+1]),(elevis[0:tmp_i+1]),'-',markersize=10, color=fontb['color'], lw=1, alpha=0.5) # , alpha=(alphis[tmp_i]/2))            

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


    #opencvImageHD = cv2.cvtColor(np.array(imagCropHD1), cv2.COLOR_RGB2BGR)
    dst_tmp = tmpfld+'/dummy_tmp.jpg'
    #cv2.imwrite(dst_tmp, opencvImageHD, [int(cv2.IMWRITE_JPEG_QUALITY), int(q_resize)])

    #opencvImageHD = Image.fromarray(imagCropHD1)
    imagCropHD1.save(dst_tmp,"JPEG", quality=int(q_resize))
    
    #im_nameHD = tmpfld+"/dummy.tmp/imageHD_"+aktual_t_f+str(licznik_1)+".jpg"
    dst = tmpfld+'/dummy_1080p.jpg'
    #shutil.copy( dst_tmp, im_nameHD)
    shutil.move( dst_tmp, dst)
    



class AsyncWrite(threading.Thread):  
  
    def __init__(self, aktual_t_f):

        # calling superclass init 
        threading.Thread.__init__(self)  
        #self.exposure = exposure 
        #self.gain = gain 
        #self.arr = arr 
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

        imagCrop = Image.new('RGB', (1080, 1080), color = str(bg_color))
        #imagCrop = Image.new('RGB', (2240, 2240), color = '#262626')
        #imagCrop = Image.new('RGB', (1080, 1080), color = '#262626')
        #imagCrop = Image.new('RGB', (1080, 1080), color = '#9fa69b')
        
        draw = ImageDraw.Draw(imagCrop)
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 15)
        #draw.text((30,5  ),metar.strip(' ')                                                        ,(125,125,125),font=font)
        draw.text((20,5 ),"AllSkyRadar a0.2 - Dummy"                                                ,(100,100,100),font=font)

        draw.text((20,25),"tt: "+self.aktual_t_f                           ,(255,255,0),font=font)

        draw.text((20,980 ),str_vs                                          ,(125,125,125),font=font)
        draw.text((20,995 ),str_vm                                          ,(125,125,125),font=font)
        draw.text((20,1010 ),str_vju                                        ,(125,125,125),font=font)
        draw.text((20,1025 ),str_vsa                                        ,(125,125,125),font=font)
        draw.text((20,1040 ),str_vma                                        ,(125,125,125),font=font)
        draw.text((20,1055),str_vve                                        ,(125,125,125),font=font)
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 17)
        draw.text((60,980 ),sols    ,(125,125,125),font=font)
        draw.text((60,995 ),luns    ,(125,125,125),font=font)
        draw.text((60,1010 ),jups   ,(125,125,125),font=font)
        draw.text((60,1025 ),sats   ,(125,125,125),font=font)
        draw.text((60,1040 ),mars   ,(125,125,125),font=font)
        draw.text((60,1055),vens   ,(125,125,125),font=font)

        aktual_t3 = datetime.datetime.now()
        imagCropHD = imagCrop
        plotting_1(imagCropHD, vs, vm, vju, vsa, vma, vve, self.aktual_t_f)
        aktual_t4 = datetime.datetime.now()
        aaaa1 = datetime.timedelta.total_seconds(aktual_t4-aktual_t3)
        print("Saved 0: ", self.aktual_t_f, "Time: ", aaaa1)


def read_conf():
    global w_resize
    global h_resize
    global q_resize
    #global q_fullsize
    global theta_corr
    global delay_between_captures
    global crop_x
    global crop_y
    global crop_w
    global crop_h
    global overlay
    global spines_ovrl
    global stars_ovrl
    #global h_flip
    #global v_flip
    #global d_wb1
    #global d_wb2
    #global n_wb1
    #global n_wb2
    global landmarks_ovrl
    global iss_ovrl
    global issline
    global plot_trails
    global alhablend_trails
    global plot_adj_l
    global plot_adj_b
    global plot_adj_r
    global plot_adj_t
    global bg_color
    bg_color = Dummy_Conf.bg_color
    plot_adj_l       = Dummy_Conf.plot_adj_l
    plot_adj_b       = Dummy_Conf.plot_adj_b
    plot_adj_r       = Dummy_Conf.plot_adj_r
    plot_adj_t       = Dummy_Conf.plot_adj_t

    #global calibration1_ovrl
    #global calibration2_ovrl
    
    importlib.reload(Dummy_Conf)

    w_resize = Dummy_Conf.w_resize
    h_resize = Dummy_Conf.h_resize
    q_resize = Dummy_Conf.q_resize
    #q_fullsize = Dummy_Conf.q_fullsize
    theta_corr  = Dummy_Conf.theta_corr
    #cam_azimuth  = Dummy_Conf.cam_azimuth
    delay_between_captures = Dummy_Conf.delay_between_captures

    crop_x = Dummy_Conf.crop_x
    crop_y = Dummy_Conf.crop_y
    crop_w = Dummy_Conf.crop_w
    crop_h = Dummy_Conf.crop_h

    overlay     = Dummy_Conf.overlay
    spines_ovrl = Dummy_Conf.spines_ovrl
    stars_ovrl  = Dummy_Conf.stars_ovrl
    #h_flip      = Dummy_Conf.h_flip
    #v_flip      = Dummy_Conf.v_flip
    # = Dummy_Conf.

    #d_wb1       = Dummy_Conf.d_wb1
    #d_wb2       = Dummy_Conf.d_wb2
    #n_wb1       = Dummy_Conf.n_wb1
    #n_wb2       = Dummy_Conf.n_wb2
    landmarks_ovrl = Dummy_Conf.landmarks_ovrl
    iss_ovrl = Dummy_Conf.iss_ovrl
    calibration1_ovrl = Dummy_Conf.calibration1_ovrl
    calibration2_ovrl = Dummy_Conf.calibration2_ovrl
    plot_trails = Dummy_Conf.plot_trails
    alhablend_trails = Dummy_Conf.alhablend_trails

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
    #global q_fullsize
    global theta_corr
    global delay_between_captures
    global crop_x
    global crop_y
    global crop_w
    global crop_h
    global overlay
    global spines_ovrl
    global stars_ovrl
    #global h_flip
    #global v_flip
    #global d_wb1
    #global d_wb2
    #global n_wb1
    #global n_wb2
    global landmarks_ovrl
    global iss_ovrl
    global issline
    global plot_trails
    global alhablend_trails
    global plot_adj_l
    global plot_adj_b
    global plot_adj_r
    global plot_adj_t
    global bg_color
    #plot_adj_l       = Dummy_Conf.plot_adj_l
    #plot_adj_b       = Dummy_Conf.plot_adj_b
    #plot_adj_r       = Dummy_Conf.plot_adj_r
    #plot_adj_t       = Dummy_Conf.plot_adj_t
    #global calibration1_ovrl
    #global calibration2_ovrl
    #global pfff
    #global dataz
    #global datay
    with open(DataFileName9D,'w') as tsttxt:
        newdataz = 0
        tsttxt.write(str(newdataz)+"\n")

    while True:
        aktual_t1 = datetime.datetime.now()
        print(aktual_t1)

        datafile9D=open(DataFileName9D, 'r')
        dataz9D=datafile9D.readlines()
        datafile9D.close()

        if int(dataz9D[0]) == 1:
            with open(DataFileName9D,'w') as tsttxt:
                newdataz = 0
                tsttxt.write(str(newdataz)+"\n")
                print("break")
                exit()
                #pfff = False
        else:
            aktual_t = datetime.datetime.now()
            aktual_t_f = aktual_t.strftime("%Y%m%d_%H%M%S")

            background = AsyncWrite(aktual_t_f)
            background.start()

            time.sleep(int(delay_between_captures))

if __name__=='__main__': 
    Main() 
    
