from datetime import date
import re

def date_distance(date_today, date_ski):
    
    dat_lis = re.findall('[0-9]+',date_today)
    ski_lis = re.findall('[0-9]+',date_ski)
    print(dat_lis)
    print(ski_lis)
    
    d0 = date(int(dat_lis[2]), int(dat_lis[0]), int(dat_lis[1]))
    d1 = date(int(ski_lis[2]), int(ski_lis[0]), int(ski_lis[1]))
    delta = d1 - d0
    print(delta.days)
    return list(range(delta.days))
    


def grab_weather(id_list, days_list, check):
    
    select = 'SELECT '
    fields = 'wthr, dscr, temp, snow '

    snow_fall = []
    addition = None
    for day in days_list:
        if addition == None:
            addition = '(' + str(day + 1) + '_snow'
        else:
            addition = addition + ' + ' + str(day + 1) + '_snow' 
    addition = addition + ') as [Total Snow Fall] '
    snow_fall.append(addition)

    weather = str(days_list[-1]) + '_wthr, '
    description = str(days_list[-1]) + '_dscr, '
    average_day = str(days_list[-1]) + '_avg_day, '

    fro_cur = 'FROM current '
    fro_for = 'FROM forecast '
    new_id = []
    for person in id_list:
        change = str(person)
        new_id.append(change)
    customer_id = "(" + ", ".join(new_id) + ")"
    where = 'WHERE ID IN ' + customer_id
    if check == 'yes':
        return (select + fields + fro_cur + where + ' UNION ' + select + weather + 
                description + average_day + snow_fall[0] + fro_for + where)
    else:
        return select + fields + fro_cur + where
        
