# Using Weather Data
#
# Wesbite

import requests
import json

def get_current_weather(gps_coord):
    
    API_KEY = '2862f4116ca55cb42c41cb9ea03711b0'
    forecast_addr = "http://api.openweathermap.org/data/2.5/weather/"
    current_addr = "http://api.openweathermap.org/data/2.5/forecast/"
    
    