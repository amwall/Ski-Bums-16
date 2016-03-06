def create_dictionary():
    
    dictionary = {}
    dictionary['Night Skiing'] = False
    dictionary['Terrain Parks'] = 0
    dictionary['Beginner Runs'] = 0
    dictionary['Intermediate Runs'] = 0
    dictionary['Advanced Runs'] = 0
    dictionary['Expert Runs'] = 0
    dictionary['Runs'] = 0
    dictionary['Skiable Terrain'] = 'N/A'
    dictionary['Average Snowfall'] = 'N/A'

    return dictionary

def optimal_score(ter, beg, inte, adv, exp, resort_dict):
    
    ter_score = resort_dict['Terrain Parks'] * ter 
    beg_score = resort_dict['Beginner Parks'] * beg
    int_score = resort_dict['Intermidiate Parks'] * inte
    adv_score = resort_dict['Advanced Parks'] * adv
    exp_score = resort_dict['Expert Parks'] * exp
    
    score = beg_score + int_score + adv_score + exp_score + ter_score

    return (score)

def create_dict():
    
    dic = {'resort_1':{'Terrain Parks':10, 'Beginner Parks':20, 'Intermidiate Parks':30, 
            'Advanced Parks':40, 'Expert Parks':50}, 'resort_2':{'Terrain Parks':20, 'Beginner Parks':30, 'Intermidiate Parks':40,
            'Advanced Parks':50, 'Expert Parks':10},'resort_3':{'Terrain Parks':30, 'Beginner Parks':40, 'Intermidiate Parks':50,
            'Advanced Parks':10, 'Expert Parks':20}, 'resort_4':{'Terrain Parks':40, 'Beginner Parks':50, 'Intermidiate Parks':10,
            'Advanced Parks':20, 'Expert Parks':30}, 'resort_5':{'Terrain Parks':50, 'Beginner Parks':10, 'Intermidiate Parks':20,
            'Advanced Parks':30, 'Expert Parks':40}}

    return dic

def create_pref(ter, beg, inte, adv, exp):
    
    dic = {}
    dic['Terrain Parks'] = ter
    dic['Beginner Parks'] = beg
    dic['Intermidiate Parks'] = inte
    dic['Advanced Parks'] = adv
    dic['Expert Parks'] = exp 

    return dic

def optimal_order(pref_dict, resort_dict):
    order_list = []
    for resort in resort_dict:
        score = optimal_score(pref_dict['Terrain Parks'], pref_dict['Beginner Parks'], 
                              pref_dict['Intermidiate Parks'], pref_dict['Advanced Parks'], 
                              pref_dict['Expert Parks'], resort_dict[resort])
        tup = (resort, score)
        order_list.append(tup)
    sort_list = sorted(order_list, key=lambda x: x[1], reverse = True)

    return sort_list



