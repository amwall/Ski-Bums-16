from lxml import html
import re
from urllib.request import urlopen
import json

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8'
GEOCODING_ID = 'AIzaSyB0Sx4EMq-IP2fXfzSyoRQ4-1llyKNJQgU'

def cur_lat_and_long(current_location):
    '''
    This function is used for getting the GPS coordinates for a given location.
    Current_location can be any combination of city, state, addr and zip code.
    However, the more fields that are provided the greater likelyhood that
    GPS coordinates will be correct
    '''
    current = str(current_location).split()
    current = '+'.join(current)
    
    url =  ('https://maps.googleapis.com/maps/api/geocode/json?' +
            'address=' + current + '&key=' + GEOCODING_ID)

    request = urlopen(url)
    test = request.read().decode("utf-8")
    data = json.loads(test)
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    
    return lat, lng

def parse_destination(addr, city, state, zip_code):
    '''
    A helper function for pars
    '''
    int_list = list(range(10))
    num_list = list(map(str,int_list)) # create a list of strings

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
    

def get_distance(addr, city, state, zip_code, current_location):
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
    data = json.loads(text)
    
    seconds = data['rows'][0]['elements'][0]['duration']['value']
    meters = data['rows'][0]['elements'][0]['distance']['value']
    
    time_text = data['rows'][0]['elements'][0]['duration']['text']
    dist_text = data['rows'][0]['elements'][0]['distance']['text']
    
    print(seconds, time_text)
    print(meters, dist_text)

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
    print(url)
    request = urlopen(url)
    text = request.read()
    text = text.decode('utf-8', errors='ignore')
    data = json.loads(text)
    
    steps = data['routes'][0]['legs'][0]['steps']
    
    instructions = []
    time = 0
    dist = 0
    for x in range(len(steps)):
        instr = steps[x]['html_instructions']
        instructions.append(instr)
        dist += steps[x]['distance']['value']
        time += steps[x]['duration']['value']
        print(instr)
    print('time', time)
    print('dist', dist)

    return instructions, time, distance
    
    # values = re.findall('("text"\s:\s)\"([0-9\.\sa-z]*)', text)
    # time_travel = values[1][1]
    # 
    # distances = []
    # for i in values[2::2]:
    #     distances.append(i[1])
    # 
    # instructions = re.findall('("html_instructions"\s:\s)\"([A-Za-z0-9\\\/\s\-]*)', text)
    # directions = []
    # for i in instructions:
    #     directions.append(i[1])
    # 
    # l = []
    # for i in directions:
    #     x = re.findall('([A-Za-z\s]+)([A-Za-z0-9\s\-]+)', i)
    #     l.append(x)
    # 
    # directions = []
    # for turn in l:
    #     new = ''
    #     first_term = turn[0][0]
    #     if first_term == 'u':
    #         for i in turn[1:len(turn) - 1:2]:
    #             new += i[1][4:] + ' '
    #     else:
    #         new += first_term + ' '
    #         for i in turn[2:len(turn) - 1:2]:
    #             new += i[1][4:] + ' '
    # 
    #     directions.append(new)
    # 
    # direct_and_dist = []
    # for i in range(len(directions)):
    #     entry = directions[i] + 'and continue for ' + distances[i]
    #     direct_and_dist.append(entry)
    # 
    # miles = distance_traveled(addr, city, state, zip_code, current_location)
    # direct_and_dist.append('Total travel time is ' + time_travel)
    # direct_and_dist.append('Total miles traveled: ' + str(miles) + 'mi')
    # 
    # return direct_and_dist