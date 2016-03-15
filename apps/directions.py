# directions.py
# Megan Wall

from urllib.request import urlopen
import json
from math import sin,cos,radians,asin,sqrt

DISTANCE_MATRIX_ID = 'AIzaSyDJ4p7topWHJW7SRAJJFY88BYVAapEkz0g'
DIRECTIONS_ID = 'AIzaSyBkmUNSECcrSIPufRXJQCEm-0OhAmH9Mm8'
GEOCODING_ID = 'AIzaSyCeg-uM3PsOT2ssRsPDfQdxZPbGz6k0kBc'


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