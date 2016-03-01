from django.shortcuts import render
from django.template import loader

# Create your views here.

# run python manage.py runserver 
from django.http import HttpResponse


def index(request):
    info = {'parameters': ['Night Skiing', 'Terrain Parks', 'Beginner Slopes',
                           'Intermediate Slopes', 'Advanced Slopes', 'Expert Slopes',
                           'Amount of Runs', 'Amount of Skiable Terrain', 'Average Snowfall'],
            }
    if request.method == 'POST':
        print(request.POST)


        info['results'] = [..., ..., .]

        #request.POST[]
        # this is where we interact with the database

    #else: 
        # what to output when loading the page for the first time 

    #template = loader.get_template('ski_bums/index.html')

    #return HttpResponse(template.render(info, request))
     return render(request, 'ski_bums/index.html', info)


        
