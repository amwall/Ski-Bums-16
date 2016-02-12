# Trying to scrape http://onthesnow.com
# Alison Wall

import urllib.parse
import requests
import bs4
from lxml import html
import re

starting_url = 'http://www.onthesnow.com/united-states/ski-resorts.html'
limiting_domain = 'onthesnow.com'


def create_dictionary():
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


def create_resort_list():
    '''
    Gets all of the necessary information from the
    resorts

    Returns a list of dictionaries
    '''
    page = requests.get(starting_url)
    page.raise_for_status()
    html = bs4.BeautifulSoup(page.text, 'html5lib')

    resort_dictionary = {} # key is an id for the resort and the entry is 
                           # another dictionary containing all of the info
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
        #print(resort_url)
        resort_url = convert_if_relative_url(starting_url, resort_url)
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

    # Looking at all of the individual ski resorts main page
    for resort in resort_dictionary:
        page = requests.get(resort_dictionary[resort]['link'])
        page.raise_for_status()
        html = bs4.BeautifulSoup(page.text, 'html5lib')
        # info: state
        region_info = html.find('div', class_ = 'resort_header_inner_wrap')
        state = region_info.find('a')
        resort_dictionary[resort]['State'] = state['title']
        # info: num runs; % beginner, intermediate, advanced, expert;
        # num terrain parks; whether they have night skiing
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
        # entering the info into the dictonary
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
        resort_overview = html.find('div', class_ = 'resort_overview resort_box module')
        td_tags = resort_overview.find_all('td')
        resort_overview_list = []
        for i in td_tags:
            class_name = i.find('span', class_ = 'ovv_t t2')
            if class_name == None:
                resort_overview_list.append(i.text)
        # adding this info to the dictionary    
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
        # obtaining the average snowfall
        important_dates = html.find('div', id = 'resort_impdates')
        important_dates = important_dates.find_all('li')
        for date in important_dates:
            text = date.text
            if 'Average Snowfall' in text:
                average_snowfall = re.search('[0-9]+', text).group()
                resort_dictionary[resort]['Average Snowfall'] = average_snowfall
        # obtaining the towns and addresses of the resorts
        resort_contact = html.find('div', id = 'resort_contact') 
        address_info = resort_contact.find_all('p')
        address = address_info[1].text
        resort_dictionary[resort]['Address'] = address
        city = address_info[2].text
        zip_code = re.search('[0-9]+', city).group()
        if len(zip_code) == 4:
            resort_dictionary[resort]['Zip Code'] = '0' + zip_code
        else:
            resort_dictionary[resort]['Zip Code'] = zip_code
        if re.search('[A-Za-z]+', city) != None:
            town = re.search('[A-Za-z]+', city).group()
            resort_dictionary[resort]['City'] = town
        else:
            resort_dictionary[resort]['City'] = ''

    resort_list = [{}] * len(resort_dictionary)

    for resort in resort_dictionary:
        resort_info = resort_dictionary[resort]
        resort_list[resort] = resort_info

    return resort_list


def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if len(url) == 0:
        return False
    return len(urllib.parse.urlparse(url).netloc) != 0



def convert_if_relative_url(current_url, new_url):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        current_url: absolute URL
        new_url: 

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Examples:
        convert_if_relative_url("http://cs.uchicago.edu", "pa/pa1.html") yields 
            'http://cs.uchicago.edu/pa/pa.html'

        convert_if_relative_url("http://cs.uchicago.edu", "foo.edu/pa.html") yields
            'http://foo.edu/pa.html'
    '''
    if len(new_url) == 0 or not is_absolute_url(current_url):
        return None

    if is_absolute_url(new_url):
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None

    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return parsed_url.scheme + new_url
    elif new_url[:3] == "www":
        return parsed_url.scheme + new_path
    else:
        return urllib.parse.urljoin(current_url, new_url)