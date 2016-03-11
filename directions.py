from lxml import html
import re
from urllib.request import urlopen
import json

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8'
GEOCODING_ID = 'AIzaSyB0Sx4EMq-IP2fXfzSyoRQ4-1llyKNJQgU'

def cur_lat_and_long(current_location):
    '''
    '''
    current = str(current_location).split()
    current = '+'.join(current)
    
    url =  ('https://maps.googleapis.com/maps/api/geocode/json?' +
            'address=' + current + '&key=' + GEOCODING_ID)

    request = urlopen(url)
    # print(request.read())
    test = request.read().decode("utf-8")
    print(test)
    data = json.loads(test)
    # print(data)
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    print(lat, lng)
    return lat, lng

def destination(addr, city, state, zip_code):
    '''
 
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
    print(text)
    data = json.loads(text)
    
    seconds = data['rows'][0]['elements'][0]['duration']['value']
    meters = data['rows'][0]['elements'][0]['distance']['value']
    
    time_text = data['rows'][0]['elements'][0]['duration']['text']
    dist_text = data['rows'][0]['elements'][0]['distance']['text']
    
    print(seconds, time_text)
    print(meters, dist_text)