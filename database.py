import csv

def csv_writer(dictionary):
        
    with open('ski-resorts.csv', 'w', newline='') as f:
        resortwriter = csv.writer(f, delimeter='|')
        
        keys = dictionary