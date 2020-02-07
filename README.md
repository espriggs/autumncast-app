# Autumncast-App

Autumncast is a tool for predicting peak fall foliage dates based on climate and weather data. A web version of the app is available at:
https://secure-stream-96026.herokuapp.com/). This repository contains all of the files necessary to run the app, but data cleaning and modeling notebooks can be found in the autumncast-modeling (https://github.com/espriggs/autumncast-modeling) repository.

Below is an overview of the steps Autumncast takes to make fall foliage predictions:
#### 1. Collect a user input location translate the location to latitude and longitude. 
Autumncast uses geocoder from geopy to query the Nomatim API and retrieve latitude and longitude data. Sometimes this service is unavailable and a few cities in New England are included in "backup_city_list.csv" so that the app will still run in these cases.
#### 2. For this location look up the dominant deciduous species in that region. 
Get the county FIP code, use that to look up in a table, "Single_deciduous_county.csv" what the most common deciduous species is. For full details on how this table was created see the data_cleaning.ipynb in autumncast-modeling.
#### 3. Retrieve daily climate data and calculate the features necessary for the model. 
#### 4. Run the model.
#### 5. Plot a heatmap that maches the model.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

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

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system



## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
