#!/home/cak/Desktop/Jupyter-lumped-models/venv/bin/python
import time
import datetime
import os, glob
import pandas as pd
import sqlite3 as db

folder = '/home/cak/Desktop/Jupyter-lumped-models/Measurements'
os.chdir(folder)

database = glob.glob('*.sqlite')
print(database)

df = pd.DataFrame(columns=['Date', 'temp', 'clouds', 'rain', 'rain hours', 'wind_speed',
                           'humidity', 'pressure', 'status', 'sunrise', 'sunset', 'location',
                           'lat', 'lon', 'station_id'])
for data in database:
    conn = db.connect(data)
    temp = pd.read_sql_query("select * from Measurements", conn)
    df = df.append(temp,ignore_index=True)

conn = db.connect('Merged.db')
cur = conn.cursor()
df.to_sql('Measurements', conn, if_exists='append', index=False)
conn.commit()

    #name = database[0].split('.sqlite')[0] + '.csv'

# cur = conn.cursor()
# cur.execute('select * from Measurements')
#
# rows = cur.fetchall()
#
# for row in rows:
#     print(row)
