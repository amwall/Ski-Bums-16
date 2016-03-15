# Alison Wall and Megan Wall

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

import os
import sqlite3
import pandas as pd

from . import models

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, '../../ski-resorts.db')

CITY_1000 = os.path.dirname(__file__)
CITY_1000_FILENAME = os.path.join(CITY_1000, 'top1000_scored.csv')

CITY_200 = os.path.dirname(__file__)
CITY_200_FILENAME = os.path.join(CITY_200, 'top200_scored.csv')

def index(request):
    # the home page of the website
    return render(request, 'ski_bums/index.html')


def results(request):
    # the results page based on the search inputs
    info = {}
    if request.method == 'POST':
        current_location = request.POST['current_location']
        id_ranking = models.build_ranking(request.POST, 
                                          DATABASE_FILENAME)
        # obtain the percentile of how good the current location is
        # at accessing ski resorts
        percentile = models.score_location(current_location, 
                            CITY_1000_FILENAME, DATABASE_FILENAME) 
        info['location'] = percentile
        
        if id_ranking != []:
            addr_info = models.address_info(id_ranking)
            dir_list = []
            drive_time = []
            # obtains the general info (i.e. City, State, Elevation...)
            general_info = models.general_information(id_ranking)
            for i in range(len(addr_info)):
                # adding general information about the resort to info dict
                info['name_' + str(i + 1)] = general_info[i][0]
                info['id_' + str(i + 1)] = ['ID', general_info[i][1]]
                info['city_' + str(i + 1)] = ['City', general_info[i][2]]
                info['state_' + str(i + 1)] = ['State', general_info[i][3]]
                info['elev_' + str(i + 1)] = ['Elevation', general_info[i][4]]
                info['price_' + str(i + 1)] = (['Max Ticket Price', 
                                               '$' + str(general_info[i][5])])
                info['beg_' + str(i + 1)] = (['Beginner Slopes', 
                                             str(general_info[i][6]) + '%'])
                info['int_' + str(i + 1)] = (['Intermediate Slopes', 
                                             str(general_info[i][7]) + '%'])
                info['adv_' + str(i + 1)] = (['Advanced Slopes', 
                                             str(general_info[i][8]) + '%'])
                info['exp_' + str(i + 1)] = (['Expert Slopes', 
                                             str(general_info[i][9]) + '%'])
                # Night Skiing
                if general_info[i][10] == '0':
                    info['night_' + str(i + 1)] = ['Night Skiing', 'No']
                else:
                    info['night_' + str(i + 1)] = ['Night Skiing', 'Yes']
                # Terrain Parks
                if general_info[i][11] == '0':
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'No']
                else:
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'Yes']
                info['runs_' + str(i + 1)] = (['Total Number of Runs', 
                                              general_info[i][12]])
                info['area_' + str(i + 1)] = (['Total Area', 
                                         str(general_info[i][13]) + ' acres'])

                # adding directions/ driving time  to the info dictionary
                loc = (addr_info[i][1] + " " + addr_info[i][2] + 
                       " " + addr_info[i][3])

                time, dist = models.get_distance(loc, current_location)
                drive_time.append(time)
                info['time_' + str(i + 1)] = ['Driving Time', drive_time[i]]

                if 'driving dir' in request.POST:
                    directions = models.get_directions(loc, current_location)
                    dir_list.append(directions)
                    info['drive_' + str(i + 1)] = dir_list[i]

            ## obtaining weather information
            # if the person wants to ski within the next week
            if request.POST['week'] == 'Yes':
                days_list = models.date_distance(request.POST['date'])
                weather = models.grab_weather(id_ranking, days_list, 
                                              request.POST['week'])
            else:
                weather = models.grab_weather(id_ranking, [], 
                                              request.POST['week'])
            # adding the weather info to the info dictionary
            for i in range(len(weather)):
                current = list(weather[i][1:5])
                for j in range(len(current)):
                    if type(current[j]) == float:
                        current[j] = "{0:.2f}".format(current[j])
                info['current_' + str(i + 1)] = ['Current Weather'] + current
                # if they are skiing within the next week, add the forecast 
                # for the day they want to ski
                if request.POST['week'] == 'Yes':
                    forecast = list(weather[i][5:])
                    for j in range(len(forecast)):
                        if type(forecast[j]) == float:
                            forecast[j] = "{0:.2f}".format(forecast[j])
                    info['forecast_' + str(i + 1)] = (['Forecast for ' + 
                                        request.POST['date']] + forecast)

    return render(request, 'ski_bums/results.html', info)


def info(request):
    # obtaining information for the general information page
    sql_string = 'SELECT ID, name, city, state, dates, rating FROM main'
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    resort_list = execute.fetchall()
    connection.close()
    c = {}
    for i in range(len(resort_list)):
        c['info' + str(i)] = resort_list[i]

    return render(request, 'ski_bums/info.html', c)


def d3_ski_resorts(request):
    # Weather Interactive Map
    return render(request, 'ski_bums/d3-ski-resorts.html')


def city_graphic(request):
    # City Interactive Map
    return render(request, 'ski_bums/city_graphic.html')


def ranking(request):
    '''
    Build the city ranking from the largest 200 cities
    '''
    # ranking the top 20 cities for skiing
    df = pd.read_csv(CITY_200_FILENAME)
    df['avg_time'] = df['time'] / df['number']
    
    c = {}
    for i, city in df.iterrows():
        if i < 20:
            rv = list(city)
            avg_time = rv[-1]
            number = rv[5]
            rv = rv[1:4]
            rv.append(number)
            rv.append(avg_time)
            rv[-1] = round(rv[-1],2)
            rv.insert(0, i+1)
            
            c['city' + str(i)] = rv
        else:
            break

    return render(request, 'ski_bums/ranking.html', c)
