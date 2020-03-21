#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
=======================================================================
Original idea: https://github.com/darethehair/flight-warning
=======================================================================
flight_warning.py
v3.20200320 (web)

=======================================================================
Changes:
=======================================================================
v3.20200320 (web)
- interactive html table - higlighted flight in table will be highlighted in allskyradar/dummy

v3.20200314 (web)
- json conf (same folder atm, ready for gui configuration panel)
- countdown js corrections

v3.20200311 (web)
- web table
- countdown to transits if wav/mp3 files provided (see filenames in code)


v0.2
- try/except for aircraft lat/lon in MSG 3

v0.1
- Color console realtime display Az/Alt
- Sun/Moon transits prediction

<aleksander5416@gmail.com>

=======================================================================
=======================================================================

Copyright (C) 2015 Darren Enns <darethehair@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA.
"""

#
# import required libraries
#
import os
import sys
import datetime
import time
import math
import ephem
import re
from math import atan2, sin, cos, acos, radians, degrees, atan, asin, sqrt, isnan
#import flight_warning_Conf
import json

#import flight_warning_Pressure
deg = u'\xb0'
uus = u'\xb5s'

jups = u"\u2643"
mars = u"\u2642"
vens = u"\u2640"
sats = u"\u2644"
sols = u"\u2609"
luns = u"\u263d"

deg_html = '&#xb0'
uus_html = '&#xb5s'

jups_html = "&#x2643"
mars_html = "&#x2642"
vens_html = "&#x2640"
sats_html = "&#x2644"
sols_html = "&#x2609"
luns_html = "&#x263d"

with open('/etc/raspap/location_settings.json') as f:
    LOCATION_CONF = json.load(f)

with open('/etc/raspap/fw_settings.json') as f:
    FW_CONF = json.load(f)

#for i  key, value in enumerate(data.items()):
#    print(key, value)
#time.sleep(2.5)

#exit()
last_sekundy = -1
int_counter_1 = 0
int_counter_2 = 0
int_counter_3 = 0
int_counter_4 = 0

footer=''
if os.name == 'nt':
    print(os.name)
    os.system('color')
    os.system('mode con: cols=160 lines=13')
    metar_active = int(FW_CONF['metar_active'])
    metar_path = str(FW_CONF['metar_path']) # windows \\ in path should work

    out_path = str(FW_CONF['out_path']) # windows \\ in path should work
    out_path_html = str(FW_CONF['out_path_html']) # windows \\ in path should work
    out_path_html_snd = str(FW_CONF['out_path_html_snd']) # windows \\ in path should work
else:
    print(os.name)
    metar_active = int(FW_CONF['metar_active'])
    metar_path = str(FW_CONF['metar_path'])

    out_path = str(FW_CONF['out_path'])
    out_path_html = str(FW_CONF['out_path_html']) # windows \\ in path should work
    out_path_html_snd = str(FW_CONF['out_path_html_snd']) # windows \\ in path should work

    #out_path = '/tmp/out.txt'


ignore_pressure = int(FW_CONF['ignore_pressure'])
ignore_my_elevation = int(FW_CONF['ignore_my_elevation'])

my_lat = float(LOCATION_CONF['MY_LAT'])
my_lon = float(LOCATION_CONF['MY_LON'])
my_alt = int(LOCATION_CONF['MY_ALT'])

time_corr = int(FW_CONF['time_corr'])
minutes_add = int(FW_CONF['minutes_add'])

time_corr_mlat = int(FW_CONF['time_corr_mlat'])
minutes_add_mlat = int(FW_CONF['time_corr_mlat'])

time_corr_ephem = int(FW_CONF['time_corr_ephem'])
minutes_add_ephem = int(FW_CONF['time_corr_ephem'])

gen_html = int(FW_CONF['gen_html'])
gen_html_snd = int(FW_CONF['gen_html_snd'])

gen_term = int(FW_CONF['gen_term'])

sel_obj_A = str(FW_CONF['sel_obj_A'])
sel_obj_B = str(FW_CONF['sel_obj_B'])


print( "Starting...")
started = datetime.datetime.now()


#deg = u'\xb0'
earth_R = 6371
#sols = u"\u2609"
#luns = u"\u263d"

#TERMINAL COLORS
REDALERT        = '\x1b[1;37;41m'
PURPLE          = '\x1b[1;35;40m'
PURPLEDARK      = '\x1b[0;35;40m'
RED             = '\x1b[0;31;40m' 
GREEN           = '\x1b[0;30;42m' 
GREENALERT      = '\x1b[0;30;42m' 
# GREENFG       = '\x1b[0;42;40m' 
GREENFG         = '\x1b[1;32;40m' 
BLUE            = '\x1b[1;34;40m'
YELLOW          = '\x1b[1;33;40m'
CYAN            = '\x1b[1;36;40m'
RESET           = '\x1b[0m' 
CLEARSCREEN     = '\033c'
#
# initialize empty dictionaries
#
plane_dict = {}


# 
# set desired units
#
metric_units = True # inactive

aktual_t = datetime.datetime.now()
last_t = datetime.datetime.now() - datetime.timedelta(seconds=10)
last_t_terminal = datetime.datetime.now() - datetime.timedelta(seconds=10)

metar_t = datetime.datetime.now() - datetime.timedelta(minutes=20)
gong_t = datetime.datetime.now()
#
# set desired distance and time limits
#

warning_distance                 = int(FW_CONF['warning_distance'])
alert_duplicate_minutes          = int(FW_CONF['alert_duplicate_minutes'])
alert_distance                   = int(FW_CONF['alert_distance'])
xtd_tst                          = int(FW_CONF['xtd_tst'])

transit_separation_sound_alert = float(FW_CONF['transit_separation_sound_alert'])
transit_separation_REDALERT_FG   = int(FW_CONF['transit_separation_REDALERT_FG'])
transit_separation_GREENALERT_FG = int(FW_CONF['transit_separation_GREENALERT_FG'])
transit_separation_notignored    = int(FW_CONF['transit_separation_notignored'])

transit_history_log              = int(FW_CONF['transit_history_log'])
transit_history_log_path         = str(FW_CONF['transit_history_log_path'])

heatmap_latlon_log               = int(FW_CONF['heatmap_latlon_log'])
heatmap_latlon_log_path          = str(FW_CONF['heatmap_latlon_log_path'])

sun_tr_sound                     = int(FW_CONF['sun_tr_sound'])
moon_tr_sound                    = int(FW_CONF['moon_tr_sound'])

terminal_beeps                   = int(FW_CONF['terminal_beeps'])
entering_sound                   = int(FW_CONF['entering_sound'])
detected_sound                   = int(FW_CONF['detected_sound'])
min_t_sound                      = float(FW_CONF['min_t_sound'])

display_limit = int(FW_CONF['display_limit'])
minimum_alt_transits= int(FW_CONF['minimum_alt_transits']) 
#pressure = 1013
pressure = int(FW_CONF['pressure'])

#
# set geographic location and elevation
#
my_elevation_const = my_alt # why                    #yourantennaelevation
my_elevation = my_alt       # why                     #yourantennaelevation
near_airport_elevation = int(FW_CONF['near_airport_elevation'])


gatech = ephem.Observer()

gatech.lat, gatech.lon = str(my_lat), str(my_lon)
gatech.elevation = my_elevation_const # get rid of this _const use conf 

#
# calculate time zone for ISO date/timestamp ???????????
#
timezone_hours = time.altzone/60/60

#
# define havesine great-circle-distance routine
# credit: http://www.movable-type.co.uk/scripts/latlong.html
#
def haversine(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination

    if (metric_units):
        radius = 6371 # km
    else:
        radius = 3959 # miles

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(radians(lat1)) * math.cos(radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = float(radius * c)

    return d

#
# define cross-track error routine
# credit: http://www.movable-type.co.uk/scripts/latlong.html
#
def crosstrack(distance, azimuth, track):
    if (metric_units):
        radius = 6371 # km
    else:
        radius = 3959 # miles

    xtd = round(abs(math.asin(math.sin(float(distance)/radius) * math.sin(radians(float(azimuth) - float(track)))) * radius),1)

    return xtd


#
# przeciecie azymutu slonca/ksiezyca z torem lotu
# credit: http://www.movable-type.co.uk/scripts/latlong.html
#
def transit_pred(obs2moon, plane_pos, track, velocity, elevation, obj_alt, obj_az):

    if obj_alt < 0.1:
        return 0
    lat1, lon1 = obs2moon
    lat2, lon2 = plane_pos
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    theta_13 = radians(float(obj_az))
    theta_23 = radians(float(track))
    Dlat = lat1-lat2
    Dlon = lon1-lon2
    delta_12 =  2*asin( sqrt( sin(Dlat/2)*sin(Dlat/2) + \
    cos(lat1)*cos(lat2)*sin(Dlon/2)*sin(Dlon/2) ) )
    if (float(delta_12 == 0)):
        return 0 
    theta_a = acos( ( sin(lat2) - sin(lat1)*cos(delta_12) ) / ( sin(delta_12)*cos(lat1) ) )
    if (isnan(theta_a)):
        theta_a = 0
    theta_b = acos( ( sin(lat1) - sin(lat2)*cos(delta_12) ) / ( sin(delta_12)*cos(lat2) ) )
    if sin(lon2-lon1) > 0:
        theta_12 = theta_a
        theta_21 = 2*math.pi - theta_b
    else:
        theta_12 = 2*math.pi - theta_a
        theta_21 = theta_b
    
    alfa_1 = theta_13 - theta_12
    alfa_2 = theta_21 - theta_23

    if (sin(alfa_1) == 0) and (sin(alfa_2) == 0):
        return 0 #null
    if ((sin(alfa_1))*(sin(alfa_2)) < 0):
        return 0 #null
    
    alfa_3 = acos( -cos(alfa_1)*cos(alfa_2) + sin(alfa_1)*sin(alfa_2)*cos(delta_12) )
    delta_13 = atan2( sin(delta_12)*sin(alfa_1)*sin(alfa_2), cos(alfa_2)+cos(alfa_1)*cos(alfa_3) )
    lat3 = asin( sin(lat1)*cos(delta_13) + cos(lat1)*sin(delta_13)*cos(theta_13) )
    Dlon_13 = atan2( sin(theta_13)*sin(delta_13)*cos(lat1), cos(delta_13)-sin(lat1)*sin(lat3) )
    lon3 = lon1 + Dlon_13;

    lat3 = degrees(lat3)
    lon3 = (degrees(lon3)+540)%360-180
    ## the distance from the observer's position to the calculated position of the aircraft when it crosses the azimuth of the moon
    dst_h2x = round(haversine((my_lat, my_lon), (lat3, lon3)),1)    
    if dst_h2x > 500:
        return 0
    if dst_h2x == 0:
        dst_h2x = 0.001
    ## tu test wysokosci na metrach nie ft    
    # if elevation < 2166:
        # my_elevation = 0 ## taka sama wysokoĹ›Ä‡ punktu obserwacji n.p.m jak pas na EPPO
    # else:
        # my_elevation = my_elevation_const
    if not is_int_try(elevation):
        return 0
    # wtf again my_elevation again?!? corr? was it virt-in-future position???
    #altitude1 = degrees(atan(int(elevation - my_elevation)/(dst_h2x*1000)))
    altitude1 = degrees(atan(int(elevation)/(dst_h2x*1000)))

    azimuth1 = atan2(sin(radians(lon3-my_lon)) * cos(radians(lat3)),  cos(radians(my_lat)) * sin(radians(lat3)) - sin(radians(my_lat))*cos(radians(lat3))*cos(radians(lon3-my_lon)))
    azimuth1 = round(((degrees(azimuth1) + 360) % 360),1)

    ## the distance from the CURRENT position of the airplane to the calculated position of the aircraft when it CROSSES the azimuth of the moon
    dst_p2x = round(haversine((plane_pos[0], plane_pos[1]), (lat3, lon3)),1) 
    if not velocity == '':
        velocity = int(velocity)
    else:
        velocity = 900 # only used for transit countdown
    delta_time = (dst_p2x / velocity)*3600

    obj_alt_B = 90.00 - obj_alt
    ideal_dist = (sin(radians(obj_alt_B))*elevation) / sin(radians(obj_alt)) / 1000
    ideal_lat = asin((sin(radians(my_lat)) * cos(ideal_dist/earth_R)) + (cos(radians(my_lat)) * sin(ideal_dist/earth_R) * cos(radians(obj_az))))
    ideal_lon = radians(my_lon) + atan2((sin(radians(obj_az))*sin(ideal_dist/earth_R)*cos(radians(my_lat))), (cos(ideal_dist/earth_R)-((sin(radians(my_lat))) * sin(ideal_lat))))

    ideal_lat = degrees(ideal_lat)
    ideal_lon = degrees(ideal_lon)
    ideal_lon = (ideal_lon+540)%360-180

    return  lat3, lon3, azimuth1, altitude1, dst_h2x, dst_p2x, delta_time, 0, obj_az, obj_alt
    ##        0        1        2        3            4        5        6           7    8        9


def dist_col(distance):
    if (distance <= 300 and distance > 100):
        return PURPLE
    elif (distance <= 100 and distance > 50):
        return CYAN
    elif (distance <= 50 and distance > 30):
        return YELLOW
    elif (distance <= 30 and distance > 15):
        return REDALERT
    elif (distance <= 15 and distance >0):
        return GREENALERT
    else:
        return PURPLEDARK

def alt_col(altitude):
    if (altitude >= 5 and altitude < 15):
        return PURPLE
    elif (altitude >= 15 and altitude < 25):
        return CYAN
    elif (altitude >= 25 and altitude < 30):
        return YELLOW
    elif (altitude >= 30 and altitude < 35):
        return REDALERT
    elif (altitude >=35 and altitude <= 90):
        return GREEN
    else:
        return PURPLEDARK

def elev_col(elevation):
    if (elevation >= 4000 and elevation <= 8000):
        return PURPLE
    elif (elevation >= 2000 and elevation < 4000):
        return GREEN
    elif (elevation > 0 and elevation < 2000):
        return YELLOW
    else:
        return RESET    


def dist_col_2(distance):
    if (distance <= 300 and distance > 100):
        return ' class="ptext"'
    elif (distance <= 100 and distance > 50):
        return ' class="ctext"'
    elif (distance <= 50 and distance > 30):
        return ' class="ytext"'
    elif (distance <= 30 and distance > 15):
        return ' class="rrtext"'
    elif (distance <= 15 and distance >0):
        return ' class="ggtext"'
    else:
        return ' class="dptext"'


def alt_col_2(altitude):
    if (altitude >= 5 and altitude < 15):
        return ' class="ptext"'
    elif (altitude >= 15 and altitude < 25):
        return ' class="ctext"'
    elif (altitude >= 25 and altitude < 30):
        return ' class="ytext"'
    elif (altitude >= 30 and altitude < 35):
        return ' class="rrtext"'
    elif (altitude >=35 and altitude <= 90):
        return ' class="ggtext"'
    else:
        return ' class="dptext"'


def elev_col_2(elevation):
    if (4000 <= elevation <= 8000):
        return ' class="ctext"'
    elif (2000 >= elevation < 4000):
        return ' class="gtext"'
    elif (0 > elevation < 2000):
        return ' class="ytext"'
    else:
        return ' class="ptext"'
    
def wind_deg_to_str1(deg):
        if   deg >=  11.25 and deg <  33.75: return 'NNE'
        elif deg >=  33.75 and deg <  56.25: return 'NE'
        elif deg >=  56.25 and deg <  78.75: return 'ENE'
        elif deg >=  78.75 and deg < 101.25: return 'E'
        elif deg >= 101.25 and deg < 123.75: return 'ESE'
        elif deg >= 123.75 and deg < 146.25: return 'SE'
        elif deg >= 146.25 and deg < 168.75: return 'SSE'
        elif deg >= 168.75 and deg < 191.25: return 'S'
        elif deg >= 191.25 and deg < 213.75: return 'SSW'
        elif deg >= 213.75 and deg < 236.25: return 'SW'
        elif deg >= 236.25 and deg < 258.75: return 'WSW'
        elif deg >= 258.75 and deg < 281.25: return 'W'
        elif deg >= 281.25 and deg < 303.75: return 'WNW'
        elif deg >= 303.75 and deg < 326.25: return 'NW'
        elif deg >= 326.25 and deg < 348.75: return 'NNW'
        else: return 'N'

def gong():
    global gong_t
    aktual_gong_t = datetime.datetime.now()
    diff_gong_t = (aktual_gong_t - gong_t).total_seconds() 
    if int(terminal_beeps) == 1:
        if (diff_gong_t > min_t_sound):
            gong_t = aktual_gong_t
            print( '\a') ## TERMINAL GONG!

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

def get_metar_press():
    global metar_t
    global pressure
    global metar_path
    global metar_active

    if metar_active == 1:
        aktual_metar_t = datetime.datetime.now()
        diff_metar_t = (aktual_metar_t - metar_t).total_seconds() 
        if (diff_metar_t > 900):
            metar_t = aktual_metar_t
            metar_file=open(metar_path, 'r')
            metar_data=metar_file.readlines()
            metar_file.close()
            metar_line=[]
            pressure = ''
            PRESS_RE = re.compile(r"Q[0-1][0-9][0-9][0-9]")
            # metar_data=['METAR EPPO 021730Z 25007KT 6000 OVC023 04/03 Q0998 =' ]
            for i, line in enumerate(metar_data):
                if "EPPO" in line: 
                    metar_line.append(line.strip('\r\n').rstrip().strip())
                else:
                    return 1013

            for f, fields in enumerate(metar_line): 
                metar_fields = fields.split(" ")

            # print( metart_fields        

            for ff, field in enumerate(metar_fields): 
                if PRESS_RE.search(field): 
                    pressure = int(field[1:5])
            if ( 800 < pressure < 1100):
                return pressure
            else:
                return 1013
        else:
            #print(pressure)
            return pressure
    else:
        # alt pressure correction from metar inactive until tested
        # returns 1013 from global var
        return pressure


def pressure_corr(elevation):
    global my_elevation
    global my_elevation_const
    global near_airport_elevation
    global pressure

    if ignore_pressure == 1:
        if ignore_my_elevation == 1:
            elevation=int(elevation)
        else:
            if elevation > 6500:
                my_elevation_local = my_elevation * 3.28084 # why? # -90 ## taka sama wysokosc punktu obserwacji n.p.m jak pas na EPPO
                elevation=int(elevation) - my_elevation_local
            else:
                elevation = elevation - (my_elevation_local - near_airport_elevation_local)
    else:
        elevation=int(elevation)
        pressure = int(get_metar_press())


        my_elevation_local = my_elevation * 3.28084 # why? # -90 ## taka sama wysokosc punktu obserwacji n.p.m jak pas na EPPO
        near_airport_elevation_local = near_airport_elevation * 3.28084

        if elevation > 6500: # m or ft at this stage? 

            # elev > 6500m altimeters calibrated to 1013hPa
            #my_elevation = my_elevation_const #  wtf why? # my_elev was somewhere set to airport elev
            
            ################################################################################################################
            # THIS SEEMS TO BE THE GOLD, # FOR TESTS NOW
            elevation = (elevation + ((1013 - pressure)*30)) - my_elevation_local # now it's missing diff to my_elev!?!?
            ################################################################################################################

            #elevation = elevation + ((1013 - pressure)*30) # now it's missing diff to my_elev!?!?

        # elif, transition zone, but fok et
        else:

            # below 6500 altimeters calibrated to local airport pressure
            # we need diff between elev of observation point and airport!

            # todo
            #near_airport_elevation
            # probably this one is correct +/- diff between elev of observation point and airport
            
            
            elevation = elevation - (my_elevation_local - near_airport_elevation_local)

            #elevation - ((1013 - pressure)*30)) - my_elevation)
            #elevation = elevation #- ((1013 - pressure)*30) - my_elevation)
            #elevation = elevation - (((1013 - pressure)*30) - my_elevation) # adsb elev - ( pressure_corr - my_elev ) #30ft or m??

            # pfff, not sure, testing atm # probably unwanted mix with > 6500ft :/
            # elevation = (elevation + ((1013 - pressure)*30)) - my_elevation # adsb elev - ( pressure_corr - my_elev ) #30ft or m??


    return elevation


def clean_dict():
    for pentry in plane_dict:
        then2 = plane_dict[pentry][0]
        now2 = datetime.datetime.now()
        diff_minutes2 = (now2 - then2).total_seconds() / 60.
        
        if (diff_minutes2 > 1):
            del plane_dict[pentry]
            break

        if plane_dict[pentry][17] != "":
            thenZ = plane_dict[pentry][17]
            nowZ = datetime.datetime.now()
            diff_secondsZ = (nowZ - thenZ).total_seconds()
            if (diff_secondsZ > 60):
                del plane_dict[pentry]
                break

def countdown_s(sekundy, countdown_licznik):
    global last_sekundy
    global footer
    #print(sekundy)
    if is_float_try(sekundy):
        #print("a0")
        sekundy = int(sekundy)
    if is_int_try(sekundy):
        #print("a1")
        sekundy = int(sekundy)
    #footer = ''
    #footer += '<script>audioElements.play();sleep(700).then(() => {;audioElements.play();})</script>'
    #footer += '<script>audioElements.play();sleep(700).then(() => {;audioElement3.play();sleep(700).then(() => {;audioElementmin.play();  })  })</script>'
    #print(countdown_licznik, last_sekundy )
    if sekundy == "0":
        #print("xx1")
        return countdown_licznik, footer
    if sekundy == '':
        #print("xx2")
        return countdown_licznik, footer
    if (countdown_licznik >= 0): 
     if (last_sekundy == -1) or (last_sekundy > sekundy):
        print('x')
        #if sekundy > 186:
        #    footer = '''<script>var audioElements = new Audio('Sun.mp3');
        #                        var audioElement3 = new Audio('3.wav');
        #                        var audioElementmin = new Audio('Minutes.wav');
        #                        audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
        #                        audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
        #                        audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
        #    footer += 'audioElements.play(); sleep(700).then(() => {; '
        #    footer += 'audioElement3.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
        #    countdown_licznik += 1
        #    last_sekundy = sekundy

        if 179 <= sekundy <= 181:
            footer = '''<script>var audioElementm = new Audio('sun.mp3');
                                var audioElement3 = new Audio('3.wav');
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
            footer += 'audioElementm.play(); sleep(700).then(() => {;'
            footer += 'audioElement3.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 117 <= sekundy <= 123:
            footer = '''<script>var audioElementm = new Audio('sun.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement2 = new Audio('2.wav');
                                audioElement2.addEventListener('loadeddata', () => { let duration = audioElement2.duration; })
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement2.play();sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 58 <= sekundy <= 62:
            footer = '''<script>var audioElementm = new Audio('sun.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement1 = new Audio('1.wav');
                                audioElement1.addEventListener('loadeddata', () => { let duration = audioElement1.duration; })
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''

            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement1.play();sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 48 <= sekundy <= 52:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                var audioElement50 = new Audio('50.wav');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                audioElement50.addEventListener('loadeddata', () => { let duration = audioElement50.duration; });
                                '''

            footer += 'audioElements.play();sleep(700).then(() => {; audioElement50.play(); })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 38 <= sekundy <= 42:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement40 = new Audio('40.wav');
                                audioElement40.addEventListener('loadeddata', () => { let duration = audioElement40.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement40.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 28 <= sekundy <= 32:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement30 = new Audio('30.wav');
                                audioElement30.addEventListener('loadeddata', () => { let duration = audioElement30.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement30.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 18 <= sekundy <= 22:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement20 = new Audio('20.wav');
                                audioElement20.addEventListener('loadeddata', () => { let duration = audioElement20.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement20.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 14 <= sekundy <= 16:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement15 = new Audio('15.wav');
                                audioElement15.addEventListener('loadeddata', () => { let duration = audioElement15.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement15.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 10 <= sekundy <= 12:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement10 = new Audio('10.wav');
                                audioElement10.addEventListener('loadeddata', () => { let duration = audioElement10.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement10.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 0 < sekundy < 1:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement0 = new Audio('0.wav');
                                audioElement0.addEventListener('loadeddata', () => { let duration = audioElement0.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement0.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 1 <= sekundy < 2:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement1 = new Audio('1.wav');
                                audioElement1.addEventListener('loadeddata', () => { let duration = audioElement1.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement1.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 2 <= sekundy < 3:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement2 = new Audio('2.wav');
                                audioElement2.addEventListener('loadeddata', () => { let duration = audioElement2.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement2.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 3 <= sekundy < 4:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement3 = new Audio('3.wav');
                                audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement3.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 4 <= sekundy < 5:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement4 = new Audio('4.wav');
                                audioElement4.addEventListener('loadeddata', () => { let duration = audioElement4.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement4.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 5 <= sekundy < 6:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement5 = new Audio('5.wav');
                                audioElement5.addEventListener('loadeddata', () => { let duration = audioElement5.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement5.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 6 <= sekundy < 7:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement6 = new Audio('6.wav');
                                audioElement6.addEventListener('loadeddata', () => { let duration = audioElement6.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement6.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 7 <= sekundy < 8:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement7 = new Audio('7.wav');
                                audioElement7.addEventListener('loadeddata', () => { let duration = audioElement7.duration; });'''
            footer += 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement7.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 8 <= sekundy < 9:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement8 = new Audio('8.wav');
                                audioElement8.addEventListener('loadeddata', () => { let duration = audioElement8.duration; });'''
            footer = 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement8.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 9 <= sekundy < 10:
            footer = '''<script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement9 = new Audio('9.wav');
                                audioElement9.addEventListener('loadeddata', () => { let duration = audioElement9.duration; });'''
            footer = 'audioElements.play();sleep(700).then(() => {;'
            footer += 'audioElement9.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        #print(footer)
    return countdown_licznik, footer


def countdown_m(sekundy, countdown_licznik):
    global last_sekundy
    global footer
    #print(sekundy)
    if is_float_try(sekundy):
        #print("a0")
        sekundy = int(sekundy)
    if is_int_try(sekundy):
        #print("a1")
        sekundy = int(sekundy)
    #footer = ''
    #footer += '<script>audioElements.play();sleep(700).then(() => {;audioElements.play();})</script>'
    
    #footer += '<script>audioElements.play();sleep(700).then(() => {;audioElement3.play();sleep(700).then(() => {;audioElementmin.play();  })  })</script>'
    # print(countdown_licznik, last_sekundy )
    if sekundy == "0":
        #print("xx1")
        return countdown_licznik, footer
    if sekundy == '':
        #print("xx2")
        return countdown_licznik, footer
    if (countdown_licznik >= 0): 
     if (last_sekundy == -1) or (last_sekundy > sekundy):
        print('x1')
        #if sekundy > 186:
        #    footer = '<script>audioElementm.play();sleep(700).then(() => {;'
        #    footer += 'audioElement20.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
        #    countdown_licznik += 1
        #    last_sekundy = sekundy
        '''
                                var audioElement60 = new Audio('60.wav');
                                var audioElement50 = new Audio('50.wav');
                                var audioElement40 = new Audio('40.wav');
                                var audioElement30 = new Audio('30.wav');
                                var audioElement20 = new Audio('20.wav');
                                var audioElement15 = new Audio('15.wav');
                                var audioElement10 = new Audio('10.wav');
                                var audioElement9 = new Audio('9.wav');
                                var audioElement8 = new Audio('8.wav');
                                var audioElement7 = new Audio('7.wav');
                                var audioElement6 = new Audio('6.wav');
                                var audioElement5 = new Audio('5.wav');
                                var audioElement4 = new Audio('4.wav');
                                var audioElement3 = new Audio('3.wav');
                                var audioElement2 = new Audio('2.wav');
                                var audioElement1 = new Audio('1.wav');
                                var audioElement0 = new Audio('0.wav');
                                var audioElements = new Audio('sun.mp3');
                                var audioElementm = new Audio('moon.mp3');
    
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                audioElement60.addEventListener('loadeddata', () => { let duration = audioElement60.duration; })
                                audioElement50.addEventListener('loadeddata', () => { let duration = audioElement50.duration; })
                                audioElement40.addEventListener('loadeddata', () => { let duration = audioElement40.duration; })
                                audioElement30.addEventListener('loadeddata', () => { let duration = audioElement30.duration; })
                                audioElement20.addEventListener('loadeddata', () => { let duration = audioElement20.duration; })
                                audioElement15.addEventListener('loadeddata', () => { let duration = audioElement15.duration; })
                                audioElement10.addEventListener('loadeddata', () => { let duration = audioElement10.duration; })
                                audioElement9.addEventListener('loadeddata', () => { let duration = audioElement9.duration; })
                                audioElement8.addEventListener('loadeddata', () => { let duration = audioElement8.duration; })
                                audioElement7.addEventListener('loadeddata', () => { let duration = audioElement7.duration; })
                                audioElement6.addEventListener('loadeddata', () => { let duration = audioElement6.duration; })
                                audioElement5.addEventListener('loadeddata', () => { let duration = audioElement5.duration; })
                                audioElement4.addEventListener('loadeddata', () => { let duration = audioElement4.duration; })
                                audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
                                audioElement2.addEventListener('loadeddata', () => { let duration = audioElement2.duration; })
                                audioElement1.addEventListener('loadeddata', () => { let duration = audioElement1.duration; })
                                audioElement0.addEventListener('loadeddata', () => { let duration = audioElement0.duration; })
            
            footer = <script>var audioElements = new Audio('sun.mp3');
                                audioElements.addEventListener('loadeddata', () => { let duration = audioElements.duration; })
                                var audioElement = new Audio('.wav');
                                audioElement.addEventListener('loadeddata', () => { let duration = audioElement.duration; })'''
        
        #if sekundy > 186:
        #    footer = '''<script>var audioElementm = new Audio('sun.mp3');
        #                        audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
        #                        var audioElement3 = new Audio('3.wav');
        #                        audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
        #                        var audioElementmin = new Audio('Minutes.wav');
        #                        audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
        #    footer += 'audioElementm.play(); sleep(700).then(() => {;'
        #    footer += 'audioElement3.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
        #    countdown_licznik += 1
        #    last_sekundy = sekundy

        
        if 179 <= sekundy <= 181:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement3 = new Audio('3.wav');
                                audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
            footer += 'audioElementm.play(); sleep(700).then(() => {;'
            footer += 'audioElement3.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 117 <= sekundy <= 123:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement2 = new Audio('2.wav');
                                audioElement2.addEventListener('loadeddata', () => { let duration = audioElement2.duration; })
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement2.play();sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 58 <= sekundy <= 62:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement1 = new Audio('1.wav');
                                audioElement1.addEventListener('loadeddata', () => { let duration = audioElement1.duration; })
                                var audioElementmin = new Audio('Minutes.wav');
                                audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement1.play();sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 48 <= sekundy <= 52:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement50 = new Audio('50.wav');
                                audioElement50.addEventListener('loadeddata', () => { let duration = audioElement50.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement50.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 38 <= sekundy <= 42:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement40 = new Audio('40.wav');
                                audioElement40.addEventListener('loadeddata', () => { let duration = audioElement40.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement40.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 28 <= sekundy <= 32:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement30 = new Audio('30.wav');
                                audioElement30.addEventListener('loadeddata', () => { let duration = audioElement30.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement30.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 18 <= sekundy <= 22:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement20 = new Audio('20.wav');
                                audioElement20.addEventListener('loadeddata', () => { let duration = audioElement20.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement20.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 14 <= sekundy <= 16:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement15 = new Audio('15.wav');
                                audioElement15.addEventListener('loadeddata', () => { let duration = audioElement15.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement15.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 10 <= sekundy <= 12:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement10 = new Audio('10.wav');
                                audioElement10.addEventListener('loadeddata', () => { let duration = audioElement10.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement10.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 0 < sekundy < 1:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement0 = new Audio('0.wav');
                                audioElement0.addEventListener('loadeddata', () => { let duration = audioElement0.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement0.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 1 <= sekundy < 2:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement1 = new Audio('1.wav');
                                audioElement1.addEventListener('loadeddata', () => { let duration = audioElement1.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement1.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 2 <= sekundy < 3:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement2 = new Audio('2.wav');
                                audioElement2.addEventListener('loadeddata', () => { let duration = audioElement2.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement2.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 3 <= sekundy < 4:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement3 = new Audio('3.wav');
                                audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement3.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 4 <= sekundy < 5:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement4 = new Audio('4.wav');
                                audioElement4.addEventListener('loadeddata', () => { let duration = audioElement4.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement4.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 5 <= sekundy < 6:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement5 = new Audio('5.wav');
                                audioElement5.addEventListener('loadeddata', () => { let duration = audioElement5.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement5.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 6 <= sekundy < 7:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement6 = new Audio('6.wav');
                                audioElement6.addEventListener('loadeddata', () => { let duration = audioElement6.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement6.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 7 <= sekundy < 8:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement7 = new Audio('7.wav');
                                audioElement7.addEventListener('loadeddata', () => { let duration = audioElement7.duration; });'''
            footer += 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement7.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 8 <= sekundy < 9:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement8 = new Audio('8.wav');
                                audioElement8.addEventListener('loadeddata', () => { let duration = audioElement8.duration; });'''
            footer = 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement8.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        elif 9 <= sekundy < 10:
            footer = '''<script>var audioElementm = new Audio('moon.mp3');
                                audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
                                var audioElement9 = new Audio('9.wav');
                                audioElement9.addEventListener('loadeddata', () => { let duration = audioElement9.duration; });'''
            footer = 'audioElementm.play();sleep(700).then(() => {;'
            footer += 'audioElement9.play();})</script>'
            countdown_licznik += 1
            last_sekundy = sekundy
        #print(footer)
    return countdown_licznik, footer



##########################################################################################################################################################
# Tabela TERMINAL
##########################################################################################################################################################

def sekundy2minsec(seconds_in):
    delta_seconds_1 = int(seconds_in)
    delta_minutes_1 = delta_seconds_1 // 60
    if delta_minutes_1 >= 1:
        delta_1 = '%02dm%02ds' % (delta_minutes_1, delta_seconds_1 % 60)
    else:
        delta_1 = '%02s %02ds' % ("  ", delta_seconds_1 % 60)
    
    #delta_1 = '%02dm%02ds' % (delta_minutes_1, delta_seconds_1 % 60)
    return str(delta_1)


def tabela_terminal():
    #global footer
    global last_t_terminal
    #global last_sekundy
    if time_corr_ephem == "1":
        #print("aaa")
        d_t1 = datetime.datetime.utcnow() + datetime.timedelta(minutes=int(minutes_add_ephem))
        gatech.date = ephem.Date(d_t1)
    else:
        gatech.date = ephem.now()
    
    # vm for right table slot, vs for left table slot 
    #print(sel_obj_A,sel_obj_B)
    if sel_obj_A == "Sun":
        vs = ephem.Sun(gatech)
    elif sel_obj_A == "Moon":
        vs = ephem.Moon(gatech)
    elif sel_obj_A == "Jupiter":
        vs = ephem.Jupiter(gatech)
    elif sel_obj_A == "Saturn":
        vs = ephem.Saturn(gatech)
    elif sel_obj_A == "Mars":
        vs = ephem.Mars(gatech)
    elif sel_obj_A == "Venus":
        vs = ephem.Venus(gatech)

    if sel_obj_B == "Sun":
        vm = ephem.Sun(gatech)
    elif sel_obj_B == "Moon":
        vm = ephem.Moon(gatech)
    elif sel_obj_B == "Jupiter":
        vm = ephem.Jupiter(gatech)
    elif sel_obj_B == "Saturn":
        vm = ephem.Saturn(gatech)
    elif sel_obj_B == "Mars":
        vm = ephem.Mars(gatech)
    elif sel_obj_B == "Venus":
        vm = ephem.Venus(gatech)
    #vs = ephem.Moon(gatech)
    #vm = ephem.Sun(gatech)
    
    # can be used via star name like this: 
    # vs = ephem.star('Polaris')
    
    # or via planet name like this:
    # vs = ephem.Mars(gatech)
    # vm = ephem.Jupiter(gatech)
    
    
    vm.compute(gatech)
    vs.compute(gatech)
    obj_A_alt, obj_A_az= round(math.degrees(vm.alt), 1), round(math.degrees(vm.az), 1)
    obj_B_alt, obj_B_az= round(math.degrees(vs.alt), 1), round(math.degrees(vs.az), 1)
    
    diff_t = (aktual_t - last_t_terminal).total_seconds()
    ## Update freq 1=1s, 0=realtime 
    if (diff_t > 1):
        last_t_terminal = aktual_t


        print('\033c'+ " Flight info:           | Current:                   | Predictions:                     | Trans: "+ str(vs.name) +" " +str(obj_B_az) +" "+ str(obj_B_alt) +'  &  '+ str(vm.name)+" "+ str(obj_A_az)+" "+ str(obj_A_alt)+ '')
        print( '{:9} {:>6} {:>6} {} {:>5}  {:>5} {:>6} {:>5} {} {:>6} {:>7} {:>7} {:>8} {} {:>7} {:>7} {:>8} {} {:>7} {:>7} {:>7} {} {:>5}'.format(\
        ' icao or', ' (m)', '(d)', '|', '(km)', '(d)', '(d)', '(l)', ' |', '(km)', '(d)', '(d)', 'time2', ' |', '(d)', '(km)', 'time2', '|', '(d)', '(km)', 'time2', ' |', '(s)'))
        print( '{:9} {:>6} {:>6} {} {:>5} {:>5} {:>6} {:>5} {} {:3} {:<5} {:>7} {:>9} {} {:>7} {:>7} {:>8} {} {:>7} {:>7} {:>7} {} {:>5}'.format(\
        ' flight', 'elev', 'trck', '|', 'dist', 'Alt', 'Azim', 'Azim', '  |', '[ warn ]', '[ Alt', 'Az ]', 'closest', '|', 'Sep', 'h2x', str(vs.name), '|', 'Sep', 'h2x', str(vm.name), ' |', 'age / latlon'))
        print( "------------------------|----------------------------|----------------------------------|--------------------------|--------------------------|-------|-------")

        ## Subloop through all entries
        #with open(out_path_html,'w') as tsttxt:
        #    tsttxt.write(str(header))
        #footer = ''
        #countdown_licznik = 0
        #last_sekundy = -1
        #with open(out_path,'w') as tsttxtzap:
        #    tsttxtzap.write('')

        for pentry in plane_dict:
            #print( plane_dict[pentry])
            #print('8', plane_dict[pentry][8],'9',plane_dict[pentry][9],'12',plane_dict[pentry][12],plane_dict[pentry][5],plane_dict[pentry][10] )
            #zapis2 = ''
            #with open(out_path,'a') as tsttxt:
            if not (plane_dict[pentry][5] == '') and (plane_dict[pentry][5] <= display_limit):
                    if plane_dict[pentry][17] != "":
                        then = plane_dict[pentry][17]
                        now = datetime.datetime.now()
                        diff_seconds = (now - then).total_seconds()
                    else:
                        diff_seconds = 999
                        
                    then1 = plane_dict[pentry][0]
                    now1 = datetime.datetime.now()
                    diff_minutes = (now1 - then1).total_seconds() / 60.0

                    wuersz = ''
                    #zapis2 = ''

                    

                    # 1st section
                    if plane_dict[pentry][1] != "":
                        wuersz += '{} {:7} {}'.format(YELLOW, str(plane_dict[pentry][1]), RESET)                                                 ##flight
                        
                    else:
                        wuersz += '{} {:7} {}'.format(RESET, str(pentry), RESET)                            ##flight
                    
                    if is_float_try(plane_dict[pentry][4]):
                        elevation=int(plane_dict[pentry][4])
                    else:
                        elevation=9999

                    wuersz += '{} {:>6} {}'.format(elev_col(elevation), str(elevation),RESET)     ##elev

                    wuersz += '{:>5}'.format(str(plane_dict[pentry][11]))                                                ## trck

                    wuersz += '  |'
                    wuersz += '{} {:>5} {}'.format(dist_col(plane_dict[pentry][5]), str(plane_dict[pentry][5]),RESET)    ## dist

                    # Current altitude in degrees
                    wuersz += '{} {:>5} {}'.format(alt_col(plane_dict[pentry][7]), str(plane_dict[pentry][7]),RESET)    ## Alt


                    # x/!/o latest msg age in pictograms :S (msg type 3 with position ())
                    if diff_seconds >= 999:
                        wuersz += '{}'.format(RED+str("x") +RESET)    
                    elif diff_seconds > 30:
                        wuersz += '{}'.format(RED+str("!") +RESET)    
                    elif diff_seconds > 15:
                        wuersz += '{}'.format(YELLOW+ str("!")+ RESET)    
                    elif diff_seconds > 10:
                        wuersz += '{}'.format(GREENFG+ str("!")+ RESET)    
                    else:
                        wuersz += '{}'.format(GREENFG+str("o") +RESET)    
                    
                    wuersz += '{:>6}'.format(str(plane_dict[pentry][6]))                                                ## Az    
                    
                    wuersz += '{:>6}'.format(str(wind_deg_to_str1(plane_dict[pentry][6])))                                ## news

                    

                    wuersz += ' | '


                    # Predicted closest altitude in degrees
                    if is_float_try(plane_dict[pentry][13]):
                        if plane_dict[pentry][13] == 0:
                            # my_elevation again :/
                            #altitudeX = round(degrees(atan((elevation - my_elevation)/(float(0.01)*1000))) ,1)
                            altitudeX = round(degrees(atan((elevation)/(float(0.01)*1000))) ,1)
                        else:
                            # my_elevation again :/
                            #altitudeX = round(degrees(atan((elevation - my_elevation)/(float(plane_dict[pentry][13])*1000))) ,1)
                            altitudeX = round(degrees(atan((elevation)/(float(plane_dict[pentry][13])*1000))) ,1)
                    else:
                        altitudeX = '0'

                    # Predicted closest dissance in km
                    if (plane_dict[pentry][12] == 'WARNING'):
                        if (plane_dict[pentry][9] == "RECEDING" or plane_dict[pentry][8] == "LEAVING"):
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),RED, str( plane_dict[pentry][13]),RESET, str(' ]')) 

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(plane_dict[pentry][7])), str(plane_dict[pentry][7]),RESET)    # kolorowanie dla aktualnej alt

                        elif (str(plane_dict[pentry][9]) == "APPROACHING"):
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),REDALERT, str( plane_dict[pentry][13]),RESET, str(' ]'))

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(float(altitudeX))), str(altitudeX),RESET)    # kolorowanie dla przewidzianej alt

                        else:
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),RESET, str( plane_dict[pentry][13]),RESET, str(' ]'))

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(float(altitudeX))), str(altitudeX),RESET)    # kolorowanie dla przewidzianej alt

                    else:
                        if (plane_dict[pentry][9] == "RECEDING" or plane_dict[pentry][8] == "LEAVING"):
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),PURPLEDARK, str( plane_dict[pentry][13]),RESET, str(' ]'))

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(plane_dict[pentry][7])), str(plane_dict[pentry][7]),RESET)    # kolorowanie dla aktualnej alt

                        elif (str(plane_dict[pentry][9]) == "APPROACHING"):
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),PURPLE, str( plane_dict[pentry][13]),RESET, str(' ]')) 

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(float(altitudeX))), str(altitudeX),RESET)    # kolorowanie dla przewidzianej altt

                        else:
                            wuersz += '{}{}{:>5}{}{}'.format(str('['),RESET, str( plane_dict[pentry][13]),RESET, str(' ]'))

                            wuersz += '{}{}{:>5}{}'.format(str(' ['), str(alt_col(float(altitudeX))), str(altitudeX),RESET)    # kolorowanie dla przewidzianej alt

                    wuersz += '{}{:>5}{}{}'.format(RESET, str(plane_dict[pentry][28]),RESET, str(' ]'))
                    wuersz += '{}{:>10}{}'.format( RESET, str(plane_dict[pentry][29]),RESET)

                    wuersz += ' |'


                    ##thenx = plane_dict[pentry][0]
                    #thenx = plane_dict[pentry][17]
                    #nowx = datetime.datetime.now()
                    #diff_secx = (nowx - thenx).total_seconds()

                    if is_float_try(plane_dict[pentry][19]) and is_float_try(plane_dict[pentry][18]):
                        separation_deg2 = round(float(plane_dict[pentry][19]-plane_dict[pentry][18]),1)
                    else:
                        separation_deg2 = 90.0

                    if (-transit_separation_GREENALERT_FG < separation_deg2 < transit_separation_GREENALERT_FG):
                        wuersz += '{} {:>6} {}'.format(GREENALERT, str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][20],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][22])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS
                        
                    elif (-transit_separation_REDALERT_FG < separation_deg2 < transit_separation_REDALERT_FG):
                        wuersz += '{} {:>6} {}'.format(REDALERT, str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][20],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][22])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS

                    elif (-transit_separation_notignored < separation_deg2 < transit_separation_notignored):
                        wuersz += '{} {:>6} {}'.format(RED, str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][20],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][22])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS

                    else:
                        wuersz += '{:>8}'.format(str("---"))  ## SEPARACJA

                        wuersz += '{:>7}'.format(str("---")) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str("---"))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROSS POINT                        

                    ###tu koniec

                    wuersz += ' |'
                    if is_float_try(plane_dict[pentry][24]) and is_float_try(plane_dict[pentry][23]):
                        separation_deg = round(float(plane_dict[pentry][24]-plane_dict[pentry][23]),1)
                    else:
                        separation_deg = 90.0

                    if (-transit_separation_GREENALERT_FG < separation_deg < transit_separation_GREENALERT_FG):
                        wuersz += '{} {:>6} {}'.format(GREENALERT, str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][25],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][26])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS

                    elif (-transit_separation_REDALERT_FG < separation_deg < transit_separation_REDALERT_FG):
                        wuersz += '{} {:>6} {}'.format(REDALERT, str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][25],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][26])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS

                    elif (-transit_separation_notignored < separation_deg < transit_separation_notignored):
                        wuersz += '{} {:>6} {}'.format(RED, str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),2)),RESET) ## SEPARACJA

                        wuersz += '{:>7}'.format(str(round(plane_dict[pentry][25],1))) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str(sekundy2minsec(plane_dict[pentry][26])))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROS

                    else:
                        wuersz += '{:>8}'.format(str("---"))  ## SEPARACJA

                        wuersz += '{:>7}'.format(str("---")) ## DISTANCE MY_POS TO CROSS POINT

                        wuersz += '{:>10}'.format(str("---"))            ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROSS POINT

                    ##tu koniec2    
                    wuersz += ' |'

                    thenx = plane_dict[pentry][0]
                    nowx = datetime.datetime.now()
                    diff_secx = (nowx - thenx).total_seconds()

                    wuersz += '{:>6}'.format(str(round(diff_secx, 1)))

                    wuersz += ' |'
                    if plane_dict[pentry][17] != "":
                        thenx1 = plane_dict[pentry][17]
                        nowx1 = datetime.datetime.now()
                        diff_secx1 = (nowx1 - thenx1).total_seconds()

                        wuersz += '{:>6}'.format(str(round(diff_secx1, 1)))
                    else:
                        wuersz += '{:>6}'.format(str('------'))

                    #print( wiersz)
                    #rint('8', plane_dict[pentry][8],'9',plane_dict[pentry][9],'12',plane_dict[pentry][12],plane_dict[pentry][5],plane_dict[pentry][10] )
                    # next 4 lines data for txt transit history
                    if transit_history_log == 1:
                        if ((-transit_separation_REDALERT_FG < separation_deg2 < transit_separation_REDALERT_FG) and obj_B_alt > minimum_alt_transits)  or ((-transit_separation_REDALERT_FG < separation_deg < transit_separation_REDALERT_FG) and obj_A_alt > minimum_alt_transits):
                            with open(transit_history_log_path,'a') as tra_txt:
                                trans_wiersz = str(plane_dict[pentry][0])+wuersz+'\n'
                                tra_txt.write(str(trans_wiersz))
                    '''
                    zapis=str(pentry)+','+str(plane_dict[pentry][1])+','+str(plane_dict[pentry][2])+','+\
                    str(plane_dict[pentry][3])+','+str(plane_dict[pentry][4])+','+str(plane_dict[pentry][5])+','+\
                    str(plane_dict[pentry][6])+','+str(plane_dict[pentry][7])+','+str(plane_dict[pentry][8])+','+\
                    str(plane_dict[pentry][9])+','+str(plane_dict[pentry][10])+','+str(plane_dict[pentry][11])+','+\
                    str(plane_dict[pentry][12])+','+str(plane_dict[pentry][13])+','+str(plane_dict[pentry][14])+','
                    for ii,e in enumerate(plane_dict[pentry][15]):
                        zapis += str(plane_dict[pentry][15][ii])+';'
                    zapis += ','
                    for ii,e in enumerate(plane_dict[pentry][16]):
                        zapis += str(plane_dict[pentry][16][ii])+';'
                    zapis += ','
                    zapis += str(plane_dict[pentry][17])+','+str(datetime.datetime.now().strftime('%H:%M:%S'))+','

                    if (obj_A_alt > minimum_alt_transits):
                        zapis += str(plane_dict[pentry][27])+','+str(separation_deg)+','+str(obj_A_az)+','+str(plane_dict[pentry][24])+','
                    else:
                        zapis += ''+','+''+','+''+','+''+','
                    if (obj_B_alt > minimum_alt_transits):
                        zapis += str(plane_dict[pentry][21])+','+str(separation_deg2)+','+str(obj_B_az)+','+str(plane_dict[pentry][19])+','
                    else:
                        zapis += ''+','+''+','+''+','+''+','

                    zapis += str(vm.name)+','+str(vs.name)+','+str(diff_seconds)+','
                    zapis += str(altitudeX)+','
                    zapis += '\n'
                    #with open('/tmp/out.txt','a') as tsttxtzap:
                    #    tsttxtzap.write(zapis)
                    with open(out_path,'a') as tsttxtzap:
                        tsttxtzap.write(zapis)
                    '''
                    
                    
            else:
                if plane_dict[pentry][17] != "":
                    then = plane_dict[pentry][17]
                    now = datetime.datetime.now()
                    diff_seconds = (now - then).total_seconds()
                else:
                    diff_seconds = 999
                if plane_dict[pentry][1] != "":
                    wuersz = ''
                    wuersz += '{} {:7} {}'.format(YELLOW, str(plane_dict[pentry][1]), RESET)   ##flight

                else:
                    wuersz = ''
                    wuersz += '{} {:7} {}'.format(RESET, str(pentry),RESET)                    ##icao
                    
                if plane_dict[pentry][4] != "":
                    if is_float_try(plane_dict[pentry][4]):
                        elevation=int(plane_dict[pentry][4])    
                    else:
                        elevation=9999
                    wuersz += '{} {:>6} {}'.format(elev_col(elevation), str(elevation),RESET)     ##elev
                    
                else:
                    wuersz += '{} {:>6} {}'.format(RESET,str('---'),RESET)                         ##elev

                if plane_dict[pentry][11] != "":
                    wuersz += '{:>5}'.format(str(plane_dict[pentry][11]))                          ##track

                else:
                    wuersz += '{:>5}'.format(str('---'))
                    
                wuersz += '  |'
                if plane_dict[pentry][5] != "":
                    wuersz = ''
                    wuersz += '{} {:>5} {}'.format(RESET, str(plane_dict[pentry][5]), RESET)       ##flight

                else:    
                    wuersz += '{} {:>5} {}'.format(RESET, str('---'),RESET)    

                wuersz += '{} {:>5} {}'.format(RESET, str('---'),RESET) ## alt    

                if diff_seconds > 5:
                    wuersz += '{}'.format(str("!"))    
                else:
                    wuersz += '{}'.format(str(" "))

                wuersz += '{:>7}'.format(str('---'))                     ## az1 news

                wuersz += '{:>5}'.format(str('---'))                     ## az2

                wuersz += ' |'


                wuersz += '{} {:>5} {}'.format(RESET, str('---'),RESET)                     ## warn

                wuersz += '{} {:>5} {}'.format(RESET, str('---'),RESET) ## alt    

                wuersz += '{} {:>5} {}'.format(RESET, str('---'),RESET) ## alt    
                wuersz += '{} {:>8} {}'.format(RESET, str('---'),RESET) ## alt    

                wuersz += '   |'


                wuersz += '{} {:>7} {}'.format(RESET, str('---'),RESET)                ## Sep

                wuersz += '{:>6}'.format(str('---')) 
                
                wuersz += '{:>10}'.format(str('---')) 

                wuersz += ' |'
                wuersz += '{} {:>7} {}'.format(RESET, str('---'),RESET)                ## Sep

                wuersz += '{:>6}'.format(str('---')) 

                wuersz += '{:>10}'.format(str('---')) 

                wuersz += ' |'
                thenx = plane_dict[pentry][0]
                nowx = datetime.datetime.now()
                diff_secx = (nowx - thenx).total_seconds()
                
                wuersz += '{:>6}'.format(str(round(diff_secx, 1)))
                
                wuersz += ' |'

                wuersz += '{:>6}'.format(str(' -----'))
            
            print( wuersz)
            #zapis2 += '</tr>'
            #tsttxt.write(str(zapis2))
                    

        #tsttxt.write(str(zapis2))
        #footer = ''
        #footer += '<script>audioElements.play();sleep(700).then(() => {;audioElement10.play();sleep(700).then(() => {;audioElementmin.play();  })  })</script>'
        
        #print("fuuuuuuuuuuuuu",footer)
        #footer_caly = str(footer)+'</table></body></html>'

        #with open(out_path_html,'a') as tsttxt:
        #    tsttxt.write(str(footer_caly))
                    
        print(print_lastline(diff_t))

    return obj_A_alt, obj_A_az, obj_B_alt, obj_B_az 





##########################################################################################################################################################
# koniecc Tabeli TERMINAL
##########################################################################################################################################################


##########################################################################################################################################################
# Tabela HTML
##########################################################################################################################################################

def tabela_html():
    global footer
    global last_t
    global last_sekundy
    global int_counter_1
    global int_counter_2
    global int_counter_3
    global int_counter_4
            
            
    if time_corr_ephem == "1":
        #print("aaa")
        d_t1 = datetime.datetime.utcnow() + datetime.timedelta(minutes=int(minutes_add_ephem))
        gatech.date = ephem.Date(d_t1)
    else:
        gatech.date = ephem.now()
    
    # vm for right table slot, vs for left table slot 
    if sel_obj_A == "Sun":
        vs = ephem.Sun(gatech)
        obj_A_str = sols_html
    elif sel_obj_A == "Moon":
        vs = ephem.Moon(gatech)
        obj_A_str = luns_html
    elif sel_obj_A == "Jupiter":
        vs = ephem.Jupiter(gatech)
        obj_A_str = jups_html
    elif sel_obj_A == "Saturn":
        vs = ephem.Saturn(gatech)
        obj_A_str = sats_html
    elif sel_obj_A == "Mars":
        vs = ephem.Mars(gatech)
        obj_A_str = mars_html
    elif sel_obj_A == "Venus":
        vs = ephem.Venus(gatech)
        obj_A_str = vens_html

    if sel_obj_B == "Sun":
        vm = ephem.Sun(gatech)
        obj_B_str = sols_html
    elif sel_obj_B == "Moon":
        vm = ephem.Moon(gatech)
        obj_B_str = luns_html
    elif sel_obj_B == "Jupiter":
        vm = ephem.Jupiter(gatech)
        obj_B_str = jups_html
    elif sel_obj_B == "Saturn":
        vm = ephem.Saturn(gatech)
        obj_B_str = sats_html
    elif sel_obj_B == "Mars":
        vm = ephem.Mars(gatech)
        obj_B_str = mars_html
    elif sel_obj_B == "Venus":
        vm = ephem.Venus(gatech)
        obj_B_str = vens_html

    #vs = ephem.Moon(gatech)
    #vm = ephem.Sun(gatech)
    
    # can be used via star name like this: 
    # vs = ephem.star('Polaris')
    
    # or via planet name like this:
    # vs = ephem.Mars(gatech)
    # vm = ephem.Jupiter(gatech)
    
    
    vm.compute(gatech)
    vs.compute(gatech)
    obj_A_alt, obj_A_az= round(math.degrees(vm.alt), 1), round(math.degrees(vm.az), 1)
    obj_B_alt, obj_B_az= round(math.degrees(vs.alt), 1), round(math.degrees(vs.az), 1)
    
    diff_t = (aktual_t - last_t).total_seconds()
    ## Update freq 1=1s, 0=realtime 
    if (diff_t > 1):
        last_t = aktual_t


        print('\033c')

        header_snd='''<html>
                    <head>
                        <meta http-equiv="refresh" content="2">
                        <meta http-equiv="Page-Enter" content="blendTrans(Duration=0.5)">
                        <meta http-equiv="Page-Exit" content="blendTrans(Duration=0.5)">
                        <script>
                            function sleep (time) {
                                return new Promise((resolve) => setTimeout(resolve, time));
                            }
                        </script>
                        </head>
                        <body style="background-color: #000000" >
        '''

        header='''<html>
                    <head>
                        <meta http-equiv="refresh" content="1">
                        <meta http-equiv="Page-Enter" content="blendTrans(Duration=0.5)">
                        <meta http-equiv="Page-Exit" content="blendTrans(Duration=0.5)">

                    <style>
                        body:not(.nohover) tbody tr:hover {
                         background-color: #403f41;

                        }


                        table {
                            border-collapse: collapse;
                            width: 99%;
                            color: white;
                            overflow: hidden;
                        }

                        td, th {
                            padding: 1px;
                            text-align: left;
                            font-size: 13px;
                            font-family: "Consolas";
                            position: relative;
                        }


                        thead {
                            color: #bcbaba;
                            background-color: #262626;
                        }

                        .ytext {
                            color: yellow;
                        }
                        .rtext {
                            color: #b30000;
                        }
                        .rrtext {
                            background-color: red;
                        }
                        .gtext {
                            color: green;
                        }
                        .ggtext {
                            background-color: green;
                        }
                        .ptext {
                            color: #cc00cc;
                        }
                        .dptext {
                            color: #660066;
                        }
                        .ctext {
                            color: #33cccc;
                        }
                        .lbtext {
                            color: #a6b5fd;
                        }
                        .otext {
                            color: #ff6600;
                        }
                        .wtext {
                            color: #ffffff;
                        }

                        td:hover::after,
                        thead th:not(:empty):hover::after,
                        td:focus::after,
                        thead th:not(:empty):focus::after {
                          content: '';
                          height: 10000px;
                          left: 0;
                          position: absolute;
                          top: -5000px;
                          width: 100%;
                          z-index: -1;
                        }
    
                        td:hover::after,
                        th:hover::after {
                            background-color: #403f41;
                        }
    
                        td:hover::after,
                        thead th:not(:empty):hover::after,
                        tr:hover::after,
                        thead th:not(:empty):focus::after { 
                        {
                            #background-color: #0000ff;
                            content: "";
                            position: absolute;
                            background-color: gray;
                            left: 0;
                            top: -5000px;
                            height: 10000px;
                            width: 100%;
                            z-index: -1;
                        }
                        /* Focus stuff for mobile */
                        td:focus::before,
                        tbody th:focus::before {
                          background-color: lightblue;
                          content: '';  
                          height: 100%;
                          top: 0;
                          left: -5000px;
                          position: absolute;  
                          width: 10000px;
                          z-index: -1;
                        }
    
                        </style>
                        <script>
                            function sleep (time) {
                                return new Promise((resolve) => setTimeout(resolve, time));
                            }

                        </script>
                        <script type='text/javascript' src='https://code.jquery.com/jquery-1.10.1.js'></script>

                        </head>
                <body style="background-color: #000000" >
                <table>

                <thead>
                <tr>
                <td>Flight</td>
                <td>info</td>
                <td></td>
                <td style="text-align: right;">CURRE</td>
                <td>NT</td>
                <td></td>
                <td></td>
                <td></td>
                <td class="otext" style="text-align: right;">PREDIC</td>
                <td class="otext">TED</td><td></td>
                
                '''
        header += '<td></td><td class="lbtext">Tr: '+str(obj_A_str)+'</td><td class="lbtext">'
        header += str(obj_B_alt)+'</td><td class="lbtext">'+str(obj_B_az)+'</td><td class="ytext">Tr: '+str(obj_B_str)+'</td><td class="ytext">'+str(obj_A_alt)+'</td><td class="ytext">'+str(obj_A_az)
        header += '''</td>
                
                <td>LAST</td><td>MSG</td>
                </tr>


                <tr>
                
                <td id="call" title="Callsign if available or icao code"  class="wtext">Callsign</td>
                
                <script> 
                $("#call").click(function(){ 
                    var name = "aargh";
                    //var name = $('#call').value();
                    $.ajax({ 
                        type: "POST", 
                        url: "phpy/lo15.php", 
                        data: {"name": name},
                        //success: function(output) { alert(name); },
                        error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } 
                    });
                });
                </script>
                
                <td title="(m) Elevation in meters, may depend on pressure and/or my_elevation. Not exactly FlightLevel" >Elev</td>
                <td title="(deg) Track aka heading aka course">Track</td>
                <td title="(km) Current distance to the aircraft in km">Dist</td>
                <td title="(deg) Current altitude in degrees on which the aircraft is visible">[ Alt</td>
                <td style="text-align: right;" title="(deg) Current azimuth in degrees on which the aircraft is visible.">Az ]&nbsp;</td>
                <td title="Current azimuth in letter /compass-like/ direction on which the aircraft is visible.">NWSE</td>
                <td title="Old data warning. See age columns for time of last msg">?</td>
                <td title="(km) Predicted closest distance from observer to aircraft in km" class="otext">Dist</td>
                <td title="(deg) Predicted altitude of the aircraft at closest distance in degrees" class="otext">[ Alt</td>
                <td style="text-align: right;" title="(deg) Predicted azimuth at which the aircraft will be at closest distance" class="otext">Az ]&nbsp;</td>
                <td title="Predicted time to closest encounter" class="otext">t2c</td>
                
                <td title="(deg) Predicted Separation from celestial object at the time of crossing its azimuth by aircraft" class="lbtext">d2x</td>
                <td title="(km) Predicted distance to the aircraft at the time of crossing object azimuth" class="lbtext">km2x</td>
                <td title="Predicted time to crossing azimuth of object by aircraft" class="lbtext">t2x</td>
                <td title="(deg) Predicted Separation from celestial object at the time of crossing its azimuth by aircraft" class="ytext">d2x</td>
                
                <td title="(km) Predicted distance to the aircraft at the time of crossing object azimuth" class="ytext">km2x</td>
                <td title="Predicted time to crossing azimuth of object by aircraft" class="ytext">t2x</td>
                <td title="Time from last message from aircraft. (Any)">any</td>
                <td title="Time from last message from aircraft. (With position)">pos</td>
                </tr>
                </thead>
                
                '''
        '''
                                //<script>audioElements.play();audioElement60.play();</script>

        '''
        ## Subloop through all entries
        with open(out_path_html,'w') as tsttxt:
            tsttxt.write(str(header))
        footer = ''
        countdown_licznik = 0
        last_sekundy = -1
        with open(out_path,'w') as tsttxtzap:
            tsttxtzap.write('')
        
        if os.path.isfile('/tmp/AllSkyRadar/highlight'):
            DataFileNameHL='/tmp/AllSkyRadar/highlight'
            datafileHL=open(DataFileNameHL, 'r')
            HL=datafileHL.readlines()
            datafileHL.close()
        else:
            HL=''
        zapis2a = ''
        for pentry in plane_dict:
            #print( plane_dict[pentry])
            #print('8', plane_dict[pentry][8],'9',plane_dict[pentry][9],'12',plane_dict[pentry][12],plane_dict[pentry][5],plane_dict[pentry][10] )
            zapis2 = ''
            with open(out_path_html,'a') as tsttxt:
                if not (plane_dict[pentry][5] == '') and (plane_dict[pentry][5] <= display_limit):
                        if plane_dict[pentry][17] != "":
                            then = plane_dict[pentry][17]
                            now = datetime.datetime.now()
                            diff_seconds = (now - then).total_seconds()
                        else:
                            diff_seconds = 999

                        then1 = plane_dict[pentry][0]
                        now1 = datetime.datetime.now()
                        diff_minutes = (now1 - then1).total_seconds() / 60.0

                        zapis2 = ''

                        # 1st section
                        if plane_dict[pentry][1] != "":
                            if str(plane_dict[pentry][1]) == str(HL[0].strip()):
                                zapis2 += '<tr id="'+str(plane_dict[pentry][1])+'"  style="background-color: #104600">'
                            else:
                                zapis2 += '<tr id="'+str(plane_dict[pentry][1])+'" >'
                            zapis2 +=  '<td class="ytext">'+str(plane_dict[pentry][1])+'</td>\n'                                                 ##flight
                            zapis2a += '$("#'+str(plane_dict[pentry][1])+'").click(function(){ var name = "'+str(plane_dict[pentry][1])+'"; $.ajax({ type: "POST", url: "phpy/lo15.php", data: {"name": name},  error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } });});\n'
                        else:
                            if str(pentry) == str(HL[0].strip()):
                                zapis2 += '<tr id="'+str(pentry)+'" style="background-color: #104600">'
                            else:
                                zapis2 += '<tr id="'+str(pentry)+'">'

                            zapis2 +=  '<td>'+str(pentry)+'</td>\n'                                                 ##flight
                            zapis2a += '$("#'+str(pentry)+'").click(function(){ var name = "'+str(pentry)+'"; $.ajax({ type: "POST", url: "phpy/lo15.php", data: {"name": name},  error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } });});\n'

                        if is_float_try(plane_dict[pentry][4]):
                            elevation=int(plane_dict[pentry][4])
                        else:
                            elevation=9999

                        zapis2 += '<td '+str(elev_col_2(elevation))+'>'+str(elevation)+'</td>\n'

                        zapis2 += '<td>'+str(plane_dict[pentry][11])+'</td>\n'

                        zapis2 += '<td '+dist_col_2(plane_dict[pentry][5])+'>'+str(plane_dict[pentry][5])+'</td>\n'


                        # Current altitude in degrees
                        zapis2 += '<td '+str(alt_col_2(plane_dict[pentry][7]))+'>['+str(plane_dict[pentry][7])+str(deg_html)+'</td>\n'




                        zapis2 += '<td style="text-align: right;">'+str(plane_dict[pentry][6])+str(deg_html)+']&nbsp;</td>\n'
                        zapis2 += '<td style="text-align: right;">'+str(wind_deg_to_str1(plane_dict[pentry][6]))+'</td>\n'

                        # x/!/o latest msg age in pictograms :S (msg type 3 with position ())
                        if diff_seconds >= 999:
                            zapis2 += '<td class="rtext">'+str("&nbsp;x&nbsp;")+'</td>\n'
                        elif diff_seconds > 30:
                            zapis2 += '<td class="rtext">'+str("&nbsp;!&nbsp;")+'</td>\n'
                        elif diff_seconds > 15:
                            zapis2 += '<td class="ytext">'+str("&nbsp;!&nbsp;")+'</td>\n'
                        elif diff_seconds > 10:
                            zapis2 += '<td class="gtext">'+str("&nbsp;!&nbsp;")+'</td>\n'
                        else:
                            zapis2 += '<td class="gtext">'+str("&nbsp;o&nbsp;")+'</td>\n'

                        # Predicted closest altitude in degrees
                        if is_float_try(plane_dict[pentry][13]):
                            if plane_dict[pentry][13] == 0:
                                # my_elevation again :/
                                #altitudeX = round(degrees(atan((elevation - my_elevation)/(float(0.01)*1000))) ,1)
                                altitudeX = round(degrees(atan((elevation)/(float(0.01)*1000))) ,1)
                            else:
                                # my_elevation again :/
                                #altitudeX = round(degrees(atan((elevation - my_elevation)/(float(plane_dict[pentry][13])*1000))) ,1)
                                altitudeX = round(degrees(atan((elevation)/(float(plane_dict[pentry][13])*1000))) ,1)
                        else:
                            altitudeX = '0'

                        # Predicted closest dissance in km
                        if (plane_dict[pentry][12] == 'WARNING'):
                            if (plane_dict[pentry][9] == "RECEDING" or plane_dict[pentry][8] == "LEAVING"):
                                zapis2 += '<td class="rtext">['+str(plane_dict[pentry][13])+']</td>\n'

                                zapis2 += '<td '+str(alt_col_2(plane_dict[pentry][7]))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'

                            elif (str(plane_dict[pentry][9]) == "APPROACHING"):
                                zapis2 += '<td class="rrtext">['+str(plane_dict[pentry][13])+']</td>\n'

                                zapis2 += '<td '+str(alt_col_2(float(altitudeX)))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'

                            else:
                                zapis2 += '<td>['+str(plane_dict[pentry][13])+'</td>\n'

                                zapis2 += '<td '+str(alt_col_2(float(altitudeX)))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'

                        else:
                            if (plane_dict[pentry][9] == "RECEDING" or plane_dict[pentry][8] == "LEAVING"):
                                zapis2 += '<td class="dptext">['+str(plane_dict[pentry][13])+']</td>\n'

                                zapis2 += '<td '+str(alt_col_2(plane_dict[pentry][7]))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'

                            elif (str(plane_dict[pentry][9]) == "APPROACHING"):
                                zapis2 += '<td class="ptext">['+str(plane_dict[pentry][13])+']</td>\n'

                                zapis2 += '<td '+str(alt_col_2(float(altitudeX)))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'

                            else:
                                zapis2 += '<td>['+str(plane_dict[pentry][13])+']</td>\n'

                                zapis2 += '<td '+str(alt_col_2(float(altitudeX)))+'>['+str(altitudeX)+str(deg_html)+'</td>\n'


                        zapis2 += '<td style="text-align: right;">'+str(plane_dict[pentry][28])+str(deg_html)+']&nbsp;</td>\n'
                        if str(plane_dict[pentry][29]) == "gone":
                            zapis2 += '<td class="rtext">'+str(plane_dict[pentry][29])+'</td>\n'
                        else:
                            zapis2 += '<td>'+str(plane_dict[pentry][29])+'</td>\n'

                        ##thenx = plane_dict[pentry][0]
                        #thenx = plane_dict[pentry][17]
                        #nowx = datetime.datetime.now()
                        #diff_secx = (nowx - thenx).total_seconds()

                        if is_float_try(plane_dict[pentry][19]) and is_float_try(plane_dict[pentry][18]):
                            separation_deg2 = round(float(plane_dict[pentry][19]-plane_dict[pentry][18]),1)
                        else:
                            separation_deg2 = 90.0

                        if (-transit_separation_GREENALERT_FG < separation_deg2 < transit_separation_GREENALERT_FG):# and (round(plane_dict[pentry][22],1) < 100):
                            zapis2 += '<td class="ggtext">'+str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),1))+str(deg_html)+'</td>\n'


                            zapis2 += '<td class="ggtext">'+str(round(plane_dict[pentry][20],1))+'</td>\n'

                            zapis2 += '<td class="ggtext">'+str(sekundy2minsec(plane_dict[pentry][22]))+'</td>\n'
                            #print("m",moon_tr_sound, minimum_alt_transits , obj_B_alt, transit_separation_sound_alert, separation_deg2)
                            if (-transit_separation_sound_alert < separation_deg2 < transit_separation_sound_alert):
                                if (int(moon_tr_sound) == 1) and (int(minimum_alt_transits) < obj_B_alt):
                                    countdown_licznik, footer = countdown_m(plane_dict[pentry][22], countdown_licznik)
                            #countdown_licznik, footer = countdown_m(plane_dict[pentry][22], countdown_licznik)
                        elif (-transit_separation_REDALERT_FG < separation_deg2 < transit_separation_REDALERT_FG): # and (round(plane_dict[pentry][22],1) < 100):
                            zapis2 += '<td class="rrtext">'+str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),1))+str(deg_html)+'</td>\n'

                            zapis2 += '<td class="rrtext">'+str(round(plane_dict[pentry][20],1))+'</td>\n'

                            zapis2 += '<td class="rrtext">'+str(sekundy2minsec(plane_dict[pentry][22]))+'</td>\n'

                            #countdown_licznik, footer = countdown_m(plane_dict[pentry][22], countdown_licznik)


                        elif (-transit_separation_notignored < separation_deg2 < transit_separation_notignored):
                            zapis2 += '<td>'+str(round((plane_dict[pentry][19]-plane_dict[pentry][18]),1))+str(deg_html)+'</td>\n'

                            zapis2 += '<td>'+str(round(plane_dict[pentry][20],1))+'</td>\n'

                            zapis2 += '<td>'+str(sekundy2minsec(plane_dict[pentry][22]))+'</td>\n'

                            #countdown_licznik, footer = countdown_m(plane_dict[pentry][22], countdown_licznik)

                        else:
                            zapis2 += '<td> ---- </td>\n'

                            zapis2 += '<td> ---- </td>\n'

                            zapis2 += '<td> ---- </td>\n'

                            #countdown_licznik, footer = countdown_s(plane_dict[pentry][22], countdown_licznik)

                        ###tu koniec

                        #wuersz += ' |'
                        if is_float_try(plane_dict[pentry][24]) and is_float_try(plane_dict[pentry][23]):
                            separation_deg = round(float(plane_dict[pentry][24]-plane_dict[pentry][23]),1)
                        else:
                            separation_deg = 90.0

                        if (-transit_separation_GREENALERT_FG < separation_deg < transit_separation_GREENALERT_FG): # and (round(plane_dict[pentry][25],1) < 100):
                            zapis2 += '<td class="ggtext">'+str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),1))+str(deg_html)+'</td>\n'


                            zapis2 += '<td class="ggtext">+'+str(round(plane_dict[pentry][25],1))+'</td>\n'

                            zapis2 += '<td class="ggtext">+'+str(sekundy2minsec(plane_dict[pentry][26]))+'</td>\n'
                            #print("s", sun_tr_sound, minimum_alt_transits,obj_A_alt, transit_separation_sound_alert, separation_deg)
                            if (-transit_separation_sound_alert < separation_deg < transit_separation_sound_alert):
                                if (int(sun_tr_sound) == 1) and (int(minimum_alt_transits) < obj_A_alt):
                                    countdown_licznik, footer = countdown_s(plane_dict[pentry][26], countdown_licznik)
                            #countdown_licznik, footer = countdown_s(plane_dict[pentry][26], countdown_licznik)
                        elif (-transit_separation_REDALERT_FG < separation_deg < transit_separation_REDALERT_FG): # and (round(plane_dict[pentry][25],1) < 100):
                            zapis2 += '<td class="rrtext">'+str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),1))+str(deg_html)+'</td>\n'

                            zapis2 += '<td class="rrtext">'+str(round(plane_dict[pentry][25],1))+'</td>\n'

                            zapis2 += '<td class="rrtext">'+str(sekundy2minsec(plane_dict[pentry][26]))+'</td>\n'

                            #countdown_licznik, footer = countdown_s(plane_dict[pentry][26], countdown_licznik)

                        elif (-transit_separation_notignored < separation_deg < transit_separation_notignored):
                            zapis2 += '<td>'+str(round((plane_dict[pentry][24]-plane_dict[pentry][23]),1))+str(deg_html)+'</td>\n'

                            zapis2 += '<td>'+str(round(plane_dict[pentry][25],1))+'</td>\n'

                            zapis2 += '<td>'+str(sekundy2minsec(plane_dict[pentry][26]))+'</td>\n'

                            #countdown_licznik, footer = countdown_s(plane_dict[pentry][26], countdown_licznik)

                        else:
                            zapis2 += '<td> ---- </td>\n'

                            zapis2 += '<td> ---- </td>\n'

                            zapis2 += '<td> ---- </td>\n'

                        ##tu koniec2    
                        #wuersz += ' |'

                        thenx = plane_dict[pentry][0]
                        nowx = datetime.datetime.now()
                        diff_secx = (nowx - thenx).total_seconds()

                        zapis2 += '<td>'+str(round(diff_secx, 1))+'</td>\n'

                        if plane_dict[pentry][17] != "":
                            thenx1 = plane_dict[pentry][17]
                            nowx1 = datetime.datetime.now()
                            diff_secx1 = (nowx1 - thenx1).total_seconds()

                            zapis2 += '<td>'+str(round(diff_secx1, 1))+'</td>\n'
                        else:
                            zapis2 += '<td>-----</td>\n'

                        if (plane_dict[pentry][30] != 0 and plane_dict[pentry][30] != '' and footer == ''):
                            if int(plane_dict[pentry][30]) == 3:

                                if int(plane_dict[pentry][31]) < 2:
                                    plane_dict[pentry][31] = int(plane_dict[pentry][31]) + 1
                                    # in_range.mp3
                                    footer += '''<script>var audioElementinrange = new Audio('in_range.mp3');
                                                audioElementinrange.addEventListener('loadeddata', () => { let duration = audioElementinrange.duration; })
                                                audioElementinrange.play();</script>'''
                                    #new_in_range.mpe
                                    #footer += '''<script>var audioElementnewinrange = new Audio('new_in_range.mp3');
                                    #            audioElementnewinrange.addEventListener('loadeddata', () => { let duration = audioElementnewinrange.duration; })
                                    #            audioElementnewinrange.play();</script>'''
                                    #
                                else:
                                    plane_dict[pentry][30] = 0
                                    plane_dict[pentry][31] = 0

                            elif int(plane_dict[pentry][30]) == 2:

                                if int(plane_dict[pentry][31]) < 2:
                                    plane_dict[pentry][31] = int(plane_dict[pentry][31]) + 1
                                    # incoming.mp3
                                    footer += '''<script>var audioElementincoming = new Audio('incoming.mp3');
                                                audioElementincoming.addEventListener('loadeddata', () => { let duration = audioElementincoming.duration; })
                                                audioElementincoming.play();</script>'''

                                else:
                                    plane_dict[pentry][31] = 0
                                    plane_dict[pentry][30] = 0

                            elif int(plane_dict[pentry][30]) == 1:
                                if int(plane_dict[pentry][31]) < 2:
                                    plane_dict[pentry][31] = int(plane_dict[pentry][31]) + 1
                                    # new_in_range.mpe
                                    footer += '''<script>var audioElementnewinrange = new Audio('new_in_range.mp3');
                                                audioElementnewinrange.addEventListener('loadeddata', () => { let duration = audioElementnewinrange.duration; })
                                                audioElementnewinrange.play();</script>'''

                                    #footer += '''<script>var audioElementincoming = new Audio('incoming.mp3');
                                    #            audioElementincoming.addEventListener('loadeddata', () => { let duration = audioElementincoming.duration; })
                                    #            audioElementincoming.play();</script>'''

                                else:
                                    plane_dict[pentry][30] = 0
                                    plane_dict[pentry][31] = 0

                        #zapis2 += '<td class="rrtext">'+str(plane_dict[pentry][30])+'</td>\n<td>'+str(plane_dict[pentry][31])+'</td>\n'

                        #print( wiersz)
                        #rint('8', plane_dict[pentry][8],'9',plane_dict[pentry][9],'12',plane_dict[pentry][12],plane_dict[pentry][5],plane_dict[pentry][10] )
                        # next 4 lines data for txt transit history
                        #if transit_history_log == 1:
                        #    if ((-transit_separation_REDALERT_FG < separation_deg2 < transit_separation_REDALERT_FG) and obj_B_alt > minimum_alt_transits)  or ((-transit_separation_REDALERT_FG < separation_deg < transit_separation_REDALERT_FG) and obj_A_alt > minimum_alt_transits):
                        #        with open(transit_history_log_path,'a') as tra_txt:
                        #            trans_wiersz = str(plane_dict[pentry][0])+wiersz+'\n'
                        #            tra_txt.write(str(trans_wiersz))

                        zapis=str(pentry)+','+str(plane_dict[pentry][1])+','+str(plane_dict[pentry][2])+','+\
                        str(plane_dict[pentry][3])+','+str(plane_dict[pentry][4])+','+str(plane_dict[pentry][5])+','+\
                        str(plane_dict[pentry][6])+','+str(plane_dict[pentry][7])+','+str(plane_dict[pentry][8])+','+\
                        str(plane_dict[pentry][9])+','+str(plane_dict[pentry][10])+','+str(plane_dict[pentry][11])+','+\
                        str(plane_dict[pentry][12])+','+str(plane_dict[pentry][13])+','+str(plane_dict[pentry][14])+','
                        for ii,e in enumerate(plane_dict[pentry][15]):
                            zapis += str(plane_dict[pentry][15][ii])+';'
                        zapis += ','
                        for ii,e in enumerate(plane_dict[pentry][16]):
                            zapis += str(plane_dict[pentry][16][ii])+';'
                        zapis += ','
                        zapis += str(plane_dict[pentry][17])+','+str(datetime.datetime.now().strftime('%H:%M:%S'))+','

                        if (obj_A_alt > minimum_alt_transits):
                            zapis += str(plane_dict[pentry][27])+','+str(separation_deg)+','+str(obj_A_az)+','+str(plane_dict[pentry][24])+','
                        else:
                            zapis += ''+','+''+','+''+','+''+','
                        if (obj_B_alt > minimum_alt_transits):
                            zapis += str(plane_dict[pentry][21])+','+str(separation_deg2)+','+str(obj_B_az)+','+str(plane_dict[pentry][19])+','
                        else:
                            zapis += ''+','+''+','+''+','+''+','

                        zapis += str(vm.name)+','+str(vs.name)+','+str(diff_seconds)+','
                        zapis += str(altitudeX)+','
                        zapis += '\n'
                        #with open('/tmp/out.txt','a') as tsttxtzap:
                        #    tsttxtzap.write(zapis)


                        #print(plane_dict[pentry][30])

                        with open(out_path,'a') as tsttxtzap:
                            tsttxtzap.write(zapis)

                else:
                    if plane_dict[pentry][17] != "":
                        then = plane_dict[pentry][17]
                        now = datetime.datetime.now()
                        diff_seconds = (now - then).total_seconds()
                    else:
                        diff_seconds = 999
                    if plane_dict[pentry][1] != "":
                        if str(plane_dict[pentry][1]) == str(HL[0].strip()):
                            zapis2 += '<tr id="'+str(plane_dict[pentry][1])+'" style="background-color: #104600">'
                        else:
                            zapis2 += '<tr id="'+str(plane_dict[pentry][1])+'"  >'

                        zapis2 +=  '<tdclass="ytext">'+str(plane_dict[pentry][1])+'</td>\n'
                        zapis2a += '$("#'+str(plane_dict[pentry][1])+'").click(function(){ var name = "'+str(plane_dict[pentry][1])+'"; $.ajax({ type: "POST", url: "phpy/lo15.php", data: {"name": name},  error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } });});\n'


                    else:
                        if str(pentry) == str(HL[0].strip()):
                            zapis2 += '<tr id="'+str(pentry)+'" style="background-color: #104600">'
                        else:
                            zapis2 += '<tr id="'+str(pentry)+'">'

                        zapis2 +=  '<td>'+str(pentry)+'</td>\n'                                                 ##flight
                        zapis2a += '$("#'+str(pentry)+'").click(function(){ var name = "'+str(pentry)+'"; $.ajax({ type: "POST", url: "phpy/lo15.php", data: {"name": name},  error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } });});\n'

                    if plane_dict[pentry][4] != "":
                        if is_float_try(plane_dict[pentry][4]):
                            elevation=int(plane_dict[pentry][4])    
                        else:
                            elevation=9999
                        zapis2 += '<td>'+str(elevation)+'</td>\n'

                    else:
                        zapis2 += '<td>---</td>\n'

                    if plane_dict[pentry][11] != "":
                        zapis2 += '<td>'+str(plane_dict[pentry][11])+'</td>\n'
                    else:
                        zapis2 += '<td>---</td>\n'

                    if plane_dict[pentry][5] != "":
                        zapis2 += '<td>'+str(plane_dict[pentry][5])+'</td>\n'

                    else:
                        zapis2 += '<td>---</td>\n'


                    zapis2 += '<td>---</td>\n'


                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'

                    if diff_seconds > 5:
                        zapis2 += '<td>&nbsp;!&nbsp;</td>\n'
                    else:
                        zapis2 += '<td>&nbsp;&nbsp;&nbsp;</td>\n'

                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'
                    
                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'


                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'
                    zapis2 += '<td>---</td>\n'

                    zapis2 += '<td>---</td>\n'

                    thenx = plane_dict[pentry][0]
                    nowx = datetime.datetime.now()
                    diff_secx = (nowx - thenx).total_seconds()
                    
                    zapis2 += '<td>'+str(round(diff_secx, 1))+'</td>\n'
                    

                    zapis2 += '<td>---</td>\n'
                
                    #print( wiersz)
                zapis2 += '</tr>\n'
                tsttxt.write(str(zapis2))

        last_line_tmp = str(print_lastline_html(diff_t))
        load1, load5, load15 = os.getloadavg()
        if 0. <= float(load1) < 1.:
            load_col='class="ctext">'+str(load1)+' '+str(load5)+' '+str(load15)
        elif 1. <= float(load1) < 2.:
            load_col='class="gtext">'+str(load1)+' '+str(load5)+' '+str(load15)
        elif 2. <= float(load1) < 3.:
            load_col='class="ytext">'+str(load1)+' '+str(load5)+' '+str(load15)
        elif 3. <= float(load1) < 4.:
            load_col='class="rtext">'+str(load1)+' '+str(load5)+' '+str(load15)
        elif float(load1) >= 4.:
            load_col='class="rrtext">'+str(load1)+' '+str(load5)+' '+str(load15)
        else:
            load_col='>'+str(load1)+' '+str(load5)+' '+str(load15)

        if os.path.isfile('/tmp/temp'):
            DataFileName='/tmp/temp'
            datafile=open(DataFileName, 'r')
            dataz=datafile.readlines()
            datafile.close()
            #print(dataz)
            dataz = dataz[0].split(' ')
            #print(dataz[1])
        else:
            dataz=[0.0, 0.0, 0.0]
        temperature = int(float(dataz[1]))
        #print(temperature)
        if 0 < temperature <= 30:
            temp_col=' class="ctext">'+str(dataz[1])+'C'
        elif 30 < temperature <= 40:
            temp_col=' class="gtext">'+str(dataz[1])+'C'
        elif 40 < temperature <= 50:
            temp_col=' class="ytext">'+str(dataz[1])+'C'
        elif 50 < temperature <= 60:
            temp_col=' class="otext">'+str(dataz[1])+'C'
        elif 60 < temperature > 70:
            temp_col=' class="rrtext">'+str(dataz[1])+'C'
        else:
            #print("x")
            temp_col='>'+str(dataz[1])+'C'

        corearm=round(float(dataz[2])/1000000,0)
               #plane_dict[pentry][4]

        zapis3 = '</table>\n<table style="background-color: #262626;"><th><td>'+last_line_tmp+'</td>\n<td '+str(temp_col)+'</td>\n<td>'+str(corearm)+'MHz</td>\n<td>Load avg: </td>\n<td '+str(load_col)+'</td>\n</th></table><script>'+str(zapis2a)+'</script>'+'\n'

        #print(last_line_tmp)
        if int(gen_term) == 0:
            print("Only HTML output active!")
            print(str(print_lastline(diff_t)))

        #tsttxt.write(str(zapis2))
        #footer = ''
        #footer = '''<script>var audioElementm = new Audio('sun.mp3');
        #                        audioElementm.addEventListener('loadeddata', () => { let duration = audioElementm.duration; })
        #                        var audioElement3 = new Audio('3.wav');
        #                        audioElement3.addEventListener('loadeddata', () => { let duration = audioElement3.duration; })
        #                        var audioElementmin = new Audio('Minutes.wav');
        #                        audioElementmin.addEventListener('loadeddata', () => { let duration = audioElementmin.duration; });'''
        #footer += 'audioElementm.play(); sleep(700).then(() => {;'
        #footer += 'audioElement3.play(); sleep(700).then(() => {;audioElementmin.play();  }) })</script>'
        
        #print("fuuuuuuuuuuuuu",footer)
        footer_snd = str(header_snd)+ str(footer)+'</body></html>'

        #zapis3 += '<script>$("#call").click(function(){ $.ajax({ type: "POST", url: "phpy/lo15.php", data: "",  error: function(XMLHttpRequest, textStatus, errorThrown) { alert("Some error occured"); } });});</script>'

        footer_caly = str(zapis3) +'</body></html>'

        with open(out_path_html,'a') as tsttxt:
            tsttxt.write(str(footer_caly))
        
        if int(gen_html_snd) == 1:
            with open(out_path_html_snd,'w') as tsttxt:
                tsttxt.write(str(footer_snd))


    return obj_A_alt, obj_A_az, obj_B_alt, obj_B_az 

##########################################################################################################################################################
# koniecc Tabeli HTML
##########################################################################################################################################################

def print_lastline_html(diff_t):
    lastline='<td title="Last update time.">'+str(datetime.datetime.time(datetime.datetime.now()))+'</td>\n'
    lastline+= '<td>'+" --- "+'</td>\n'
    lastline+= '<td title="Dictionary size.">'+str(len (plane_dict))+'</td>\n'
    lastline+= '<td>'+" --- "+'</td>\n'
    lastline+= '<td title="Update frequency in seconds(?) 1 is pretty realtime.">'+str(int(diff_t))+'</td>\n'
    if ignore_pressure == 1:
        if ignore_my_elevation == 1:
            lastline+= '<td title="Pressure ignored! my_elevation ignored!" class="rtext">'+" === "+'</td>\n' #+ str(pressure)+"hPa"
        else:
            lastline+= '<td title="Pressure ignored! my_elevation active" class="ytext">'+" === "+'</td>\n' #+ str(pressure)+"hPa"
    else:
        if ignore_my_elevation == 1:
            lastline+= '<td title="Pressure corrections active but my_elevation ignored!" class="ytext">'+" >>> "+'</td>\n' #+ str(pressure)+"hPa"
        else:
            lastline+= '<td title="Pressure corrections active, my_elevation active." class="gtext">'+" >>> "+'</td>\n' #+ str(pressure)+"hPa"

    if (metar_active == 1 and ignore_pressure == 0):
        lastline+= '<td title="METAR pressure active, pressure corrections active." class="gtext">'+str(pressure)+"hPa"+'</td>\n'
    elif (metar_active == 0 and ignore_pressure == 1):
        lastline+= '<td title="METAR inactive and pressure ignored!" class="otext">'+str(pressure)+"hPa"+'</td>\n'
    elif (metar_active == 0 and ignore_pressure == 0):
        lastline+= '<td title="METAR inactive standart pressure." class="rtext">'+str(pressure)+"hPa"+'</td>\n'
    elif (metar_active == 1 and ignore_pressure == 1):
        lastline+= '<td title="Pressure from METAR but pressure ignored!" class="otext">!'+str(pressure)+"hPa"+'</td>\n'

    lastline+= '<td title="Script started at:">'+" Started: "+str(started)+'</td>\n' #+" Ago: "+str(aktual_txx)
    
    return lastline


def print_lastline(diff_t):
    lastline=str(datetime.datetime.time(datetime.datetime.now()))
    lastline+= " --- "
    lastline+= str(len (plane_dict))
    lastline+= " --- "
    lastline+= str(int(diff_t))
    if ignore_pressure == 1:
        if ignore_my_elevation == 1:
            lastline+= " --- "+RED+" === " #+ str(pressure)+RESET+"hPa"
        else:
            lastline+= " --- "+YELLOW+" === " #+ str(pressure)+RESET+"hPa"
    else:
        if ignore_my_elevation == 1:
            lastline+= " --- "+YELLOW+" >>> " #+ str(pressure)+RESET +"hPa"
        else:
            lastline+= " --- "+GREEN+" >>> " #+ str(pressure)+RESET +"hPa"

    if (metar_active == 1 and ignore_pressure == 0):
        lastline+= GREEN+str(pressure)+RESET+"hPa"+RESET
    elif (metar_active == 0 and ignore_pressure == 1):
        lastline+= RED+str(pressure)+RESET+"hPa"+RESET
    elif (metar_active == 0 and ignore_pressure == 0):
        lastline+= RED+str(pressure)+RESET+"hPa"
    elif (metar_active == 1 and ignore_pressure == 1):
        lastline+= RED+"!"+str(pressure)+RESET+"hPa"

    lastline+= " Started: "+str(started)#+" Ago: "+str(aktual_txx)
    return lastline


 # startowy przebieg bez danych, html tez tu ma byc? Chyba tylko pod vs.alt/az vm.alt/az
pressure = get_metar_press()
obj_A_alt, obj_A_az, obj_B_alt, obj_B_az = tabela_html()

#
# loop through all records from dump1090 port 10003 input stream on stdin
#
while True:
    line=sys.stdin.readline()
    aktual_t = datetime.datetime.now()
    if os.path.isfile('/tmp/fw_restart'):
        print("Restart in few seconds...")
        sys.exit()
    if line in ['\n', '\r\n']:
        plane_dict.clear()     # remove all entries in dict
        print( '' )
        with open(out_path_html,'w') as tsttxt:
            tsttxt.write('')

    else:
        #
        # divide input line into parts and extract desired values
        #
        parts = line.split(",")
        ## MLAT,3,1,1,484B31,1,2020/02/06,21:47:08.674,2020/02/06,21:47:08.674,,38993,441,93,52.4934,16.8546,45,,,,,,,,
        if parts[0] == '':
            print("No data, empty line/keep alive signal, go to sleep too...")
            time.sleep(5)
            break
        type = parts[1].strip()

        typemlat = parts[0].strip()
        icao = parts[4].strip()
        date = parts[6].strip()
        time = parts[7].strip()
        if (typemlat == "MLAT"):
            if int(time_corr_mlat) == 1:
                date_time_local = datetime.datetime.strptime(date + " " + time, '%Y/%m/%d %H:%M:%S.%f') + datetime.timedelta(minutes=minutes_add_mlat)
                #print('----')
            else:
                date_time_local = datetime.datetime.strptime(date + " " + time, '%Y/%m/%d %H:%M:%S.%f')
        else:
            if int(time_corr) == 1:
                #print('----')#minutes_add
                date_time_local = datetime.datetime.strptime(date + " " + time, '%Y/%m/%d %H:%M:%S.%f') + datetime.timedelta(minutes=minutes_add)
            else:
                #print('norm')
                date_time_local = datetime.datetime.strptime(date + " " + time, '%Y/%m/%d %H:%M:%S.%f')
        #date_time_iso = datetime.datetime.strftime(date_time_local, '%Y-%m-%dT%H:%M:%S.%f') + str("%+d" % (-timezone_hours)).zfill(3)

        #
        # check age of newest icao record, compare to newly-input value, and kill dictionary if too old (i.e. start fresh history)
        #
        if (icao in plane_dict):
            then = plane_dict[icao][0]
            now = datetime.datetime.now()
            diff_minutes = (now - then).total_seconds() / 60.
            # if (diff_minutes > alert_duplicate_minutes):
            if (diff_minutes > alert_duplicate_minutes):
                del plane_dict[icao]


        #
        # if type 1 record then extract datetime/flight and create or update dictionary
        #
        if (type == "1"): # this record type contains the aircraft 'flight' identifier
            flight = parts[10].strip()

            if (icao not in plane_dict): 
                plane_dict[icao] = [date_time_local, flight, "", "", "", "", "", "", "", "", "", "", "", "", "", [], [], "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0]
            else:
                plane_dict[icao][0] = date_time_local
                plane_dict[icao][1] = flight
        #
        # if type 5 flight elevation
        #
        if (type == "5"): 
            flight = parts[10].strip()
            elevation = parts[11].strip()
            if is_int_try(elevation):
                elevation=int(elevation)
                elevation = pressure_corr(elevation)

                if (metric_units):
                    elevation = float((elevation * 0.3048)) # convert elevation feet to meters
                else:
                    elevation = ""
            if (icao not in plane_dict): 
                plane_dict[icao] = [date_time_local, flight, "", "", elevation, "", "", "", "", "", "", "", "", "", "", [], [], "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0]
            else:
                plane_dict[icao][4] = elevation 
                plane_dict[icao][0] = date_time_local
                if flight != '':
                    plane_dict[icao][1] = flight

        #
        # if type 4 record then extract speed/track
        #
        if (type == "4"): # this record type contains the aircraft 'track' & 'velocity' identifier
            velocity = parts[12].strip()
            track = parts[13].strip()
            if is_int_try(velocity):
                velocity_kmh = round(int(velocity)*1.852)
            else:
                velocity_kmh = 900

            if (icao not in plane_dict):
                plane_dict[icao] = [date_time_local, "", "", "", "", "", "", "", "", "", "", track,  "", "", velocity,   [], [], "", "", "", "", "", "", "", "", "", "", "", "", "", 0,  0]

            else:
                plane_dict[icao][0] = date_time_local
                plane_dict[icao][11] = track
                plane_dict[icao][14] = velocity_kmh


        #
        # if type 3 record then extract datetime/elevation/lat/lon, calculate distance/azimuth/altitude, and create or update dictionary
        #
        if (type == "3"): # this record type contains the aircraft 'ICAO' identifier, lat/lon, and elevation
            elevation = parts[11].strip() # assumes dump1090 is outputting elevation in feet 
            if is_int_try(elevation):
                elevation=int(elevation)
                elevation = pressure_corr(elevation)

                if (metric_units):
                    elevation = float((elevation * 0.3048)) # convert elevation feet to meters

                else:
                    elevation = ""
                    elevation_units = "ft"
                    distance_units = "mi"

            try:
                plane_lat = float(parts[14])
            except:
                plane_lat = ''
                #pass
            try:
                plane_lon = float(parts[15])
            except:
                plane_lon = ''
                #pass
            #print(icao, plane_lat, plane_lon,track)
            if not plane_lat == '':
                if not plane_lon == '':
                    distance = float(round(haversine((my_lat, my_lon), (plane_lat, plane_lon)),1))
                    azimuth = atan2(sin(radians(plane_lon-my_lon))*cos(radians(plane_lat)), cos(radians(my_lat))*sin(radians(plane_lat))-sin(radians(my_lat))*cos(radians(plane_lat))*cos(radians(plane_lon-my_lon)))
                    azimuth = round(((degrees(azimuth) + 360) % 360),1)
                    if distance == 0:
                        distance = 0.01

                    # what with my_elevation ?! wtf?
                    #altitude = degrees(atan((elevation - my_elevation)/(distance*1000))) # distance converted from kilometers to meters to match elevation
                    altitude = degrees(atan((elevation)/(distance*1000))) # distance converted from kilometers to meters to match elevation
                    altitude = round(altitude,1)
                    if (icao not in plane_dict):
                        if (typemlat == "MLAT"):
                            track = parts[13].strip()
                            plane_dict[icao] = [date_time_local, "", plane_lat, plane_lon, elevation, float(distance), azimuth, altitude, "", "", float(distance), track, "", "", "", [], [], "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0]
                        else:
                            plane_dict[icao] = [date_time_local, "", plane_lat, plane_lon, elevation, float(distance), azimuth, altitude, "", "", float(distance), "", "", "", "",    [], [], "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0]
                        plane_dict[icao][15] = []
                        plane_dict[icao][16] = []
                        plane_dict[icao][15].append(azimuth)
                        plane_dict[icao][16].append(altitude)
                    else:
                        #
                        # figure out if plane is approaching/holding/receding
                        #
                        if not is_float_try(plane_dict[icao][5]):
                            #print( plane_dict[icao][5] )
                            if plane_dict[icao][5] == '':
                                plane_dict[icao][5] = float(distance)
                        if not is_float_try(plane_dict[icao][10]):
                            #print( plane_dict[icao][10] )
                            if plane_dict[icao][10] == '':
                                plane_dict[icao][10] = float(distance)

                        #print( plane_dict[icao][5] )
                        #print( plane_dict[icao][10])
                        #if not (plane_dict[icao][5] == '' or plane_dict[icao][10] == ''):
                        #distance = plane_dict[icao][10]
                        min_distance = plane_dict[icao][5]

                        if (distance < min_distance):
                            plane_dict[icao][9] = "APPROACHING"
                            #print("kupa")
                            #plane_dict[icao][10] = distance

                        elif (distance > min_distance):
                            plane_dict[icao][9] = "RECEDING"
                            #plane_dict[icao][10] = distance

                        else:
                            #plane_dict[icao][9] = "HOLDING"
                            plane_dict[icao][5] = float(distance)

                        if (typemlat == "MLAT"):
                            track = parts[13].strip()
                            plane_dict[icao][11] = track
                        else:
                            if parts[13].strip() != '':
                                plane_dict[icao][11] = track
                        plane_dict[icao][0] = date_time_local
                        plane_dict[icao][2] = plane_lat
                        plane_dict[icao][3] = plane_lon
                        plane_dict[icao][4] = elevation
                        plane_dict[icao][5] = distance
                        plane_dict[icao][6] = azimuth
                        plane_dict[icao][7] = altitude

                        if plane_dict[icao][17] == '':
                            plane_dict[icao][17] = date_time_local

                        then = plane_dict[icao][17]
                        now = datetime.datetime.now()
                        diff_seconds = (now - then).total_seconds()
                        if (diff_seconds > 6):

                            plane_dict[icao][17] = date_time_local

                            poz_az = str(plane_dict[icao][6])
                            poz_alt = str(plane_dict[icao][7])

                            plane_dict[icao][15].append(poz_az)
                            plane_dict[icao][16].append(poz_alt)

                        # Next lines - data for heatmaps
                        if heatmap_latlon_log == 1:
                            log_line = str(plane_lat)+","+str(plane_lon)+","+str(elevation)
                            with open("/tmp/_heatmap_asi.dat", 'a') as tsttxt:
                                tsttxt.write(log_line+",\n")

        # if matched record between type 1/3  occurs, log stats to stdout and also email if entering/leaving detection zone
        #
        # if ((type == "1" or type == "3" or type == "4") and (icao in plane_dict and plane_dict[icao][1] != "" and plane_dict[icao][2] != "" and plane_dict[icao][11] != "")):
        if ((type == "1" or type == "3" or type == "4") and (icao in plane_dict and plane_dict[icao][2] != "" and plane_dict[icao][11] != "")):

            flight             = plane_dict[icao][1]
            plane_lat          = plane_dict[icao][2]
            plane_lon          = plane_dict[icao][3]
            elevation          = plane_dict[icao][4]
            distance           = plane_dict[icao][5]
            azimuth            = plane_dict[icao][6]
            altitude           = plane_dict[icao][7]
            track              = plane_dict[icao][11]
            warning            = plane_dict[icao][12]
            direction          = plane_dict[icao][9]
            # elevation_feet     = int(round(int(round(elevation / 0.3048)/100)))
            velocity           = plane_dict[icao][14]
            xtd               = crosstrack(distance, (180 + azimuth) % 360, track)
            #print(flight, icao, plane_lat, plane_lon, track, distance)
            plane_dict[icao][13] = xtd

            if (xtd <= xtd_tst and distance < warning_distance and warning == "" and direction != "RECEDING"):
                plane_dict[icao][12] = "WARNING"
                plane_dict[icao][13] = xtd
                if detected_sound == 1: # not sure, looks like in detection zone without earlier warning
                    #plane_dict[icao][30] = 1
                    # new_in_range.mp3
                    gong()

            if (xtd > xtd_tst and distance < warning_distance and warning == "WARNING" and direction != "RECEDING"):
                plane_dict[icao][12] = ""
                plane_dict[icao][13] = xtd
                if detected_sound == 1: # pretty sure
                    # incoming.mp3 ? 
                    plane_dict[icao][30] = 2
                    gong() 

            if (plane_dict[icao][8] == ""):
                plane_dict[icao][8] = "LINKED!"

            #
            # if plane enters detection zone, send email and begin history capture
            #
            # if ((elevation <= 8000) and distance <= 30):
                # gong()

            if (plane_dict[icao][5] <= alert_distance and plane_dict[icao][8] != "ENTERING"):
                plane_dict[icao][8] = "ENTERING"
                if entering_sound == 1:
                    # in_range.mp3 ?
                    plane_dict[icao][30] = 3
                    gong()

            #
            # if plane leaves detection zone, generate email and include history capture
            #
            if (plane_dict[icao][5] > alert_distance and plane_dict[icao][8] == "ENTERING"):
                plane_dict[icao][8] = "LEAVING"

            
            if direction != "RECEDING":
                kosa = math.degrees(math.acos(float(xtd)/float(distance)))
                
                ####################################################################################################
                # copypasta start
                ####################################################################################################

                if 360 > int(azimuth) >= 270:
                    if (int(azimuth) - int(track)) > 180:
                        #AZM_case = 'a1'
                        AZM = int(azimuth) + kosa
                    else:
                        AZM = int(azimuth) - kosa
                        #AZM_case = 'a2'
                    '''
                    if 360 > int(azimuth) >= 270:
                    if int(track) < 180:
                        if (int(azimuth) - int(track)) < 180:
                            AZM = int(azimuth) - kosa
                        else:
                            AZM = int(azimuth) + kosa
                    else: # int(track) > 180
                        if (int(azimuth) - int(track)) > -180:
                            AZM = int(azimuth) + kosa
                        else:
                            AZM = int(azimuth) - kosa
                    '''
                elif 270 > int(azimuth) >= 180:
                    if int(track) > 180:
                        if (int(azimuth) - int(track)) < 0:
                            AZM = int(azimuth) + kosa
                            #AZM_case = 'b1' # ok
                        else:
                            AZM = int(azimuth) - kosa
                            #AZM_case = 'b2'
                    else: # int(track) < 180
                        if (int(azimuth) - int(track))  >180:
                            AZM = int(azimuth) + kosa
                            #AZM_case = 'b3' # ok
                        else:
                            AZM = int(azimuth) - kosa
                            #AZM_case = 'b4' # ok
        
                elif 180 > int(azimuth) >= 90:
                    if int(track) > 270:
                        if (int(azimuth) - int(track)) > -180:
                            AZM = int(azimuth) + kosa
                            #AZM_case = 'c1'
                        else:
                            AZM = int(azimuth) - kosa
                            #AZM_case = 'c2' # meh1
                    elif 0 < int(track) < 180:
                        AZM = int(azimuth) - kosa
                        #AZM_case = 'c3' #meh1 zmienione na +
                    else: # <270
                        #if (int(azimuth) - int(track)) < -180:
                        #    AZM = int(azimuth) + kosa
                        #    #AZM_case = 'c3a'
                        #else:
                        AZM = int(azimuth) + kosa
                        #AZM_case = 'c4' #meh1 zmienione na +
        
                elif 90 > int(azimuth) >= 0:
                    if int(track) > 180:
                        if (int(azimuth) - int(track)) > -180:
                            AZM = int(azimuth) + kosa
                            #AZM_case = 'd1'
                        else:
                            AZM = int(azimuth) - kosa
                            #AZM_case = 'd2'
                    else: # int(track) < 180
                        if (int(azimuth) - int(track)) > -180:
                            AZM = int(azimuth) + kosa
                            #AZM_case = 'd3'
                        else:
                            AZM = int(azimuth) - kosa
                            #AZM_case = 'd4'

                ####################################################################################################
                ### copypasta z AllSkyRadar - tam licz osobno az do 100% pewnosci potem updejt copypasta ponownie!
                ####################################################################################################

                dst2AZM = math.sqrt(float(distance)**2 - float(xtd)**2)
                if not velocity == '':
                    velocity = int(velocity)
                    sure_vel='= '
                else:
                    velocity = 900 # only used for transit countdown
                    sure_vel='~ '
                delta_seconds = (dst2AZM / velocity)*3600
                delta_minutes = delta_seconds // 60
                if delta_minutes >= 1:
                    delta_AZM = '%02dm%02ds' % (delta_minutes, delta_seconds % 60)
                else:
                    delta_AZM = '%02s %02ds' % ("  ", delta_seconds % 60)
                plane_dict[icao][28] = (int(AZM) % 360) # to tylko diff, trzeba przeniesc cale warunkowanie aktualny azi vs track, pfff :/
                plane_dict[icao][29] = str(delta_AZM)
            else:
                #plane_dict[icao][28] = azimuth
                plane_dict[icao][28] = int(azimuth) # rough round
                plane_dict[icao][29] = "gone"
                plane_dict[icao][13] = distance
                #print()
                #print(round(kosa,1), delta_AZM)

            ## Transit check
            tst_int1 = transit_pred((my_lat, my_lon), (plane_lat, plane_lon), track, velocity, elevation, obj_A_alt, obj_A_az)
            tst_int2 = transit_pred((my_lat, my_lon), (plane_lat, plane_lon), track, velocity, elevation, obj_B_alt, obj_B_az)

            if tst_int1 == 0:
                #if (plane_dict[icao][23] == ''):
                alt_a = 90.0 # obj_A_alt
                dst_p2x = 996
                delta_time = 0
                dst_h2x = 998
                plane_dict[icao][23] = 999.0         ## MOON ALT
                plane_dict[icao][24] = alt_a
                plane_dict[icao][25] = dst_h2x        ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                plane_dict[icao][26] = delta_time 
                plane_dict[icao][27] = dst_p2x         ## dst_p2x        ## DISTANCE PLANE TO MOON AZIMUTH (CROSS)    
            else:
                alt_a     = round(tst_int1[3],2)          ##    altitude1    ## ALT OF CROSS POINT
                dst_h2x = round(tst_int1[4],2)      ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                dst_p2x = round(tst_int1[5],2)          ## dst_p2x        ## DISTANCE PLANE TO MOON AZIMUTH (CROSS)
                delta_time = int(tst_int1[6])         ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROSS POINT
                plane_dict[icao][25] = dst_h2x        ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                plane_dict[icao][23] = obj_A_alt
                plane_dict[icao][24] = alt_a 
                plane_dict[icao][26] = delta_time 
                plane_dict[icao][27] = dst_p2x         ## dst_p2x        ## DISTANCE PLANE TO MOON AZIMUTH (CROSS)    

                if is_float_try(plane_dict[icao][24]) and is_float_try(plane_dict[icao][23]):
                    separation_deg = round(float(plane_dict[icao][24]-plane_dict[icao][23]),1)
                else:
                    separation_deg = 90.0
                if (-transit_separation_sound_alert < separation_deg < transit_separation_sound_alert):
                    if (sun_tr_sound == 1 and obj_A_alt > minimum_alt_transits): # cos tu jest na odwrot
                        gong() # SUN!!!
                        #pass

            if tst_int2 == 0:
                #if (plane_dict[icao][23] == ''):
                alt_a = 90.0 # obj_A_alt
                dst_p2x = 996
                delta_time = 0
                dst_h2x = 998
                plane_dict[icao][18] = 999.0        ## SUN ALT
                plane_dict[icao][19] = alt_a 
                plane_dict[icao][20] = dst_h2x        ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                plane_dict[icao][22] = delta_time 
                plane_dict[icao][21] = dst_p2x         ## dst_p2x        ## DISTANCE PLANE TO SUN AZIMUTH (CROSS)    

            else:
                alt_a     = round(tst_int2[3],2)         ##    altitude1    ## ALT OF CROSS POINT
                dst_h2x = round(tst_int2[4],2)      ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                dst_p2x = round(tst_int2[5],2)          ## dst_p2x        ## DISTANCE PLANE TO SUN AZIMUTH (CROSS)
                delta_time = int(tst_int2[6])         ## delta_tim    ## TIME UNTIL PLANE ARRIVE AT CROSS POINT
                plane_dict[icao][20] = dst_h2x        ## dst_h2x        ## DISTANCE MY_POS TO CROSS POINT
                plane_dict[icao][18] = obj_B_alt
                plane_dict[icao][19] = alt_a 
                plane_dict[icao][22] = delta_time 
                plane_dict[icao][21] = dst_p2x         ## dst_p2x        ## DISTANCE PLANE TO SUN AZIMUTH (CROSS)    

                if is_float_try(plane_dict[icao][19]) and is_float_try(plane_dict[icao][18]):
                    separation_deg2 = round(float(plane_dict[icao][19]-plane_dict[icao][18]),1)
                else:
                    separation_deg2 = 90.0
                if (-transit_separation_sound_alert < separation_deg2 < transit_separation_sound_alert):
                    if (moon_tr_sound == 1 and obj_B_alt > minimum_alt_transits): # cos tu jest na odwrot
                        gong()
                        #pass

    if int(gen_html) == 1:
        obj_A_alt, obj_A_az, obj_B_alt, obj_B_az = tabela_html()
        if int(gen_term) == 1:
            tabela_terminal()
    else:
        if int(gen_term) == 1:
            obj_A_alt, obj_A_az, obj_B_alt, obj_B_az = tabela_terminal()

    clean_dict()
