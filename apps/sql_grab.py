
from datetime import date
import re
import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'ski-resorts.db')

def date_distance(date_ski):
    
    date_today = date.today().strftime('%m/%d/%Y')

    dat_lis = re.findall('[0-9]+',date_today)
    ski_lis = re.findall('[0-9]+',date_ski)
    
    d0 = date(int(dat_lis[2]), int(dat_lis[0]), int(dat_lis[1]))
    d1 = date(int(ski_lis[2]), int(ski_lis[0]), int(ski_lis[1]))
    delta = d1 - d0
    return list(range(delta.days))
    

def grab_weather(id_list, days_list, check):
    
    select = 'SELECT '
    fields = 'c.ID, c.wthr, c.dscr, c.temp, c.snow'

    snow_fall = []
    addition = None
    for day in days_list:
        if addition == None:
            addition = '(f.snow_' + str(day + 1)
        else:
            addition = addition + ' + f.snow_' + str(day + 1) 
    addition = addition + ') as [Total Snow Fall] '
    snow_fall.append(addition)

    weather = 'f.wthr_' + str(days_list[-1] + 1) + ', '
    description = 'f.dscr_' + str(days_list[-1] + 1) + ', '
    average_day = 'f.avg_day_' + str(days_list[-1] + 1) + ', '

    fro_cur = ' FROM current AS c '
    new_id = []
    for person in id_list:
        change = str(person)
        new_id.append(change)
    customer_id = "(" + ", ".join(new_id) + ")"
    where = 'WHERE c.ID IN ' + customer_id
    if check == 'yes':
        sql_string = (select + fields + ', ' + weather + description + average_day +
                      snow_fall[0] + 'FROM current AS c JOIN forecast AS f ON (c.ID = f.ID) ' +
                      where)
    else:
        sql_string = select + fields + fro_cur + where

    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    execute = cursor.execute(sql_string, [])
    current_weather = execute.fetchall()
    connection.close()
    
    return current_weather
        
