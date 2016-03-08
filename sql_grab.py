from datetime import date
import datetime
import re
import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

def date_distance(date_ski):
    
    date_today = datetime.date.today().strftime('%m/%d/%Y')

    dat_lis = re.findall('[0-9]+',date_today)
    ski_lis = re.findall('[0-9]+',date_ski)
    print(dat_lis)
    print(ski_lis)
    
    d0 = date(int(dat_lis[2]), int(dat_lis[0]), int(dat_lis[1]))
    d1 = date(int(ski_lis[2]), int(ski_lis[0]), int(ski_lis[1]))
    delta = d1 - d0
    print(delta.days)
    return list(range(delta.days))
    


<<<<<<< HEAD
def grab_weather(id_list, days_list, check = 'no'):
=======
def grab_weather(id_list, days_list, check):
    
>>>>>>> beb4673d75e4630abe0fb23178a9ff40d3641b95
    select = 'SELECT '
    fields = 'wthr, dscr, temp, snow '

    snow_fall = []
    addition = None
    for day in days_list:
        if addition == None:
            addition = '(snow_' + str(day + 1)
        else:
            addition = addition + ' + snow_' + str(day + 1) 
    addition = addition + ') as [Total Snow Fall] '
    snow_fall.append(addition)

    weather = 'wthr_' + str(days_list[-1]) + ', '
    description = 'dscr_' + str(days_list[-1]) + ', '
    average_day = 'avg_day_' + str(days_list[-1]) + ', '

    fro_cur = 'FROM current '
    fro_for = 'FROM forecast '
    new_id = []
    for person in id_list:
        change = str(person)
        new_id.append(change)
    customer_id = "(" + ", ".join(new_id) + ")"
    where = 'WHERE ID IN ' + customer_id
    if check == 'yes':
        sql_string = (select + fields + fro_cur + where + ' UNION ' + select + weather + 
                description + average_day + snow_fall[0] + fro_for + where)
    else:
        sql_string = select + fields + fro_cur + where

    print(sql_string)
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    output = execute.fetchall()
    connection.close()

    print(output)
        
