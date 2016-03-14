# weather.py
# Gareth Jones
# 
# API Quick Facts
# Website: openweathermap.org
#   Limits:
#       60 per minute actually more like 1 per second
#       50,000 per day
#   Products:
#       Current Weather
#       7 Day Forecast
#
#  Full run time ~ 15 minutes

import sqlite3 as lite
import csv
import requests
import json
from time import sleep
from database import csv_writer, csv_reader
import sys

API_KEY = "&APPID=2862f4116ca55cb42c41cb9ea03711b0"

def query_resorts(db_name):

    conn = lite.connect(db_name)
    c = conn.cursor()
    query = "SELECT ID, zip FROM main"
    resorts = c.execute(query)
    conn.commit()
    return resorts


def get_current(db_name, output_file):
    '''
    This function gathers the current weather conditions for all of the resorts
    in our database and writes a csv containing all of the data
    '''

    zip_url = "http://api.openweathermap.org/data/2.5/weather?zip={},us"

    resort_loc = query_resorts(db_name)

    cnt = 0
    weather_data = []
    for ID, z_code in resort_loc:
        sleep(1.1) # Slow down to prevent API lockout
        req_addr = zip_url.format(z_code) + "&units=imperial" + API_KEY
        # Attempt to resolve faulty database connection
        try:
            r = requests.get(req_addr)
        except ConnectionError:
            sleep(5)
            r = requests.get(req_addr)

        json_str = r.text
        weather = json.loads(json_str)
        wthr = weather['weather'][0]['main']
        dscr = weather['weather'][0]['description']
        temp = weather['main']['temp']
        pres = weather['main']['pressure']
        humd = weather['main']['humidity']
        spd = weather['wind']['speed']

        if 'rain' in weather:
            rain = weather['rain']
            if '3h' in rain:
                rain = rain['3h']
        else:
            rain = 0

        if 'snow' in weather:
            snow = weather['snow']
            if '3h' in snow:
                snow = snow['3h']
        else:
            snow = 0

        data = [ID, wthr, dscr, temp, pres, humd, spd, rain, snow]
        weather_data.append(data)

    labels = ["ID", 'wthr', 'dscr', "temp", "pres", "humd", "spd", "rain", "snow"]
    
    csv_writer(labels, weather_data, output_file)

def get_forecast(db_name, output_file):

    '''
    This function gathers the seven day forecast for all of the resorts
    in our database and writes a csv containing all of the data
    '''

    zip_url = "http://api.openweathermap.org/data/2.5/forecast/daily?zip={},us"

    NUM_DAYS = 7

    labels = ['ID']
    # Build column headers for every day and field of interest
    for day_num in range(NUM_DAYS):
        fields = "wthr_{d} dscr_{d} avg_day_{d} avg_night_{d} \
                  t_min_{d} t_max_{d} pres_{d} humd_{d} w_spd_{d} \
                  rain_{d} snow_{d}".format(d=str(day_num + 1))
        fields = fields.split()
        labels = labels + fields

    resort_locs = query_resorts(db_name)

    cnt = 0
    weather_data = []
    for ID, z_code in resort_locs:
        sleep(1.1) # Slow down requests to prevent API lockout
        req_addr =  zip_url.format(z_code) + "&units=imperial" + API_KEY
        # Attempt to resolve faulty database connection
        try:
            r = requests.get(req_addr)
        except ConnectionError:
            sleep(5)
            r = requests.get(req_addr)

        json_str = r.text
        weather = json.loads(json_str)
        fcast_data = [ID]

        for day_num in range(len(weather['list'])):
            link = weather['list'][day_num]
            wthr = link['weather'][0]['main']
            dscr = link['weather'][0]['description']
            t_day = link['temp']['day']
            t_night = link['temp']['night']
            t_min = link['temp']['min']
            t_max = link['temp']['max']
            pres = link['pressure']
            humd = link['humidity']
            w_spd = link['speed']

            if 'rain' in link:
                rain = link['rain']
            else:
                rain = 0

            if 'snow' in link:
                snow = link['snow']
            else:
                snow = 0

            data = [wthr, dscr, t_day, t_night, t_min, t_max, pres, humd, w_spd, rain, snow]
            fcast_data += data

        weather_data.append(fcast_data)
    
    csv_writer(labels, weather_data, output_file)

def update_weather_tables(table_name, read_file, db_name):
    '''
    This function is used to update weather tables in the central database. It
    is called every time m
    '''
    conn = lite.connect(db_name)
    c = conn.cursor()

    fields, weather_data = csv_reader(read_file)

    refresh = "DELETE FROM " + table_name
    c.execute(refresh)

    conn.commit()

    prm_slots = ['?'] * len(fields)
    prm_slots = "(" + ",".join(prm_slots) + ")"
    insert_stmt = 'INSERT INTO ' + table_name + ' VALUES ' + prm_slots
    c.executemany(insert_stmt, weather_data)

    conn.commit()

def do_current(database_name, csv_name):

    get_current(database_name, csv_name)
    update_weather_tables('current', csv_name, database_name)

def do_forecast(database_name, csv_name):

    get_forecast(database_name, csv_name)
    update_weather_tables('forecast', csv_name, database_name)

if __name__ == "__main__":
    
    # Code appropriated from programming assignment
    if len(sys.argv) != 4:
        print("usage: python3 {} <database name> <current filename> <forecast filename>".format(sys.argv[0]))
        sys.exit(1)
        
    do_current(sys.argv[1], sys.argv[2])
    do_forecast(sys.argv[1], sys.argv[3])