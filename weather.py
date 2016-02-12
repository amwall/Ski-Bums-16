# Using Weather Data
#
# Wesbite

import requests
import json

# API Quick Facts
#   Limits:
#       60 per minute
#       50,000 per day
#   Products:
#       Current Weather
#       5Day/3 hour Forecast
#       Weather Maps

# 

def get_current_weather(gps_coord):
    
    API_KEY = "&APPID=" + '2862f4116ca55cb42c41cb9ea03711b0'
    forecast_addr = "http://api.openweathermap.org/data/2.5/weather/city?"
    current_addr = "http://api.openweathermap.org/data/2.5/forecast/city?"
    
    # Example Call
    # http://api.openweathermap.org/data/2.5/weather?q=seattle&units=imperial&APPID=2862f4116ca55cb42c41cb9ea03711b0
    #
    # {"coord":{"lon":-122.33,"lat":47.61},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],
    #"base":"cmc stations","main":{"temp":48.84,"pressure":1021.49,"humidity":97,"temp_min":48.84,"temp_max":48.84,
    #"sea_level":1032.43,"grnd_level":1021.49},"wind":{"speed":5.57,"deg":137.5},"rain":{"3h":0.445},"clouds":{"all":76},
    #"dt":1455290504,"sys":{"message":0.0039,"country":"US","sunrise":1455290363,"sunset":1455326902},"id":5809844,
    #"name":"Seattle","cod":200}
    
    # Daily Forecast Example
    #     {"cod":"200","message":0.0032,
    # "city":{"id":1851632,"name":"Shuzenji",
    # "coord":{"lon":138.933334,"lat":34.966671},
    # "country":"JP"},
    # "cnt":10,
    # "list":[{
    #     "dt":1406080800,
    #     "temp":{
    #         "day":297.77,
    #         "min":293.52,
    #         "max":297.77,
    #         "night":293.52,
    #         "eve":297.77,
    #         "morn":297.77},
    #     "pressure":925.04,
    #     "humidity":76,
    #     "weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],}
    #         ]}

    
    