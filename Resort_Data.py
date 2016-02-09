# Trying to scrape http://onthesnow.com

import urllib.parse
import requests
import bs4
import util
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

    return dictionary


def go():
    '''
    '''
    page = requests.get(starting_url)
    page.raise_for_status()
    html = bs4.BeautifulSoup(page.text, 'html5lib')

    resort_dictionary = {} # key is resort name and the entry is another 
                           # dictionary containing all of the info

    resort_links = html.find_all('div', class_ = 'name')
    resort_name_and_link = []
    for resort in resort_links:
        entry = []
        a_tag = resort.find('a')
        # obtaining the name of the resort
        resort_name = a_tag['title']
        entry.append(resort_name)
        # obtaining the link to the resort
        resort_url = a_tag['href']
        resort_url = convert_if_relative_url(starting_url, resort_url)
        entry.append(resort_url)

        resort_name_and_link.append(entry)
    
    state_names = html.find_all('div', class_ = 'rRegion')
    states = []
    for state_info in state_names:
        a_tag = state_info.find('a')
        state = a_tag['title']
        states.append(state)
    # adding the resort id, link and state to the dictionary
    for i in range(len(resort_name_and_link)):
        resort = resort_name_and_link[i][0]
        resort_dictionary[resort] = create_dictionary()
        resort_dictionary[resort]['id'] = i

        link = resort_name_and_link[i][1]
        resort_dictionary[resort]['link'] = link

        state = states[i]
        resort_dictionary[resort]['state'] = state
    # Looking at all of the individual ski resorts main page
    for resort in resort_dictionary:
        page = requests.get(resort_dictionary[resort]['link'])
        page.raise_for_status()
        html = bs4.BeautifulSoup(page.text, 'html5lib')
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
            class_name = i.find('span', class_ = 'ovv_t t1')
            if class_name == None:
                resort_overview_list.append(i.text)
        # adding this info to the dictionary    
        # print(resort_overview_list)
        open_close = resort_overview_list[0]
        resort_dictionary[resort]['Open/Close Dates'] = open_close
        resort_dictionary[resort]['Elevation'] = resort_overview_list[1]
        resort_dictionary[resort]['Number Lifts'] = resort_overview_list[2]
        if 'N/A' in resort_overview_list[3]:
            resort_dictionary[resort]['Lift tickets'] = 'N/A'
        else: 
            tic_price = resort_overview_list[3]
            tic_price = re.match
            print('tic_price', tic_price)
            resort_dictionary[resort]['Lift tickets'] = tic_price
            
        print(resort_dictionary[resort])    
        #break

                

    #print(resort_dictionary['49 Degrees North'])



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