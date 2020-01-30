import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import pickle
from datetime import datetime
from datetime import date
import calendar
import rasterio


st.title('Autumcast Version 1')

user_input = st.text_input("Which location do you want to search? Enter a location like 'Burlington, Vermont'", "Burlington, VT")
#st.write(user_input)
geolocator = Nominatim(user_agent="my-application")
try:
    location = geolocator.geocode(user_input)
    #print(loc.raw)
    print('Coordinates: ', location.latitude, location.longitude)
    st.write("Found: ", location)
except:
    st.write("Couldn't find this location. Try a different town name?")
    location = geolocator.geocode('Burlington, Vermont')
x = location.longitude
y = location.latitude

def foliage_prediction_2020(x, y):
    tmin = []
    tmax = []
    ppt = []
    year = '2020'
#    st.write('predicting for: ', x, y, 'in ', year)
    if calendar.isleap(year):
        day_of_year = 366
        Fdays = 29
    else:
        day_of_year = 365
        Fdays = 28

    #pull data for that location, that year
    with rasterio.open("/Users/elizabethspriggs/Insight/Foliage/Datasheets/stacked_PRISM/tmin_{}.bil".format(year)) as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmin.append(val)

    #pull data for that location, that year
    with rasterio.open("/Users/elizabethspriggs/Insight/Foliage/Datasheets/stacked_PRISM/tmax_{}.bil".format(year)) as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmax.append(val)

    #pull data for that location, that year
    with rasterio.open("pr_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif".format(year)) as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): ppt.append(val)

    #Get the day of the first frost:
    below_zero = np.where(tmin[0] < 0)
    first_frost = below_zero[0][below_zero[0] > 200][0]
    var1 = first_frost

    #Get the day of the fifth frost:
    below_zero = np.where(tmin[0] < 0)
    try:
        fifth_frost = below_zero[0][below_zero[0] > 200][4]
    except:
        fifth_frost = day_of_year
    var2 = fifth_frost

    #Average minimum temperature in September:
    start = date(year=year, month=9, day=1)
    end = date(year=year, month=9, day=30)
    S_tmp = tmin[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var3 = S_tmp

    #Average minimum temperature in October:
    start = date(year=year, month=10, day=1)
    end = date(year=year, month=10, day=31)
    O_tmp = tmin[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var4 = O_tmp

    #Average minimum temperature in November:
    start = date(year=year, month=11, day=1)
    end = date(year=year, month=11, day=30)
    N_tmp = tmin[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var5 = N_tmp

    #Average maximum temperature in July and August:
    start = date(year=year, month=7, day=1)
    end = date(year=year, month=8, day=31)
    JA_max = tmax[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var6 = JA_max

    #Average precipitation in July and August:
    start = date(year=year, month=7, day=1)
    end = date(year=year, month=8, day=31)
    JA_ppt = ppt[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var7 = JA_ppt

    #Average precipitation in September:
    start = date(year=year, month=9, day=1)
    end = date(year=year, month=9, day=30)
    S_ppt = ppt[0][start.timetuple().tm_yday:end.timetuple().tm_yday].mean()
    var8 = S_ppt

    #Daylength of September 1st
    start = date(year=year, month=9, day=1)
    day = start.timetuple().tm_yday
    var9 = daylength(day, y)

    #Daylength of November 1st
    start = date(year=year, month=11, day=1)
    day = start.timetuple().tm_yday
    var10 = daylength(day, y)

    return(var1, var2, var3, var4, var5, var6, var7, var8, var9, var10)
st.write(foliage_prediction_2020(x, y, '2020'))
