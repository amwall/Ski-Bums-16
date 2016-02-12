import csv
import pandas as pd


def csv_writer(resort_list):
    
    keys = resort_list[0].keys()
    with open('ski-resorts.csv', 'w') as csvfile:
        resortwriter = csv.DictWriter(csvfile, keys)
        resortwriter.writeheader()
        resortwriter.writerows(resort_list)

def create_dataframe(path):
    
    dataframe = pd.read_csv(path, engine='python', parse_dates=True)
    # dataframe.to_pickle(pickle_name)
    return dataframe
    
def load_dataframe(file_name):
    
    pass
    
    
        
        
        
        
        