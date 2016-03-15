## Files under mysite ##

db.sqlite3: Created by Django. (Did not modify)

manage.py: Created by Django. (Did not modify)

mysite: folder
    __init__.py: Created by Django. (Did not modify)
    __pycache__: Created by Django. (Did not modify)
    settings.py: Created by Django. Added an installed app and
                 changed time zone. 
    urls.py: Created by Django. Added a url to urlpatterns.
    wsgi.py: Created by Django. (Did not modify)

ski_bums: folder
    admin.py: Created by Django. (Did not modify)
    apps.py: Created by Django. Added an app to configure. 
    __init__.py: Created by Django. (Did not modify)
    migrations: a folder created by Django   
    models.py: Created by Django. Contains the SAME functions from the files under the apps folder that are used in making our output. 
    __pycache__: Created by Django. (Did not modify)
    templates: folder that contains the ski_bums folder
        ski_bums: folder that contains all of the html files
            city_graphic.html: An interactive html (obtained code online from Plotly, Inc)
            d3-ski-resorts.html: An interactive html (obtained code online from Plotly, Inc) 
            index.html: The html for our main page (Ski Resort Finder)
            info.html: The html for the general information page
            ranking.html: The html for the 
            results.html: The html for the results page
    tests.py: Created by Django. (did not modify)
    top1000_scored.csv: CSV file that contains information for the 1000 largest cities in the US
    top200_scored.csv: CSV file that contains information about the top 200 cities based on a score. These are the cities that are used in city_graphic html 
    urls.py: Created by Django. Added a url in urlpatterns for each html. 
    views.py: Created by Django. How we organized the information we wanted to output in the html documents. This is where we interacted with the user inputed data.

ski-resorts.txt: Text file that contains information about every resort
