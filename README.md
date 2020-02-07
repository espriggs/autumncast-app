# Autumncast-App

Autumncast is a tool for predicting peak fall foliage dates based on climate and weather data. A web version of the app is available at:
https://secure-stream-96026.herokuapp.com/). This repository contains all of the files necessary to run the app, but data cleaning and modeling notebooks can be found in the autumncast-modeling (https://github.com/espriggs/autumncast-modeling) repository.

Below is an overview of the steps Autumncast takes to make fall foliage predictions:
#### 1. Collect a user input location and translate the location to latitude and longitude. 
Autumncast uses geocoder from geopy to query the Nomatim API and retrieve latitude and longitude data. Sometimes this service is unavailable and a few cities in New England are included in "backup_city_list.csv" so that the app will still run in these cases.
#### 2. For the input location, look up the dominant deciduous species in that region. 
Get the county FIP code, use that to look up what the most common deciduous species is using the table, "Single_deciduous_county.csv". For full details on how this table was created see the data_cleaning.ipynb in autumncast-modeling.
#### 3. Retrieve daily climate data and calculate the features necessary for the model. 
Autumncast next retrieves daily 2020 climate data from clipped raster files. These data are from the CMIP5 models using CCSM4 model for the higher emissions scenario. 
#### 4. Run the model.
The next step is to use the pre-trained model to make a prediction for the given location.
#### 5. Plot a heatmap that maches the model.
Finally, autumncast plots a heat map that corresponds to the predicted optimal day. The heatmap is composed of townships for each state in New England, each colored based on the estimated peak fall date for the township centroid. 


More to do here . . .
### Prerequisites

conda env export --name ENVNAME > envname.yml
conda env create --file envname.yml

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo


## Authors

Elizabeth Spriggs

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

