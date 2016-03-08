from django.shortcuts import render
from django.template import loader

import re
from urllib.request import urlopen
import sqlite3
import os
#import pref_algo.py

# Create your views here.

# run python manage.py runserver 
from django.http import HttpResponse


def index(request):
    
    return render(request, 'ski_bums/index.html')


def results(request):
    info = {}
    if request.method == 'POST':
        print(request.POST)
        print()
        current_location = request.POST['current_location']
        id_ranking = [1, 2, 3]
        if id_ranking != []:
            addr_info = sql_info(id_ranking)
            dir_list = []
            drive_time = []
            general_info = general_information(id_ranking)
            for i in range(len(addr_info)):
                # adding general information about the resort to the dictionary
                info['name_' + str(i + 1)] = general_info[i][0]
                info['id_' + str(i + 1)] = ['ID', general_info[i][1]]
                info['state_' + str(i + 1)] = ['State', general_info[i][2]]
                info['elev_' + str(i + 1)] = ['Elevation', general_info[i][3]]
                info['price_' + str(i + 1)] = ['Max Ticket Price', general_info[i][4]]
                info['beg_' + str(i + 1)] = ['Beginner Slopes', str(general_info[i][5]) + '%']
                info['int_' + str(i + 1)] = ['Intermediate Slopes', str(general_info[i][6]) + '%']
                info['adv_' + str(i + 1)] = ['Advanced Slopes', str(general_info[i][7]) + '%']
                info['exp_' + str(i + 1)] = ['Expert Slopes', str(general_info[i][8]) + '%']
                if general_info[i][9] == '0':
                    info['night_' + str(i + 1)] = ['Night Skiing', 'No']
                else:
                    info['night_' + str(i + 1)] = ['Night Skiing', 'Yes']
                if general_info[i][10] == '0':
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'No']
                else:
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'Yes']
                info['runs_' + str(i + 1)] = ['Total Number of Runs', general_info[i][11]]
                info['area_' + str(i + 1)] = ['Total Area', str(general_info[i][12]) + ' acres']


                # adding directions/ driving time  to the dictionary
                directions = get_directions(addr_info[i][0], addr_info[i][1],
                                            addr_info[i][2], addr_info[i][3],
                                            current_location)
                dir_list.append(directions)
                time = travel_time_words(addr_info[i][0], addr_info[i][1],
                                         addr_info[i][2], addr_info[i][3],
                                         current_location)
                drive_time.append(time)

                info['time_' + str(i + 1)] = ['Driving Time', drive_time[i]]

                if 'driving dir' in request.POST:
                    info['drive_' + str(i + 1)] = dir_list[i]

    return render(request, 'ski_bums/results.html', info)


def info(request):

    sql_string = 'SELECT ID, name, state, dates, rating FROM main'
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    resort_list = execute.fetchall()
    connection.close()
    c = {}
    for i in range(len(resort_list)):
        c['info' + str(i)] = resort_list[i]

    return render(request, 'ski_bums/info.html', c)


# stuff with driving directions

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8' 

def where_statement(resort_ids):
    '''
    '''
    if len(resort_ids) == 1:
        where = 'id = ?'
    elif len(resort_ids) == 2:
        where = 'id = ? or id = ?'
    elif len(resort_ids) == 3:
        where = 'id = ? or id = ? or id = ?'

    return 'WHERE ' + where

def general_information(resort_ids):
    '''
    '''
    where = where_statement(resort_ids)
    sql_string = ('SELECT name, ID, state, elev, max_price, beginner, intermediate, ' +
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
    where = where_statement(resort_ids)
    sql_string = 'SELECT addr, city, state, zip FROM main ' + where
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, resort_ids)
    output = execute.fetchall()
    connection.close()

    return output


def destination(addr, city, state, zip_code):
    '''
 
    '''
    num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if addr[0] in num_list:
        destination = addr.split()
        destination = '+'.join(destination) + '+' + '+'.join(state.split())
    elif city != '':
        city = '+'.join(city.split())
        state = '+'.join(state.split())
        destination = city + '+' + state
    else:
        destination = zip_code

    return destination
    

def travel_time_hours(addr, city, state, zip_code, current_location):
    '''
    Find the time it takes to drive from a user's current location 
    to a resort. 
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(addr, city, state, zip_code)
    
    url = ('https://maps.googleapis.com/maps/api/distancematrix/json?' +
            'origins=' + current + '&' + 'destinations=' + end +  
            '&key=' + DISTANCE_MATRIX_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')
    values = re.findall('"value"\s:\s[0-9]+', text)
    meters = float(re.findall('[0-9]+', values[0])[0])
    minutes = float(re.findall('[0-9]+', values[1])[0])

    return minutes / 60


def travel_time_words(addr, city, state, zip_code, current_location):
    '''
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(addr, city, state, zip_code)
    
    url = ('https://maps.googleapis.com/maps/api/directions/json?' +
            'origin=' + current + '&' + 'destination=' + end +  
            '&key=' + DIRECTIONS_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')

    values = re.findall('("text"\s:\s)\"([0-9\.\sa-z]*)', text)
    travel_time = values[1][1]

    return travel_time


def get_directions(addr, city, state, zip_code, current_location):
    '''
    Given a user's current location and a resort, return
    a list with the directions
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(addr, city, state, zip_code)
    
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

    direct_and_dist.append('Total travel time is ' + time_travel)

    return direct_and_dist





        
