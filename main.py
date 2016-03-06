
import scraper
import weather
import database

def build_csv():
    
    resort_dict = scraper.create_resort_list()
    database.csv_writer(resort_dict)
    
    