# Trying to scrape http://onthesnow.com
# Alison Wall

import urllib.parse
import requests
import bs4
from lxml import html
import re
from urllib.request import urlopen

starting_url = 'http://www.onthesnow.com/united-states/ski-resorts.html'
limiting_domain = 'onthesnow.com'

GEOCODING_ID = 'AIzaSyB0Sx4EMq-IP2fXfzSyoRQ4-1llyKNJQgU'


def create_dictionary():
    '''
    Creates a dictionary containing some of the general
    information obtained from the website

    Returns:
        a list of dictionaries
    '''
    dictionary = {}
    dictionary['Night Skiing'] = False
    dictionary['Terrain Parks'] = 0
    dictionary['Beginner Runs'] = 0
    dictionary['Intermediate Runs'] = 0
    dictionary['Advanced Runs'] = 0
    dictionary['Expert Runs'] = 0
    dictionary['Runs'] = 0
    dictionary['Skiable Terrain'] = 'N/A'
    dictionary['Average Snowfall'] = 'N/A'

    return dictionary


def latitude_and_longitude(address, city, state, zip_code):
    '''
    Returns the latitude and longitude of a given location

    Inputs:
        address: address
        city: city
        state: two letter name for the state (Ex. IL)
        zip_code: zip code
    '''
    num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # Uses address as location if it exists and is not a P.O. Box
    if address != '' and address[0] in num_list:
        location = address.split()
        location = ('+'.join(location) + '+' + city + '+' + 
                    '+'.join(state.split()) + '+' + zip_code)
    # Uses city as location if no address is given
    elif city != '':
        city = '+'.join(city.split())
        state = '+'.join(state.split())
        location = city + '+' + state + '+' + zip_code
    # Otherwise, just uses zip code as location
    else:
        location = zip_code

    url =  ('https://maps.googleapis.com/maps/api/geocode/json?' +
             'address=' + location + '&key=' + GEOCODING_ID)

    url = urlopen(url)
    text = url.read()
    text = text.decode('utf-8')
    # Using re to obtain lat and lon
    lat = re.findall('"lat"\s:\s[0-9\.\-]+', text)
    lat = float(re.findall('[0-9\.\-]+', lat[0])[0])
    lng = re.findall('"lng"\s:\s[0-9\.\-]+', text)
    lng = float(re.findall('[0-9\.\-]+', lng[0])[0])

    return lat, lng


