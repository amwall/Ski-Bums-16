from django.db import models
import json
from datetime import date
import re
from urllib.request import urlopen
import sqlite3
import os
from math import sin, asin, sqrt, cos, radians
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, '../../ski-resorts.db')

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8'
GEOCODING_ID = 'AIzaSyCeg-uM3PsOT2ssRsPDfQdxZPbGz6k0kBc' 


def general_information(resort_ids):
    '''
    Obtains general information from the sqlite database for the 
    given resorts

    Input:
        resort_ids: a list

    Output:
        a list
    '''
    where = ['id = ?'] * len(resort_ids)
    where = " WHERE " + " OR ".join(where) 

    sql_string = ('SELECT name, ID, city, state, elev, max_price, beginner, ' +
                  'intermediate, advanced, expert, night, park, total_runs, ' +
                  'area FROM main ' + where)
    
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, resort_ids)
    output = execute.fetchall()
    connection.close()

    return output

def address_info(resort_ids):
    '''
    Obtains the address, city, state, and zip code from the sqlite
    database for the given resorts
    '''
    where = ['id = ?'] * len(resort_ids)
    where = "WHERE " + " OR ".join(where) 

    query = 'SELECT addr, city, state, zip FROM main ' + where
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(query, resort_ids)
    output = execute.fetchall()
    connection.close()

    return output


def build_ranking(search_dict, database_name='ski-resorts.db'):
    '''
    The main ranking algorithm. It takes the search results and builds 
    a query that returns the top three results. The program returns 
    the IDs, which are the primary keys for the resorts
    '''
    db = sqlite3.connect(database_name)
    db.create_function('score_size', 2, score_size)     
    db.create_function('time_between', 4, compute_time_between)
    cursor = db.cursor()    

    parameters = []

    query = 'SELECT ID, '  #size_score + run_score AS total_score,'

    ### SCORE RUNS ###
    addition, parameters = score_runs(search_dict, parameters)
    query += addition

    ### SCORE SIZE ###
    choice = search_dict['Resort Size']
    query += "score_size(area, " + "'" + choice + "')"  +  ' AS total_score'
    # Connect table

    ### CUTTING ATTRIBUTES ###
    where = []
    ### DISTANCE ###
        
    where.append(" time_between(lon,lat,?,?) <= ?")
    max_time = float(search_dict['max_drive_time']) + 0.5  #Marginally increase bounds
    cur_loc = search_dict['current_location']
    u_lat, u_lon = get_lat_lon(cur_loc)
    parameters.extend([u_lon, u_lat, max_time])

    query += ' FROM main WHERE'
    ### NIGHT SKIING ###
    if search_dict['night skiing'] != 'Indifferent':
        where.append(" night=1")

    ### MAX TICKET ###
    if search_dict['max_tic_price']:
        price = int(search_dict['max_tic_price'])
        parameters.append(price)
        where.append(" (max_price <= ? OR max_price='N/A')")

    ### Terrain Park ###
    if int(search_dict['Terrain parks']) > 1:
        where.append(" park > 0")

    where = " AND".join(where)
    query += where
    query += ' ORDER BY total_score DESC LIMIT 3'
    
    parameters = tuple(parameters)
    exc = cursor.execute(query, parameters)
    output = exc.fetchall()

    resort_ids = []
    for i in range(len(output)):
        resort_id = output[i][0]
        resort_ids.append(resort_id)
        
    return resort_ids


def score_size(area, choice):
    '''
    A system for scoring base on the users choice and the number of runs at
    the resort
    SMALL: 0-750
    MEDIUM: 750-2000
    Large: 2000 +
    '''
    if area == 'N/A':
        area = 1000

    if choice == 'Small':
        sml_mlt = 80
        med_mlt = 1
        lrg_mlt = 0.5
    elif choice == 'Medium':
        sml_mlt = 5
        med_mlt = 2
        lrg_mlt = 1
    else:
        sml_mlt = 3
        med_mlt = 1
        lrg_mlt = 1.25

    if (area >= 0 and area < 750):
        scr = area * sml_mlt
    elif (area >= 750 and area < 2000):
        scr = area * med_mlt
    else:
        scr = area * lrg_mlt

    return scr


