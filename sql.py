
import directions
# Fields we have:
#     
#     Details:
#       Runs
#         beginner
#         intermediate
#         advanced
#         expert
#       Special
#         night
#         park
#         avg_snowfall
#         rating
#     Travel Time:
#         Sort out distance matrix use
#     
#     Location:
#         city
#         state
#     Size:
#         lifts
#         area
#         total_runs
#     Cost:
#         max_price
#         min_price
#         
#     Weather:
#         seven day forecast
#             - precipitation
#         current
# 
#     Notes on Website:
#         - (Most important)
#         - Include size
#         - Terrain Park (Should this be the same type of decision as Night skiing)
#         
#     Scoring procedure:
#         Linear?
#         |  1  |  2  |  3  |  4  |  5  |
#     lin |  0     1     2     3     4
#     non |  0     1    1.5    3     5
    
def build_ranking(search_dict, database_name):
    
    db = lite.connect(DATABASE_FILENAME)
    db.create_function('score_size', 2, score_size)
    db.create_function('')
    cursor = db.cursor

    parameters = []
    
    query = 'SELECT main.ID, (size_score + run_score) AS total_scr'
    
    ### SCORE RUNS ###
    addition, parameters = score_runs(search_dict, parameters)
    query += addition
    
    ### SCORE SIZE ###
    choice = search_dict['Resort Size'][0]
    parameters.append(choice)
    query += " score_size(main.num_runs, ?) AS size_score"
    
    ### SCORE DISTANCE ###
    
    
    query += score + ' FROM main '
    
    run_fnc = '(SELECT )'
    
    query += ' ORDER BY score DESC LIMIT 10'
    
def score_size(num_runs, choice):
    
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
    
    score_dict = {1: 0,
                  2: 1,
                  3: 1.5,
                  4: 3,
                  5: 5}
    
    beg_prf = int(search_dict['Beginner runs'][0])
    int_prf = int(search_dict['Intermediate runs'][0])
    exp_prf = int(search_dict['Expert runs'][0])
    adv_prf = int(seacrh_dict['Advanced runs'][0])
    
    beg_mlt = score_dict[beg_prf]
    int_mlt = score_dict[int_prf]
    adv_mlt = score_dict[adv_prf]
    exp_mlt = score_dict[exp_prf]
    
    parameters.extend([beg_mlt, int_mlt, adv_mlt, exp_mlt])
    query = "((main.beginner * ?) + (main.intermediate * ?) + \
              (main.advanced * ?) + (main.expert * ?)) AS run_score"
    
    return query
    
    '''
    SELECT ID (run_scr + size_scr + loc_scr) AS total_scr,
    WHERE distance > ?
    ORDER BY total_scr
    LIMIT 3
    '''
    
    
def score_runs():
    pass
    
def score_weather():
    pass
    
def score_size():
    pass

    