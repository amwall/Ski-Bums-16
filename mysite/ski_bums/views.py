from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

import os
import sqlite3

from . import models

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

def index(request):
    
    return render(request, 'ski_bums/index.html')


def results(request):
    info = {}
    if request.method == 'POST':
        current_location = request.POST['current_location']
        print(request.POST)
        id_ranking = models.build_ranking(request.POST, DATABASE_FILENAME)

        if id_ranking != []:
            addr_info = models.sql_info(id_ranking)
            dir_list = []
            drive_time = []
            general_info = models.general_information(id_ranking)
            for i in range(len(addr_info)):
                # adding general information about the resort to the dictionary
                info['name_' + str(i + 1)] = general_info[i][0]
                info['id_' + str(i + 1)] = ['ID', general_info[i][1]]
                info['city_' + str(i + 1)] = ['City', general_info[i][2]]
                info['state_' + str(i + 1)] = ['State', general_info[i][3]]
                info['elev_' + str(i + 1)] = ['Elevation', general_info[i][4]]
                info['price_' + str(i + 1)] = ['Max Ticket Price', '$' + str(general_info[i][5])]
                info['beg_' + str(i + 1)] = ['Beginner Slopes', str(general_info[i][6]) + '%']
                info['int_' + str(i + 1)] = ['Intermediate Slopes', str(general_info[i][7]) + '%']
                info['adv_' + str(i + 1)] = ['Advanced Slopes', str(general_info[i][8]) + '%']
                info['exp_' + str(i + 1)] = ['Expert Slopes', str(general_info[i][9]) + '%']
                if general_info[i][10] == '0':
                    info['night_' + str(i + 1)] = ['Night Skiing', 'No']
                else:
                    info['night_' + str(i + 1)] = ['Night Skiing', 'Yes']
                if general_info[i][11] == '0':
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'No']
                else:
                    info['terrain_' + str(i + 1)] = ['Terrain Parks', 'Yes']
                info['runs_' + str(i + 1)] = ['Total Number of Runs', general_info[i][12]]
                info['area_' + str(i + 1)] = ['Total Area', str(general_info[i][13]) + ' acres']


                # adding directions/ driving time  to the dictionary
                directions = models.get_directions(addr_info[i][0], addr_info[i][1],
                                            addr_info[i][2], addr_info[i][3],
                                            current_location)
                dir_list.append(directions)
                time = models.travel_time_words(addr_info[i][0], addr_info[i][1],
                                         addr_info[i][2], addr_info[i][3],
                                         current_location)
                drive_time.append(time)

                info['time_' + str(i + 1)] = ['Driving Time', drive_time[i]]

                if 'driving dir' in request.POST:
                    info['drive_' + str(i + 1)] = dir_list[i]

            if request.POST['week'] == 'Yes':
                days_list = models.date_distance(request.POST['date'])
                weather = models.grab_weather(id_ranking, days_list, request.POST['week'])
            else:
                weather = models.grab_weather(id_ranking, [], request.POST['week'])
            for i in range(len(weather)):
                current = list(weather[i][1:5])
                for j in range(len(current)):
                    if type(current[j]) == float:
                        current[j] = "{0:.2f}".format(current[j])
                info['current_' + str(i + 1)] = ['Current Weather'] + current
                if request.POST['week'] == 'Yes':
                    forecast = list(weather[i][5:])
                    for j in range(len(forecast)):
                        if type(forecast[j]) == float:
                            forecast[j] = "{0:.2f}".format(forecast[j])
                    info['forecast_' + str(i + 1)] = ['Forecast for ' + request.POST['date']] + forecast

    return render(request, 'ski_bums/results.html', info)


def info(request):

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