def create_resort_list():
    '''
    Gets all of the necessary information from the
    resorts from onthesnow.com

    Returns a list of dictionaries
    '''
    page = requests.get(starting_url)
    page.raise_for_status()
    html = bs4.BeautifulSoup(page.text, 'html5lib')
    # creates a dictionary where the key is an id for the reosrt 
    # and the entry in another dictionary containing all of the info
    resort_dictionary = {} 
    # getting the rating of the resorts (out of 5 stars)
    rating_tags = html.find_all('b', class_ = 'rating_small')
    rating_list = []
    for i in rating_tags:
        b_tag = i.find_all('b')
        rating = b_tag[1].text
        rating_list.append(rating)
    # getting the name and the links of the resorts
    resort_links = html.find_all('div', class_ = 'name')
    resort_name_and_link = []
    for resort in resort_links:
        entry = []
        a_tag = resort.find('a')
        # name of the resort
        resort_name = a_tag['title']
        entry.append(resort_name)
        # link to the resort
        resort_url = a_tag['href']
        resort_url = 'http://www.' + limiting_domain + resort_url 

        entry.append(resort_url)

        resort_name_and_link.append(entry)

    # adding the resort name, link, and rating to the dictionary
    for i in range(len(resort_name_and_link)):
        resort = resort_name_and_link[i][0]
        resort_dictionary[i] = create_dictionary()
        resort_dictionary[i]['Resort Name'] = resort

        link = resort_name_and_link[i][1]
        resort_dictionary[i]['link'] = link

        rate = rating_list[i]
        resort_dictionary[i]['Rating'] = rate

    # Looking at all of the individual ski resorts main page and obtaining 
    # general info about each resort such as night skiing, terrain parks, etc.
    for resort in resort_dictionary:
        page = requests.get(resort_dictionary[resort]['link'])
        page.raise_for_status()
        html = bs4.BeautifulSoup(page.text, 'html5lib')
        # info: state
        region_info = html.find('div', class_ = 'resort_header_inner_wrap')
        state = region_info.find('a')
        resort_dictionary[resort]['State'] = state['title']
        # info: num runs, % beginner, % intermediate, % advanced, % expert,
        # num terrain parks, whether they have night skiing
        terrain_table = html.find_all('p')
        terrain_info = []
        for p_tag in terrain_table:
            if p_tag.has_attr('class'):
                entry = []
                if 'label' in p_tag['class']:
                    entry.append(p_tag.text)
                if 'value' in p_tag['class']:
                    entry.append(p_tag.text)

                if entry != []:
                    terrain_info.append(entry)
        # entering the terrain_info into the dictonary
        for i in range(0, len(terrain_info), 2):
            info = terrain_info[i][0]
            if info in resort_dictionary[resort]:
                if info == 'Night Skiing':
                    resort_dictionary[resort]['Night Skiing'] = True
                else:
                    value = terrain_info[i + 1]
                    value = re.search('[0-9]+', value[0]).group()
                    resort_dictionary[resort][info] = value
        # info: open/close dates, elevation, num lifts, lift tickets
        resort_overview = html.find('div', 
                          class_ = 'resort_overview resort_box module')
        td_tags = resort_overview.find_all('td')
        resort_overview_list = []
        for i in td_tags:
            class_name = i.find('span', class_ = 'ovv_t t2')
            if class_name == None:
                resort_overview_list.append(i.text)
        # adding this info (resort_overview_list) to the dictionary    
        open_close = resort_overview_list[0]
        open_close = re.findall('[0-9]+/[\s]*[0-9]+', open_close)
        open_close = open_close[0] + '-' + open_close[1]
        resort_dictionary[resort]['Open/Close Dates'] = open_close
        resort_dictionary[resort]['Elevation'] = resort_overview_list[1]
        resort_dictionary[resort]['Number Lifts'] = resort_overview_list[2]
        if 'N/A' in resort_overview_list[3]:
            resort_dictionary[resort]['Min Ticket Price'] = 'N/A'
            resort_dictionary[resort]['Max Ticket Price'] = 'N/A'
        else: 
            tic_price = resort_overview_list[3]
            tic_price = re.findall('[0-9]+.[0-9]+', tic_price)
            resort_dictionary[resort]['Min Ticket Price'] = tic_price[0]
            resort_dictionary[resort]['Max Ticket Price'] = tic_price[1]  
        # obtaining the average snowfall and adding to dictionary
        important_dates = html.find('div', id = 'resort_impdates')
        important_dates = important_dates.find_all('li')
        for date in important_dates:
            text = date.text
            if 'Average Snowfall' in text:
                average_snowfall = re.search('[0-9]+', text).group()
                resort_dictionary[resort]['Average Snowfall'] = 
                                                        average_snowfall
        # obtaining the town, address, and zip code of the resort
        resort_contact = html.find('div', id = 'resort_contact') 
        address_info = resort_contact.find_all('p')
        address = address_info[1].text
        resort_dictionary[resort]['Address'] = address
        
        city = address_info[2].text
        zip_code = re.search('[0-9]+', city).group()
        # if the zip code starts with a 0
        if len(zip_code) == 4:
            resort_dictionary[resort]['Zip Code'] = '0' + zip_code
        else:
            resort_dictionary[resort]['Zip Code'] = zip_code
        # if a town is available for the resort
        if re.search('[A-Za-z]+', city) != None:
            town = re.search('[A-Za-z]+', city).group()
            resort_dictionary[resort]['City'] = town
        else:
            resort_dictionary[resort]['City'] = ''
        # obtaining the latitude and longitude of the resort
        lat, lon = latitude_and_longitude(resort_dictionary[resort]['Address'],
                resort_dictionary[resort]['City'], 
                resort_dictionary[resort]['State'],
                resort_dictionary[resort]['Zip Code'])
        resort_dictionary[resort]['Latitude'] = lat
        resort_dictionary[resort]['Longitude'] = lon

    # creating a list of dictionaries where the index in the list 
    # corresponds to the id number of the resort 
    resort_list = [{}] * len(resort_dictionary)

    for resort in resort_dictionary:
        resort_info = resort_dictionary[resort]
        resort_list[resort] = resort_info

    return resort_list



