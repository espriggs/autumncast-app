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
st.write('test update')

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
