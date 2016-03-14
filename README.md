# Ski-Bums-16
# Final Project: Winter 2016

## How to run Ski-Bums:
1. navigate to the mysite directory in the shell
2. Open a web browser
3. type:
    ```
    python manage.py runserver
    ```
4. 

## File Overview 
1. apps:
    This folder contains the files for the functions that are called in our website or were used to create material
    - database.py: Used for creating the SQL database and uploading csv data into it 
    - directions.py: Uses Google's API to get directions and driving times
    - scraper.py: A web scraper used to gather information from the OnTheSnow.com
    - preferences.py: The preference algorithm that is preforms a ranking with a SQL query
    - weather.py: A program for getting current weather conditions and a seven day forecast for every resort in our database. The data comes courtesy of OpenWeatherMap.org

2. CSVs:
    A directory containing the CSVs that hold our list of resorts and the weather data
    - current_weather.csv
    - forecast_weather.csv
    - ski-resorts.csv
    - ski-resorts.txt
    - top1000.csv
    - top1000_scored.csv
    - top200.csv
    - top200_scored.csv
3. mysite: This directory contains the code for running web page
4. Other Stuff:
    Presentation materials
5. visualization:
    A directory containing the visualizations used in the website and the program used for creating them
    
6. README.md (This file)