# Using Weather Data
#
# Wesbite

import sqlite3 as lite
import csv
import requests
import json
import time
import database

# API Quick Facts
#   Limits:
#       60 per minute actually more like 1 per second
#       50,000 per day
#   Products:
#       Current Weather
#       5Day/3 hour Forecast
#       Weather Maps

API_KEY = "&APPID=2862f4116ca55cb42c41cb9ea03711b0"

def query_resorts(db_name):
    
    conn = lite.connect(db_name)
    c = conn.cursor()
    query = "SELECT ID, zip FROM main"
    resorts = c.execute(query)
    return resorts


def get_current(db_name, output_file):
    '''
    This API will work best if given a lat and lon.
    However, it is currently designed to accept zipcodes in a list.
    '''
    
    city_url = "http://api.openweathermap.org/data/2.5/weather?q="
    zip_url = "http://api.openweathermap.org/data/2.5/weather?zip={},us"
    
    resort_loc = query_resorts(db_name)
    
    cnt = 0
    weather_data = []
    for ID, z_code in resort_loc:
        time.sleep(1.1)
        req_addr = zip_url.format(z_code) + "&units=imperial" + API_KEY
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
            rain = weather['rain']['3h']
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
    
    fields = ["ID", 'wthr', 'dscr', "temp", "pres", "humd", "spd", "rain", "snow"]
    weather_data = weather_data
    with open(output_file, 'w') as csvfile:
        row_writer = csv.writer(csvfile, lineterminator = '\n')
        row_writer.writerow(fields)
        row_writer.writerows(weather_data)
    
def get_forecast(db_name, output_file):
    
    '''
    This function should be run once a day in order to update the database
    '''
    
    exmp_url = 'http://api.openweathermap.org/data/2.5/forecast/daily?zip=4843,us&units=imperial&APPID=2862f4116ca55cb42c41cb9ea03711b0'    
    city_url = "http://api.openweathermap.org/data/2.5/forecast?q="
    zip_url = "http://api.openweathermap.org/data/2.5/forecast/daily?zip={},us"
    
    NUM_DAYS = 7 
    
    labels = ['ID']
    for day_num in range(NUM_DAYS):
        fields = "{d}-wthr {d}-dscr {d}-avg_day {d}-avg_night \
                  {d}-t_min {d}-t_max {d}-pres {d}-humd {d}-w_spd \
                  {d}-rain {d}-snow".format(d=str(day_num+1))
        fields = fields.split()
        labels = labels + fields
        
    resort_locs = query_resorts(db_name)
        
    cnt = 0
    weather_data = []
    for ID, z_code in resort_locs:
        time.sleep(1.1)
        req_addr =  zip_url.format(z_code) + "&units=imperial" + API_KEY
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
        
    with open(output_file, 'w') as csvfile:
        row_writer = csv.writer(csvfile, lineterminator = '\n')
        row_writer.writerow(labels)
        row_writer.writerows(weather_data)
        

def update_weather_tables(table_name, read_file, db_name):
    '''
    
    '''
    conn = lite.connect(db_name)
    c = conn.cursor()
    
    fields, weather_data = database.csv_reader(read_file)
    
    refresh = "DELETE FROM " + table_name
    c.exectute(refresh)
    
    prm_slots = ['?'] * len(fields)
    prm_slots = "(" + ",".join(prm_slots) + ")" 
    insert_stmt = 'INSERT INTO ' + table_name + ' VALUES ' + prm_slots
    c.executemany(insert_stmt, weather_data)

    conn.commit()
    conn.close()
            
if __name__ == '__main__':
    
    get_current("ski-resorts.db", "CSVs\current_weather.csv")
    get_forecast("ski-resorts.db", "CSVs\forecast_weather.csv")
    update_weather_tables('current', "CSVs\current_weather.csv", "ski-resorts.db")
    update_weather_tables('forecast', 'CSVs\forecast_weather.csv', 'ski-resorts.db')