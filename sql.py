


Fields we have:
    
    Details:
        beginner
        intermediate
        advanced
        expert
        night
        park
        avg_snowfall
        rating
    Travel Time:
        Sort out distance matrix use
    
    Location:
        city
        state
    Size:
        lifts
        area
        total_runs
    Cost:
        max_price
        min_price
        
    Weather:
        seven day forecast
            - precipitation
        current

    Notes on Website:
        - (Most important)
        - Include size
        - Terrain Park (Should this be the same type of decision as Night skiing)
        
    Scoring procedure:
        Linear?
        |  1  |  2  |  3  |  4  |  5  |
    lin |  0     1     2     3     4
    non |  0     1    1.5    3     5
    
def build_ranking(search_dict):
    
    
    query = 'SELECT name, city, state, link'
   
    ###### SCORE COMPONENT #######
    score = '(run_scr'
    if...:
        score += ' + size_scr' 
    if...:
        score + ' + loc_scr' 
    score += ') as score'
    #############################
    
    query += score + ' FROM main JOIN current, forecast ON main.id=current.id, current.id=forecast.id'
    
    query += ' ORDER BY score DESC LIMIT 10'
    
def score_runs():
    
    score_dict = {'1': 0,
                  '2': 1,
                  '3': 1.5,
                  '4': 3,
                  '5': 5}
    
    for kind in search_dict:
        pref = search_dict[kind]
        multiplier = score_dict[pref]
        
    db.db = lite.connect(DATABASE_FILENAME)
    db.create_function('score_runs, 4, compute_time_between)
    cursor = db.cursor()
    exc = cursor.execute(statement, parameters)
    query = exc.fetchall()
    
def score_runs()
    
    
def score_weather():
    
    
def score_size():
    
    SMALL:
    MEDIUM:
    LARGE:
    