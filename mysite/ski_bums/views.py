from django.shortcuts import render
from django.template import loader
#import pref_algo.py

# Create your views here.

# run python manage.py runserver 
from django.http import HttpResponse

def optimal_score(ter, beg, inte, adv, exp, resort_dict):
    
    
    ter_score = resort_dict['Terrain parks'][0] * ter 
    beg_score = resort_dict['Beginner runs'][0] * beg
    int_score = resort_dict['Intermidiate runs'][0] * inte
    adv_score = resort_dict['Advanced runs'][0] * adv
    exp_score = resort_dict['Expert runs'][0] * exp
    
    score = beg_score + int_score + adv_score + exp_score + ter_score
    

    return (score)

def optimal_order(pref_dict, resort_dict):
    order_list = []
    for resort in resort_dict:
        score = optimal_score(pref_dict['Terrain parks'], pref_dict['Beginner runs'], 
                              pref_dict['Intermidiate runs'], pref_dict['Advanced runs'], 
                              pref_dict['Expert runs'], resort_dict[resort])
        tup = (resort, score)
        order_list.append(tup)
    sort_list = sorted(order_list, key=lambda x: x[1], reverse = True)

    return sort_list

def index(request):
    info = {'parameters': ['Night Skiing', 'Terrain Parks', 'Beginner Slopes',
                           'Intermediate Slopes', 'Advanced Slopes', 'Expert Slopes',
                           'Amount of Runs', 'Amount of Skiable Terrain', 'Average Snowfall'],
            }
    if request.method == 'POST':
        print(request.POST)

    opti_order = (request.POST, resort_dict)


    
        #info['results'] = [..., ..., .]

        #request.POST[]
        # this is where we interact with the database

    #else: 
        # what to output when loading the page for the first time 

    #template = loader.get_template('ski_bums/index.html')

    #return HttpResponse(template.render(info, request))
    return render(request, 'ski_bums/index.html', info)


        
