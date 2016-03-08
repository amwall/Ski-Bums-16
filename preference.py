# preference.py
# Gareth Jones

from directions import destination, travel_time_hours

def build_ranking(search_dict, database_name):
    '''
    The main ranking algorithm. It takes the search results and builds a query
    that returns the top three results. The program returns the IDs, which are
    the primary keys for the resorts
    '''

    db = lite.connect(database_name)
    db.create_function('score_size', 2, score_size)
    db.create_function('travel_time', 5, travel_time_hours)
    cursor = db.cursor()

    parameters = []

    query = 'SELECT ID, (size_score + run_score) AS total_score,'

    ### SCORE RUNS ###
    addition, parameters = score_runs(search_dict, parameters)
    query += addition

    ### SCORE SIZE ###
    choice = search_dict['Resort Size'][0]
    parameters.append(choice)
    query += " score_size(num_runs, ?) AS size_score"

    # Connect table
    query += ' FROM main'

    ### CUTTING ATTRIBUTES ###
    where = []
    ### DISTANCE ###
    if search_dict['max_drive_time'][0]:
        max_time = str(int(search_dict['max_drive_time'][0] + 0.5))
        cur_loc = search_dict['current_locations'][0]
        parameters.extend([cur_loc, max_time])
        where.append(" travel_time(addr,city,state,zip,?) <= ?")

    ### NIGHT SKIING ###
    if search_dict['night_skiing'][0] != 'Indifferent':
        where.append(" night=1")

    ### MAX TICKET ###
    if search_dict['max_tic_price'][0]:
        price = int(search_dict['max_tic_price'][0]) + 15
        parameters.append(str(price))
        where.append(" (max_price <= ? OR max_price='N/A')")

    ### Terrain Park ###
    if int(search_dict['Terrain parks']) > 1:
        where.append(" park > 0")

    where = " AND".join(where)
    query += where
    query += ' ORDER BY total_score DESC LIMIT 3'

    print(query)
    print(parameters)
    parameters = tuple(parameters)
    exc = cursor.execute(query, parameters)
    output = exc.fetchall()

    resort_ids = []
    for resorts in output:
        resort_id = output[0]
        resort_ids.append(resort_id)

    return resort_ids

def score_size(num_runs, choice):
    '''
    A system for scoring base on the users choice and the number of runs at
    the resort
    '''

    # SMALL: 1-35
    # MEDIUM: 35-100
    # Large: 100 +

    if choice == 'SMALL':
        sml_mlt = 5
        med_mlt = 3
        lrg_mlt = 1
    elif choice == 'MEDIUM':
        sml_mlt = 2
        med_mlt = 5
        lrg_mlt = 2
    else:
        sml_mlt = 1
        med_mlt = 3
        lrg_mlt = 5

    if num_runs >= 100:
        scr = num_runs * lrg_mlt
    elif num_runs >= 35 and num_runs < 100:
        scr = num_runs * med_mlt
    else:
        scr = num_runs * lrg_mlt

    return scr

def score_runs(search_dict, parameters):
    '''
    A function for builds a portion of the SQL query that scores based on the
    percentage of runs that are of a given difficulty.
    '''

    score_dict = {'1': 0,
                  '2': .5,
                  '3': 1,
                  '4': 2,
                  '5': 4}

    beg_mlt = score_dict[search_dict['Beginner runs'][0]]
    int_mlt = score_dict[search_dict['Intermediate runs'][0]]
    exp_mlt = score_dict[search_dict['Expert runs'][0]]
    adv_mlt = score_dict[seacrh_dict['Advanced runs'][0]]

    parameters.extend([beg_mlt, int_mlt, adv_mlt, exp_mlt])
    query = " (main.beginner * ?) + (main.intermediate * ?) + \
              (main.advanced * ?) + (main.expert * ?) AS run_score"

    return query, parameters
