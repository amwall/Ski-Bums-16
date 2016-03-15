# Ski-Bums:
Gareth, Alison, Megan, & Syd


## Packages Required 
Our project is composed of the following:
Python3
Plotty
Sqlite3
Django

To Install run the following code in your command temrinal:
sudo pip install python3
sudo pip install plotty
sudo pip install sqlite3
sudo pip install django

## Project Overview
Our project is composed of the following:
1. **Django Website**
    * Interactive Website for displaying our data and results
2. **Data**
    * A database contaning information on resorts and their current and predicted weather.
    * A databse ranking major cities by their acess to resorts
3. **Algorithms**
    * An algorithm for producing the top 3 resorts given a user's input
    * An algorithm for ranking the user's current location relative to other cities in our database
4. **Visualizations**
    * Quality of resorts based on snowfall
    * Quality of cities for access to ski and snowboard areas

## How to run Ski-Bums:
1. Open a web browser
2. navigate to the mysite directory in the shell
3. In the shell run:
    ```
    python manage.py runserver
    ```
4. The page search page should have appeard in your browser

## File Overview 
1. **apps**: This folder contains the files for the functions that are called in our website or were used to create material
    - analysis.py: The file for creating the scored city lists and scoring the users current location
    - database.py: Used for creating the SQL database and uploading csv data into it 
    - directions.py: Uses Google's API to get directions, locations, and distances
    - forecast.py: Functions for getting the weather forecast from the database
    - scraper.py: A web scraper used to gather information from the OnTheSnow.com
    - preferences.py: The preference algorithm that is preforms a ranking with a SQL query
    - weather.py: A program for getting current weather conditions and a seven day forecast for every resort in our database. The data comes courtesy of OpenWeatherMap.org

2. **CSVs**: A directory containing the CSVs that hold our list of resorts, cities, and the weather data
    - current_weather.csv
    - forecast_weather.csv
    - ski-resorts.csv
    - ski-resorts.txt
    - top1000.csv
    - top1000_scored.csv
    - top200.csv
    - top200_scored.csv
    
3. **mysite**: This directory contains the code for running web page
    - More information on README found inside
    
4. **Other Stuff**: Presentation materials
    - Initial Presentation
    - Final Presentation
    
5. **visualization**:  A directory containing the visualizations used in the website and the program used for creating them
    - city_graphic.html: Graphic displaying cities based on their access to resorts
    - d3-ski-resorts.html: GRaphic showing resort quality based on snowfall
    - denisty-plot.html: Exploratory graph of resort data
    - newtork.hmtl: Sidelind project for displaying user's location
    - visualization.py: Program for creating visualization output
    
6. **README.md**: (This file)
