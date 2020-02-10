import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import pickle
import datetime
from datetime import date
import calendar
import rasterio
import requests
import urllib
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from shapely.geometry import Point
from matplotlib.lines import Line2D
import re
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
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmin.append(val-273.15)

    #pull data for that location, that year
    with rasterio.open("tasmax_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif") as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): tmax.append(val-273.15)

    #pull data for that location, that year
    with rasterio.open("pr_day_CCSM4_rcp85_r6i1p1_20200101-20201231_clipped.tif") as raster:
        for val in raster.sample([(x, y)], indexes = range(1,day_of_year+1)): ppt.append(val*24*60*60)

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

#Read in the model file from a pickle file:
pkl_filename = 'rf_2020_model_12_features.pkl'
with open(pkl_filename, 'rb') as file:
    pickle_model = pickle.load(file)

NE4 = gpd.read_file('NE4.shp')

st.title('Autumncast')

#create some default locations for a dropdown menu:
select = st.selectbox('Select a location:', ['Cambridge, MA', 'Providence, RI', 'Lee, MA', 'Baxter, Maine', 'Burlington, VT', 'Hanover, NH'])
city_list = pd.read_csv('backup_city_list.csv', sep='\t')
city_list = pd.read_csv('backup_city_list.csv', sep='\t')
y = float(city_list[city_list.City == select].Latitude)
x = float(city_list[city_list.City == select].Longitude)

#for these dropdown menu options, provide some lat lons:
#this is necessary because sometimes geocoder goes down:
user_input = st.text_input("Or try searching one here:", "")
if user_input == '':
    user_input = select
else:
    geolocator = Nominatim(user_agent="my-application")
    try:
        location = geolocator.geocode(user_input)
        #print('Coordinates: ', location.latitude, location.longitude)
        x = location.longitude
        y = location.latitude
        r = re.compile(r'\bRhode\b | \bConnecticut\b | \bMaine\b | \bHampshire\b | \bVermont\b | \bMassachusetts\b', flags=re.I | re.X)
        found = r.findall(str(location))
        if len(found) == 0:
            st.write("That location wasn't found. Try another place in New England.")
            x = 0
            y = 0
    except:
        st.write("Sorry, the feature we use to find locations isn't working right now. Try picking an option from the drop down menu or try again later.")
        x = 0
        y = 0



if y > 0:

    #In order to find the dominant species near the given location,
    #Find the FIP code for the location
    #Encode parameters that are used for the query:
    params = urllib.parse.urlencode({'latitude': y, 'longitude':x, 'format':'json'})
    #Contruct request URL
    url = 'https://geo.fcc.gov/api/census/block/find?' + params
    #Get response from API
    response = requests.get(url)
    #Parse json in response
    data = response.json()

    #For that FIPS code, look up the dominant species in the table made from FIA data
    #then print that value for the user (could be extended to show more than one species)
    fips = data['County']['FIPS']
    deciduous_single = pd.read_csv('Single_deciduous_county.csv')

    #not all of the counties have FIA plots, for those, do not print a species to the screen
    if any(deciduous_single.COUNTYFIP.astype(str).str.contains(fips)):
        tree = deciduous_single[deciduous_single.COUNTYFIP == int(fips)].Dominant_Species
        st.write('The dominant deciduous tree species near ',user_input ,' is ', tree.to_string(index = False), '.', sep='')

    #Use the function from above to get the relevant features for the model:
    values = foliage_prediction_2020(x, y)

    #Convert these values into inputs for the model:
    #select only the features in the model (var1, var6, var7, var8, var10)
    model_in = [values[0], values[5], values[6], values[7], values[9], '0', '0', '0', '0', '0', '0', '0']
    #create a dictionary to replace the right values according to which species is dominant in that area
    dict = {' American beech':5, ' flowering dogwood':6, ' northern red oak':7, ' red maple':8, ' sugar maple':9, ' white ash':10, ' white oak':11}
    model_in[dict[tree.to_string(index = False)]] = "1"

    prediction = pickle_model.predict(np.array(model_in).reshape(1,-1))[0]
    start_date = prediction - 7
    end_date = prediction + 7

    start_month = pd.to_datetime(start_date, format = '%j').month
    start_day = pd.to_datetime(start_date, format = '%j').day

    end_month = pd.to_datetime(end_date, format = '%j').month
    end_day = pd.to_datetime(end_date, format = '%j').day

    st.write('The best fall color in', user_input, ' will be between:')
    st.write(calendar.month_name[start_month], str(start_day), str(2020), 'and', calendar.month_name[end_month], str(end_day), str(2020))


    # ##################################################################
    ## Plot a heatmap

    prediction_date = pd.to_datetime(prediction, format = '%j')
    prediction_date = prediction_date.replace(year = 2020)
    User_input_day = st.date_input('Change this date to see a map for a different date:', prediction_date)
    User_input_day = User_input_day.timetuple().tm_yday
    #User_input_day = st.slider('Day of the year', 200, 365, int(prediction))
    #st.write(str(User_input_day), 'is ', calendar.month_name[pd.to_datetime(User_input_day, format = '%j').month], str(pd.to_datetime(User_input_day, format = '%j').day), '2020')
    #NE4.head()

    #create a custom color list that varies based on the user input:
    colors_list = np.repeat('lightgrey', 9, axis = 0)
    dates = [270, 275, 280, 285, 290, 295, 300, 305, 310]
    i = 0
    for date in dates:
       # print(User_input_day-date)
        if (User_input_day-date <= 14) & (User_input_day-date >= 7):
            colors_list[i] = 'darkred'
        if (User_input_day-date <= 7) & (User_input_day-date >= -7):
            colors_list[i] = 'red'
        if (User_input_day-date >= -14) & (User_input_day-date <= -7):
            colors_list[i] = 'orange'
        if (User_input_day-date >= -21) & (User_input_day-date <= -14):
            colors_list[i] = 'goldenrod'
        i +=1

    #color_list = ['darkred','darkred','darkred','red','red','red','orange','orange','lightgrey']
    colormap = []
    colormap = LinearSegmentedColormap.from_list([270, 275, 280, 285, 290, 295, 300, 305, 310],colors_list)

    add_point = Point((x,y))
    gdf_am = gpd.GeoSeries([add_point], crs={'init': 'epsg:4326'})

    fig, ax = plt.subplots(figsize=(8,8))
    NE4.plot(ax=ax, column = 'predicted', cmap = colormap)
    gdf_am.to_crs({'init': 'epsg:4326'}).plot(ax=ax, markersize = 150, marker = '*')

    #ax = NE3.plot(column = 'predicted', cmap = colormap)
    #legend_labels = {'goldenrod':'very early','orange':'early', 'red': 'peak', 'darkred':'late'}
    legend_elements = [Patch(facecolor = 'lightgrey', edgecolor ='w', label = 'No fall color'),
                        Patch(facecolor = 'goldenrod', edgecolor ='w', label = 'Very early'),
                       Patch(facecolor = 'orange', edgecolor ='w', label = 'Early'),
                       Patch(facecolor = 'red', edgecolor ='w', label = 'Peak'),
                       Patch(facecolor = 'darkred', edgecolor ='w', label = 'Late'),
                       Line2D([0],[0], marker = '*',
                        color ='w', markerfacecolor='cornflowerblue',
                        label = user_input, markersize=20)]
    ax.legend(handles=legend_elements,
              bbox_to_anchor=(.3, .97),
              facecolor="white",
              frameon = False)
    st.pyplot()
