# analysis.py
# Gareth Jones

import pandas as pd
from directions import get_lat_lon, compute_time_between
from database import csv_writer
import sqlite3 as lite
import numpy as np

def score_location(current_location, path, db_path):
    '''
    This function is used for comparing a user's given location
    against the scores for 1,000 most populous cities in the country.
    It returns a string the gives the percentile their location falls into.
    Input: current_location: user's input
           path: The path to the scored registry of cities
           db_path: The path to the ski-resorts database
    
    '''
    
    conn = lite.connect(db_path)
    c = conn.cursor()
    conn.create_function('time_between', 4, compute_time_between)
    lat, lon, city, state = get_lat_lon(current_location, locality=True)
    params = (lon,lat,lon,lat)
    query = "SELECT SUM(area), SUM(time_between(lon, lat, ?, ?)), COUNT(*)\
             FROM main WHERE time_between(lon, lat, ?, ?) < 3.25"
    result = c.execute(query, params)
    
    area, time, count = list(result)[0]
    score = (area)/(time/count)
    info = (city, state, area, time, count,lat,lon,score)
    
    conn.commit()
    conn.close()
    
    percentile = compare_score(info, path)
    if type(percentile) == str:
        return percentile
    else:
        rv = (city + ", " + state + " is in the " + str(round(((1-percentile) * 100),1)) +
              " percentile of places to live for access to ski resorts")
        return rv
    
def compare_score(info, path):
    '''
    
    Compare_score is helper function called in the score_location function which
    does the actual comparison of the user location to the registry of cities.
    If the city they give is not in our database of cities, the information is added
    to our registry for future users to compare with
    '''
    
    df = pd.read_csv(path)
    if info[0] != 'NaN':    
        if any(np.where(df['city'] == info[0])):
            rank = np.where(df['city'] == info[0])[0][0]
            print(rank)
            rv = rank/len(df)
        else:
            df.loc[len(df)] = info 
            print(df.tail())
            df.sort_values(['score'], ascending=False, inplace=True)
            
            rank = np.where(df['city'] == info[0])[0][0]
            rv = rank/len(df)
            df.to_csv(path, index=False)
    else:
        rv = "We could not compare your location"
        
    return rv
    
    
def gather_city_data(city_csv, db_name, output_name):
    '''
    This function creates a csv that saves the total acreage, number of resorts
    and time to drive to them for all resorts within a 3.25 hour drive of the
    city.   
    '''
    
    conn = lite.connect(db_name)
    c = conn.cursor()
    conn.create_function('time_between', 4, compute_time_between)
    cities = pd.read_csv(city_csv)
    rows = []
    for i, city in cities.iterrows():
        lat, lon = get_lat_lon(city['city'] + " " + city['state'])
        params = (lon,lat,lon,lat)
        query = "SELECT SUM(area), SUM(time_between(lon, lat, ?, ?)), COUNT(*) \
                 FROM main WHERE time_between(lon, lat, ?, ?) < 3.25"
        result = c.execute(query, params)
        area, time, count = list(result)[0]
        rows.append((city['city'], city['state'], area, time, count, lat, lon))
        
    conn.commit()
    conn.close()

    labels = ['city','state','area','time','number', 'lat', 'lon']
    csv_writer(labels,rows,output_name)
    
def analyze_data(city_score_csv, output_name):
    '''
    For a given list of cities and the information about them,
    this function create a score for each city based on the total amount of
    ski able terrain in the area and the average driving time to a resort
    '''
    
    df = pd.read_csv(city_score_csv)
    df.fillna(0, inplace=True)
    
    scores = []
    for i, city in df.iterrows():
        if city['number'] == 0:  #Deal with cities with no nearby resorts
            score = 1
        else:
            area = city['area']
            avg_time = city['time']/city['number']
            score = area/avg_time
        scores.append(score)
        
    df['score'] = pd.Series(scores, index=df.index)
    df.sort_values(['score'], ascending=False, inplace=True)
    df.to_csv(output_name)