def score_runs(search_dict, parameters):
    '''
    A function for builds a portion of the SQL query that scores based on the
    percentage of runs that are of a given difficulty.
    '''
    score_dict = {'1': 0,
                  '2': 25,
                  '3': 50,
                  '4': 100,
                  '5': 200}

    beg_mlt = score_dict[search_dict['Beginner runs']]
    int_mlt = score_dict[search_dict['Intermediate runs']]
    exp_mlt = score_dict[search_dict['Expert runs']]
    adv_mlt = score_dict[search_dict['Advanced runs']]

    parameters.extend([beg_mlt, int_mlt, adv_mlt, exp_mlt])
    query = " beginner * ? + intermediate * ? + advanced * ? + expert * ? + "
    
    return query, parameters

#############################################################
#                                                           #
#                       Weather                             #
#                                                           #
#############################################################

def date_distance(date_ski):
    '''
    Returns the number of days in a list between the current 
    date and the inputed date
    '''
    date_today = date.today().strftime('%m/%d/%Y')

    dat_lis = re.findall('[0-9]+',date_today)
    ski_lis = re.findall('[0-9]+',date_ski)
    
    d0 = date(int(dat_lis[2]), int(dat_lis[0]), int(dat_lis[1]))    
    d1 = date(int(ski_lis[2]), int(ski_lis[0]), int(ski_lis[1]))
    delta = d1 - d0
    return list(range(delta.days))
    

def grab_weather(id_list, days_list, check):
    '''
    Returns current weather of the given ski resorts. 
    If check == True, also returns the forecast for the day
    the user wants to ski
    '''
    select = 'SELECT '
    fields = 'c.ID, c.wthr, c.dscr, c.temp, c.snow'

    if days_list != []:
        snow_fall = []
        addition = None
        for day in days_list:
            if addition == None:
                addition = '(f.snow_' + str(day + 1)
            else:
                addition = addition + ' + f.snow_' + str(day + 1) 
        addition = addition + ') as [Total Snow Fall] '
        snow_fall.append(addition)

        weather = 'f.wthr_' + str(days_list[-1] + 1) + ', '
        description = 'f.dscr_' + str(days_list[-1] + 1) + ', '
        average_day = 'f.avg_day_' + str(days_list[-1] + 1) + ', '

    fro_cur = ' FROM current AS c '
    new_id = []
    for person in id_list:
        change = str(person)
        new_id.append(change)
    customer_id = "(" + ", ".join(new_id) + ")"
    where = 'WHERE c.ID IN ' + customer_id
    if check == 'Yes':
        sql_string = (select + fields + ', ' + weather + description +
                      average_day + snow_fall[0] + 
                      'FROM current AS c JOIN forecast AS f ON (c.ID = f.ID) ' +
                      where)
    else:
        sql_string = select + fields + fro_cur + where

    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    current_weather = execute.fetchall()
    connection.close()
    
    return current_weather
        
        
#########################################################
#                                                       #
#               DISTANCE & DIRECTIONS                   #
#                                                       #
#########################################################
        
                 
def get_lat_lon(location, locality=False):
    '''
    This function is used for getting the GPS coordinates for a given location.
    location can be any combination of city, state, addr and zip code.
    However, the more fields that are provided the greater likelyhood that
    GPS coordinates will be correct
    '''
    current = str(location).split()
    current = '+'.join(current)
    
    url =  ('https://maps.googleapis.com/maps/api/geocode/json?' +
            'address=' + current + '&key=' + GEOCODING_ID)
    
    request = urlopen(url)
    test = request.read().decode("utf-8")
    data = json.loads(test)
    
    try:
        lat = data['results'][0]['geometry']['location']['lat']
        lon = data['results'][0]['geometry']['location']['lng']
         
    except:
        lat = 0
        lon = 0
    
    if locality:
        city = 'NaN'
        state = 'NaN'
        short = data['results'][0]['address_components']
        for i in range(len(short)):
            if 'locality' in short[i]['types']:
                city = short[i]['short_name']
            if "administrative_area_level_1" in short[i]['types']:
                state = short[i]["long_name"]
        return lat, lon, city, state
        
    return lat, lon
    

