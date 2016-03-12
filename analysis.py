import pandas as pd
import seaborn as sb
from directions import get_lat_lon, compute_time_between
from database import csv_writer
import sqlite3 as lite


def gather_city_data(city_csv, db_name, output_name):
    
    conn = lite.connect(db_name)
    c = conn.cursor()
    conn.create_function('time_between', 4, compute_time_between)
    cities = pd.read_csv(city_csv)
    rows = []
    for i, city in cities.iterrows():
        # print(city['City'], city['State'])
        lat, lon = get_lat_lon(city['City'] + " " + city['State'])
        params = (lon,lat,lon,lat)
        query = "SELECT SUM(area), SUM(time_between(lon, lat, ?, ?)), COUNT(*) FROM main WHERE time_between(lon, lat, ?, ?) < 3.25"
        result = c.execute(query, params)
        area, time, count = list(result)[0]
        rows.append((city['City'], city['State'], area, time, count))
    
    labels = ['city','state','area','time','number']
    csv_writer(labels,rows,output_name)
    
def analyze_data(city_score_csv):
    
    df = pd.read_csv(city_score_csv)
    avg_area = df['area'].mean()
    avg_time = df['time'].mean()
    

def return_user_score(user):
    
    pass