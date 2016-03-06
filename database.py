# Gareth Jones
# database.py

import csv
import pandas as pd
import sqlite3 as lite

def csv_writer(info_list, filename):
    
    keys = info_list[0].keys()
    with open(filename, 'w') as csvfile:
        row_writer = csv.DictWriter(csvfile, keys)
        row_writer.writeheader()
        row_writer.writerows(info_list)

def create_dataframe(path):
    
    dataframe = pd.read_csv(path, engine='python', parse_dates=True)
    return dataframe
    
def csv_reader(filename):
    
    with open(filename, 'r') as csvfile:
        row_reader = csv.reader(csvfile)
        fields = next(row_reader)
        row_list = []
        for row in row_reader:
            row_list.append(row)
            
        return fields, row_list
    
def create_main_sql_table(read_file, db_name):
    
    '''
    This function is used to create an sql table from a list of fields, where the
    first field is the field that is the primary key
    '''
      
    conn = lite.connect(db_name)
    c = conn.cursor()
    
    fields, resort_list = csv_reader(read_file)

    exec_stmt = 'CREATE TABLE'
    exec_stmt += " 'main' ("
    
    cols = []
    for field in fields:
        if field in ('city','zip', 'name', 'state', 'addr', 'elev', 'dates', 'link'):
            kind = 'TEXT'
        elif field in ('lat', 'lon'):
            kind = 'REAL'
        else:
            kind = 'INTEGER'
        col =  "'" + field + "' " + kind
        cols.append(col)
    cols[0] = cols[0] + ' PRIMARY KEY'
    cols = ", ".join(cols)
    exec_stmt += cols + ");"
    c.execute(exec_stmt)
    
    prm_slots = ['?'] * len(fields)
    prm_slots = "(" + ",".join(prm_slots) + ")" 
    insert_stmt = 'INSERT INTO main VALUES' + prm_slots
    c.executemany(insert_stmt, resort_list)

    conn.commit()
    conn.close()

def create_weather_tables(table_name, file_name, db_name):
    
    conn = lite.connect(db_name)
    c = conn.cursor()
    
    fields, rows = csv_reader(file_name)
    
    drop = "DROP TABLE IF EXISTS " + table_name
    c.execute(drop)
    conn.commit()
    
    cols = []
    for field in fields:
        if field[2:6] in 'wthr_dscr':
            kind = 'TEXT'
        elif field in ('wthr', 'dscr'):
            kind = 'TEXT'
        else:
            kind = 'REAL'
        col =  "'" + field + "' " + kind
        cols.append(col)
        
    cols[0] = cols[0] + ' PRIMARY KEY'
    cols = ", ".join(cols)
    exec_stmt = 'CREATE TABLE ' + table_name + '(' + cols + ')'
    c.execute(exec_stmt)
    
    conn.commit()
    conn.close()
    