# Megan Wall

import re
from urllib.request import urlopen


# **Will need to change the inputs into some of the functions

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8' 


def destination(resort_dictionary, resort):
    '''
 
    '''
    num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    resort_info = resort_dictionary[resort]
    address = resort_info['Address']
    city = resort_info['City']
    state = resort_info['State']
    zip_code = resort_info['Zip Code']

    if address[0] in num_list:
        destination = address.split()
        destination = '+'.join(destination) + '+' + '+'.join(state.split())
    elif city != '':
        city = '+'.join(city.split())
        state = '+'.join(state.split())
        destination = city + '+' + state
    else:
        destination = zip_code

    return destination
    

def travel_time_minutes(resort_dictionary, resort, current_location):
    '''
    Find the time it takes to drive from a user's current location 
    to a resort. 
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(resort_dictionary, resort)
    
    url = ('https://maps.googleapis.com/maps/api/distancematrix/json?' +
            'origins=' + current + '&' + 'destinations=' + end +  
            '&key=' + DISTANCE_MATRIX_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')
    values = re.findall('"value"\s:\s[0-9]+', text)
    meters = float(re.findall('[0-9]+', values[0])[0])
    minutes = float(re.findall('[0-9]+', values[1])[0])

    return minutes


def travel_time_words(resort_dictionary, resort, current_location):
    '''
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(resort_dictionary, resort)
    
    url = ('https://maps.googleapis.com/maps/api/directions/json?' +
            'origin=' + current + '&' + 'destination=' + end +  
            '&key=' + DIRECTIONS_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')

    values = re.findall('("text"\s:\s)\"([0-9\.\sa-z]*)', text)
    time_travel = values[1][1]

    return travel_time


def get_directions(resort_dictionary, resort, current_location):
    '''
    Given a user's current location and a resort, return
    a list with the directions
    '''
    current = current_location.split()
    current = '+'.join(current)

    end = destination(resort_dictionary, resort)
    
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
        entry = str(i + 1) + '. ' + directions[i] + 'and continue for ' + distances[i]
        direct_and_dist.append(entry)

    direct_and_dist.append('Total travel time is ' + time_travel)

    return direct_and_dist