def get_distance(destination, current_location):
    '''
    Find the time it takes to drive from a user's current location 
    to a given location. 
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination.split()
    end = "+".join(end)
    
    url = ('https://maps.googleapis.com/maps/api/distancematrix/json?' +
           'units=imperial' + '&origins=' + current + '&destinations=' + 
           end + '&key=' + DISTANCE_MATRIX_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')
    data = json.loads(text)
    
    try:
        seconds = data['rows'][0]['elements'][0]['duration']['value']
        meters = data['rows'][0]['elements'][0]['distance']['value']
    
        time_text = data['rows'][0]['elements'][0]['duration']['text']
        dist_text = data['rows'][0]['elements'][0]['distance']['text']
    except:
        seconds = 0
        meters = 0
        time_text = 'NaN'
        dist_text = 'NaN'
    
    return time_text, dist_text


def get_directions(destination, current_location):
    '''
    Given a user's current location and a resort, return
    a list with the directions
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination.split()
    end = "+".join(end)
    
    url = ('https://maps.googleapis.com/maps/api/directions/json?' +
            'origin=' + current + '&' + 'destination=' + end +  
            '&key=' + DIRECTIONS_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')

    values = re.findall('("text"\s:\s)\"([0-9\.\sa-z]*)', text)
    # Make a list of the distances you are driving for each step
    distances = []
    for i in values[2::2]:
        distances.append(i[1])

    instructions = re.findall('("html_instructions"\s:\s)\"([A-Za-z0-9\\\/\s\-]*)', 
                              text)
    directions = []
    for i in instructions:
        directions.append(i[1])
    # Narrowing down the directions by using regular expressions
    l = []
    for i in directions:
        x = re.findall('([A-Za-z\s]+)([A-Za-z0-9\s\-]+)', i)
        l.append(x)
    # Make a list of the directions (i.e. Turn right onto street, Merge onto...) 
    directions = []
    for turn in l:
        new = ''
        first_term = turn[0][0]
        if first_term == 'u':
            for i in turn[1:len(turn) - 1:2]:
                new += i[1][4:] + ' '
        else:
            new += first_term + ' '
            for i in turn[2:len(turn) - 1:2]:
                new += i[1][4:] + ' '

        directions.append(new)
    # Make a final list of the directions with distance for each step
    direct_and_dist = []
    for i in range(len(directions)):
        entry = directions[i] + 'and continue for ' + distances[i]
        direct_and_dist.append(entry)

    time_travel, dist_travel = get_distance(destination, current_location)
    direct_and_dist.append('Total travel time is ' + time_travel)
    direct_and_dist.append('Total miles traveled: ' + dist_travel)

    return direct_and_dist

    
def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)
    #adjusted downwards to account for manhattan distance
    driving_speed_per_hr = 55000 #55km an hr
    hrs = meters / driving_speed_per_hr

    return hrs


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m




########################################################
#                                                      #
#                   ANALYSIS FILES                     #
#                                                      #
########################################################


def score_location(current_location, path, db_path):
    '''
    This function is used for comparing a user's given location
    against the scores for 1,000 most populous cities in the country.
    It returns a string the gives the percentile their location falls into.
    Input: current_location: user's input
           path: The path to the scored registry of cities
           db_path: The path to the ski-resorts database
    
    '''
    
    conn = sqlite3.connect(db_path)
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
    
    percentile = compare_score(info, path)
    if type(percentile) == str:
        return percentile
    else:
        rv = (city + ", " + state + " is in the " + 
              str(round(((1-percentile) * 100),1)) +
              " percentile of places to live for access to ski resorts")
        return rv
    
def compare_score(info, path):
    '''
    Compare_score is helper function called in the score_location function 
    which does the actual comparison of the user location to the registry 
    of cities.
    If the city they give is not in our database of cities, the information 
    is added to our registry for future users to compare with
    '''
    
    df = pd.read_csv(path)
    if info[0] != 'NaN':    
        if any(np.where(df['city'] == info[0])):
            rank = np.where(df['city'] == info[0])[0][0]
            rv = rank/len(df)
        else:
            df.loc[len(df)] = info 
            df.sort_values(['score'], ascending=False, inplace=True)
            
            rank = np.where(df['city'] == info[0])[0][0]
            rv = rank/len(df)
            df.to_csv(path, index=False)
    else:
        rv = "We could not compare your location"
        
    return rv

