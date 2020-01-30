import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import pickle
from datetime import datetime
from datetime import date
import calendar
import rasterio
import requests
import urllib

########################################################################
# Read in useful functions
#######################################################################
#daylength function from: https://gist.github.com/anttilipp/ed3ab35258c7636d87de6499475301ce
def daylength(dayOfYear, lat):
    """Computes the length of the day (the time between sunrise and
    sunset) given the day of the year and latitude of the location.
    Function uses the Brock model for the computations.
    For more information see, for example,
    Forsythe et al., "A model comparison for daylength as a
    function of latitude and day of year", Ecological Modelling,
    1995.
    Parameters
    ----------
    dayOfYear : int
        The day of the year. 1 corresponds to 1st of January
        and 365 to 31st December (on a non-leap year).
    lat : float
        Latitude of the location in degrees. Positive values
        for north and negative for south.
    Returns
    -------
    d : float
        Daylength in hours.
    """
    latInRad = np.deg2rad(lat)
    declinationOfEarth = 23.45*np.sin(np.deg2rad(360.0*(283.0+dayOfYear)/365.0))
    if -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0:
        return 24.0
    elif -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0:
        return 0.0
    else:
        hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
        return 2.0*hourAngle/15.0

#feature engineering required for user input locations:
def foliage_prediction_2020(x, y):
    tmin = []
    tmax = []
    ppt = []
    year = 2020
#    st.write('predicting for: ', x, y, 'in ', year)
    if calendar.isleap(year):
        day_of_year = 366
        Fdays = 29
    else:
        day_of_year = 365
        Fdays = 28

    #pull data for that location, that year
    with rasterio.open("tasmin_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif") as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmin.append(val)

    #pull data for that location, that year
    with rasterio.open("tasmax_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif") as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmax.append(val)

    #pull data for that location, that year
    with rasterio.open("pr_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif") as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): ppt.append(val)

    #Get the day of the first frost:
    below_zero = np.where(tmin[0] < 0)
    try:
        first_frost = below_zero[0][below_zero[0] > 200][0]
    except:
        first_frost = day_of_year
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


########################################################################
# The actual app part
#######################################################################

st.title('Autumcast')

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

#get the county FIP code for that location:

#Encode parameters
params = urllib.parse.urlencode({'latitude': y, 'longitude':x, 'format':'json'})
#Contruct request URL
url = 'https://geo.fcc.gov/api/census/block/find?' + params

#Get response from API
response = requests.get(url)

#Parse json in response
data = response.json()
#Get FIPS code, print dominant species
fips = data['County']['FIPS']
deciduous_single = pd.read_csv('Single_deciduous_county.csv')
tree = deciduous_single[deciduous_single.COUNTYFIP == int(fips)].Dominant_Species

st.write('The dominant deciduous tree species near ',user_input ,' is ', tree.to_string(index = False), '.', sep='')

pkl_filename = 'rf_2020_model.pkl'
with open(pkl_filename, 'rb') as file:
    pickle_model = pickle.load(file)

values = foliage_prediction_2020(x, y)

#st.write(values)

model_in = [values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8], values[9], '0', '0', '0', '0', '0']
#st.write(model_in)

prediction = pickle_model.predict(np.array(model_in).reshape(1,-1))[0]
start_date = prediction - 5
end_date = prediction + 5

start_month = pd.to_datetime(start_date, format = '%j').month
start_day = pd.to_datetime(start_date, format = '%j').day

end_month = pd.to_datetime(end_date, format = '%j').month
end_day = pd.to_datetime(end_date, format = '%j').day


st.write('The best fall color will be between:')
st.write(calendar.month_name[start_month], start_day, 2020, 'and', calendar.month_name[end_month], end_day, 2020)
