# preference.py
# Syd Reynolds & Gareth Jones


import sqlite3
from directions import compute_time_between, get_lat_lon

def build_ranking(search_dict, database_name='ski-resorts.db'):
    '''
    The main ranking algorithm. It takes the search results and builds a query
    that returns the top three results. The program returns the IDs, which are
    the primary keys for the resorts
    '''

    db = sqlite3.connect(database_name)
    db.create_function('score_size', 2, score_size)     
    db.create_function('time_between', 4, compute_time_between)
    cursor = db.cursor()    

    parameters = []

    query = 'SELECT ID, '  #size_score + run_score AS total_score,'

    ### SCORE RUNS ###
    addition, parameters = score_runs(search_dict, parameters)
    query += addition

    ### SCORE SIZE ###
    choice = search_dict['Resort Size']
    # print(choice)
    query += "score_size(area, " + "'" + choice + "')"  +  ' AS total_score'
    # Connect table

    ### CUTTING ATTRIBUTES ###
    where = []
    ### DISTANCE ###
        
    where.append(" time_between(lon,lat,?,?) <= ?")
    max_time = float(search_dict['max_drive_time']) + 0.5  #Marginally increase bounds
    print(max_time)
    cur_loc = search_dict['current_location']
    u_lat, u_lon = get_lat_lon(cur_loc)
    parameters.extend([u_lon, u_lat, max_time])

    query += ' FROM main WHERE'
    ### NIGHT SKIING ###
    if search_dict['night skiing'] != 'Indifferent':
        where.append(" night=1")

    ### MAX TICKET ###
    if search_dict['max_tic_price']:
        price = int(search_dict['max_tic_price'])
        parameters.append(price)
        where.append(" (max_price <= ? OR max_price='N/A')")

    ### Terrain Park ###
    if int(search_dict['Terrain parks']) > 1:
        where.append(" park > 0")

    where = " AND".join(where)
    query += where
    query += ' ORDER BY total_score DESC LIMIT 3'
    print('QUERY', query)
    parameters = tuple(parameters)
    print('PARAMS', parameters)
    exc = cursor.execute(query, parameters)
    output = exc.fetchall()

    resort_ids = []
    for i in range(len(output)):
        resort_id = output[i][0]
        resort_ids.append(resort_id)
        
    return resort_ids

def score_size(area, choice):
    '''
    A system for scoring base on the users choice and the number of runs at
    the resort
    SMALL: 0-750
    MEDIUM: 750-2000
    Large: 2000 +
    '''
    print(area, choice)
    if area == 'N/A':
        area = 1000

    if choice == 'Small':
        sml_mlt = 80
        med_mlt = 1
        lrg_mlt = 0.5
    elif choice == 'Medium':
        sml_mlt = 5
        med_mlt = 2
        lrg_mlt = 1
    else:
        sml_mlt = 3
        med_mlt = 1
        lrg_mlt = 1.25

    if (area >= 0 and area < 750):
        scr = area * sml_mlt
    elif (area >= 750 and area < 2000):
        scr = area * med_mlt
    else:
        scr = area * lrg_mlt

    return scr

def score_runs(search_dict, parameters):
    '''
    A function for builds a portion of the SQL query that scores based on the
    percentage of runs that are of a given difficulty.
    '''
    score_dict = {'1': 0,
                  '2': 25,
                  '3': 50,
                  '4': 100,
                  '5': 200}

    beg_mlt = score_dict[search_dict['Beginner runs']]
    int_mlt = score_dict[search_dict['Intermediate runs']]
    exp_mlt = score_dict[search_dict['Expert runs']]
    adv_mlt = score_dict[search_dict['Advanced runs']]

    parameters.extend([beg_mlt, int_mlt, adv_mlt, exp_mlt])
    query = " beginner * ? + intermediate * ? + advanced * ? + expert * ? + "
    
    return query, parameters