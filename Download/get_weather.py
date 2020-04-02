#!/usr/bin/python3

import time
import datetime
import schedule
import os, glob
import xarray as xr
import pyowm
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3 as db

folder = '/mnt/e/Test/T_2m'
folder = '/home/cak/Desktop/Jupyter-lumped-models/Measurements'

day = datetime.date.today()
sql_data = str(day) + '_measurements.sqlite'
# sql_data = str(day) + '.sqlite'
os.chdir(folder)


def get_data(id):
    owm = pyowm.OWM('9432d39621b9931ab44618f69f611f2d')
    observation = owm.weather_at_id(id)
    w = observation.get_weather()
    l = observation.get_location()
    t = {'Date': str(w.get_reference_time(timeformat='date')), 'temp': (w.get_temperature('celsius')['temp']),
         'clouds': w.get_clouds(), 'rain': 0 if len(w.get_rain()) == 0 else w.get_rain(),
         'wind_speed': w.get_wind()['speed'],
         'humidity': w.get_humidity(),
         'pressure': w.get_pressure()['press'], 'status': w.get_status(),
         'sunrise': str(w.get_sunrise_time(timeformat='date')),
         'sunset': str(w.get_sunset_time(timeformat='date')), 'location': str(l.get_name()), 'lat': l.get_lat(),
         'lon': l.get_lon(), 'station_id': l.get_ID()}
    print("Data taken at {}".format(str(datetime.datetime.now())))
    return t


def create_sql(sql_data, df):
    conn = db.connect(sql_data)
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS Result''')
    df.to_sql('Measurements', conn, if_exists='replace')
    print("Data written at {}".format(str(datetime.datetime.now())))


def tosql(df):
    conn = db.connect(sql_data)
    cur = conn.cursor()
    df.to_sql('Measurements', conn, if_exists='append', index=False)
    conn.commit()


stations = pd.read_csv('weather_stations.csv', names=['City', 'id', 'lat', 'lon'])
df = pd.DataFrame(columns=['Date', 'temp', 'clouds', 'rain', 'wind_speed',
                           'humidity', 'pressure', 'status', 'sunrise', 'sunset', 'location',
                           'lat', 'lon', 'station_id'])
create_sql(sql_data, df)


def to_df(df):
    for row in stations.iterrows():
        obs = get_data(row[1][1])
        df = df.append([obs])
        time.sleep(5)
    return df


while True:
    df = to_df(df)
    print("Sleeping to get write data")
    time.sleep(900)
    tosql(df)
    time.sleep(900)
    print("Sleeping to get data")

# schedule.every(20).minutes.do(to_df, df=df)
# schedule.every(25).minutes.do(tosql, df=df)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
