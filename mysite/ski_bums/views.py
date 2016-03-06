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
    info = {'one': '49 Degrees North',
            'state_1': ['State', 'WA'],
            'two': 'Afton Alps',
            'state_2': ['State', 'MN'],
            'three': 'Alpental',
            'state_3': ['State', 'WA'],
            }
    if request.method == 'POST':
        print(request.POST)
        print()
        current_location = request.POST['current_location']
        addr_info = sql_info([1,2,3])
        print(addr_info)
        dir_list = []
        drive_time = []
        for i in range(len(addr_info)):
            directions = get_directions(addr_info[i][0], addr_info[i][1],
                                        addr_info[i][2], addr_info[i][3],
                                        current_location)
            dir_list.append(directions)
            time = travel_time_words(addr_info[i][0], addr_info[i][1],
                                     addr_info[i][2], addr_info[i][3],
                                     current_location)
            drive_time.append(time)
        
        info['time_1'] = ['Driving Time', drive_time[0]]
        info['time_2'] = ['Driving Time', drive_time[1]]
        info['time_3'] = ['Driving Time', drive_time[2]]
        if 'driving dir' in request.POST:
            info['drive_1'] = dir_list[0]
            info['drive_2'] = dir_list[1]
            info['drive_3'] = dir_list[2]



    #else:
        # what to output if someone were type /results into the url
    return render(request, 'ski_bums/results.html', info)


# stuff with driving directions

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8' 

def sql_info(resort_ids):
    '''
    '''
    sql_string = 'SELECT addr, city, state, zip FROM main WHERE id = ? or id = ? or id = ?'
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





        
