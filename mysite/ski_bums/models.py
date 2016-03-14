from django.db import models
import json
from datetime import date
import re
from urllib.request import urlopen
import sqlite3
import os
from math import sin, asin, sqrt, cos, radians

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8'
GEOCODING_ID = 'AIzaSyCeg-uM3PsOT2ssRsPDfQdxZPbGz6k0kBc' #'AIzaSyB0Sx4EMq-IP2fXfzSyoRQ4-1llyKNJQgU'

def general_information(resort_ids):
    '''
    '''
    where = ['id = ?'] * len(resort_ids)
    where = " WHERE " + " OR ".join(where) 

    sql_string = ('SELECT name, ID, city, state, elev, max_price, beginner, intermediate, ' +
                  'advanced, expert, night, park, total_runs, area ' +
                  'FROM main ' + where)
    
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, resort_ids)
    output = execute.fetchall()
    connection.close()

    return output

def sql_info(resort_ids):
    '''
    '''
    where = ['id = ?'] * len(resort_ids)
    where = "WHERE " + " OR ".join(where) 

    query = 'SELECT addr, city, state, zip FROM main ' + where
    print(query)
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(query, resort_ids)
    output = execute.fetchall()
    connection.close()

    return output


def build_ranking(search_dict, database_name='ski-resorts.db'):
    '''
    The main ranking algorithm. It takes the search results and builds a query
    that returns the top three results. The program returns the IDs, which are
    the primary keys for the resorts
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
    # print(choice)
    query += "score_size(total_runs, " + "'" + choice + "')"  +  ' AS total_score'
    # Connect table

    ### CUTTING ATTRIBUTES ###
    where = []
    ### DISTANCE ###
    if search_dict['max_drive_time']:
        
        where.append(" time_between(lon,lat,?,?) <= ?")
        max_time = int(search_dict['max_drive_time'][0]) + 0.5  #Marginally increase bounds
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
    
    print(query)
    
    parameters = tuple(parameters)
    exc = cursor.execute(query, parameters)
    output = exc.fetchall()

    resort_ids = []
    for i in range(len(output)):
        resort_id = output[i][0]
        resort_ids.append(resort_id)
    
    print()
    print(resort_ids)
    print()
    print(parameters)
    return resort_ids

def score_size(num_runs, choice):
    '''
    A system for scoring base on the users choice and the number of runs at
    the resort
    SMALL: 1-35
    MEDIUM: 35-150
    Large: 150 +
    '''
    
    if choice == 'Small':
        sml_mlt = 10
        med_mlt = 3
        lrg_mlt = 0.5
    elif choice == 'Medium':
        sml_mlt = 8
        med_mlt = 4
        lrg_mlt = 2
    else:
        sml_mlt = 0.5
        med_mlt = 0.65
        lrg_mlt = 0.8

    if num_runs >= 100:
        scr = num_runs * lrg_mlt
    elif num_runs >= 35 and num_runs < 150:
        scr = num_runs * med_mlt
    else:
        scr = num_runs * lrg_mlt

    return scr

def score_runs(search_dict, parameters):
    '''
    A function for builds a portion of the SQL query that scores based on the
    percentage of runs that are of a given difficulty.
    '''
    score_dict = {'1': 0,
                  '2': .25,
                  '3': .5,
                  '4': 1,
                  '5': 2}

    beg_mlt = score_dict[search_dict['Beginner runs']]
    int_mlt = score_dict[search_dict['Intermediate runs']]
    exp_mlt = score_dict[search_dict['Expert runs']]
    adv_mlt = score_dict[search_dict['Advanced runs']]

    parameters.extend([beg_mlt, int_mlt, adv_mlt, exp_mlt])
    query = " beginner * ? + intermediate * ? + \
              advanced * ? + expert * ? + "
    
    return query, parameters

def date_distance(date_ski):
    
    date_today = date.today().strftime('%m/%d/%Y')

    dat_lis = re.findall('[0-9]+',date_today)
    ski_lis = re.findall('[0-9]+',date_ski)
    
    d0 = date(int(dat_lis[2]), int(dat_lis[0]), int(dat_lis[1]))    
    d1 = date(int(ski_lis[2]), int(ski_lis[0]), int(ski_lis[1]))
    delta = d1 - d0
    return list(range(delta.days))
    

def grab_weather(id_list, days_list, check):
    
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
        sql_string = (select + fields + ', ' + weather + description + average_day +
                      snow_fall[0] + 'FROM current AS c JOIN forecast AS f ON (c.ID = f.ID) ' +
                      where)
    else:
        sql_string = select + fields + fro_cur + where

    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    current_weather = execute.fetchall()
    connection.close()
    
    return current_weather
        
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

def get_lat_lon(location):
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
           'units=imperial' + '&origins=' + current + '&destinations=' + end +  
            '&key=' + DISTANCE_MATRIX_ID)

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
    time_travel = values[1][1]

    distances = []
    for i in values[2::2]:
        distances.append(i[1])

    instructions = re.findall('("html_instructions"\s:\s)\"([A-Za-z0-9\\\/\s\-]*)', text)
    directions = []
    for i in instructions:
        directions.append(i[1])

    l = []
    for i in directions:
        x = re.findall('([A-Za-z\s]+)([A-Za-z0-9\s\-]+)', i)
        l.append(x)
    
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

    direct_and_dist = []
    for i in range(len(directions)):
        entry = directions[i] + 'and continue for ' + distances[i]
        direct_and_dist.append(entry)

    time_travel, dist_travel = get_distance(destination, current_location)
    direct_and_dist.append('Total travel time is ' + time_travel)
    direct_and_dist.append('Total miles traveled: ' + dist_travel)

    return direct_and_dist