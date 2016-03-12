# preference.py
# Gareth Jones

from directions import destination, travel_time_hours

def build_ranking(search_dict, database_name):
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
    query += "score_size(total_runs, " + "'" + choice + "')"  +  ' AS total_score'
    # Connect table

    ### CUTTING ATTRIBUTES ###
    where = []
    ### DISTANCE ###
    if search_dict['max_drive_time'][0]:
        
        # query += " time_between(lon,lat,?,?) AS travel_time"
        
        where.append(" time_between(lon,lat,?,?) <= ?")
        max_time = int(search_dict['max_drive_time']) + 0.5
        cur_loc = search_dict['current_location']
        u_lat, u_lon = cur_lat_and_long(cur_loc)
        parameters.extend([u_lon, u_lat, max_time])

    
    query += ' FROM main WHERE'
    ### NIGHT SKIING ###
    if search_dict['night skiing'][0] != 'Indifferent':
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
    
    parameters = tuple(parameters)
    exc = cursor.execute(query, parameters)
    output = exc.fetchall()

    resort_ids = []
    for i in range(len(output)):
        resort_id = output[i][0]
        resort_ids.append(resort_id)
    
    return resort_ids


def compute_time_between(lon1, lat1, lon2, lat2):

    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    
    meters = haversine(lon1, lat1, lon2, lat2)
    #adjusted downwards to account for manhattan distance
    driving_speed_per_hr = 70 
    hrs = meters / driving_speed_per_hr
    return hrs

def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m 
