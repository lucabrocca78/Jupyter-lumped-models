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
day = datetime.date.today()
sql_data = str(day) + '.sqlite'
os.chdir(folder)


def get_forecast(lat, lon):
    files = glob.glob('*.nc')
    d = xr.open_dataset(files[0])
    daily = d.sel(lon=lon, lat=lat, method='nearest')
    df = daily.to_dataframe()
    df = df.set_index(daily.time.values)
    df = df.drop(['lon', 'lat'], axis=1)
    # df.to_csv('test.csv')
    return df


def create_sql(sql_data, df_weather):
    conn = db.connect(sql_data)
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS Result''')
    df_weather.to_sql('Result', conn, if_exists='replace')


def tosql(df_weather):
    conn = db.connect(sql_data)
    cur = conn.cursor()
    # cur.execute('''DROP TABLE IF EXISTS Result''')
    df_weather.to_sql('Result', conn, if_exists='append', index=True)  # - writes the pd.df to SQLIte DB
    conn.commit()


def get_data(df_weather):
    owm = pyowm.OWM('9432d39621b9931ab44618f69f611f2d')
    observation = owm.weather_at_id(323786)

    w = observation.get_weather()

    temp = (w.get_temperature('celsius')['temp'])
    time = w.get_reference_time(timeformat='date') + datetime.timedelta(hours=3)
    t = {'Date': str(time), 'temp_measured': temp}
    temp = pd.DataFrame([t])
    df_weather = df_weather.append(temp)
    df_weather = df_weather.set_index('Date')
    tosql(df_weather)
    print('data inserted at {}'.format(str(datetime.datetime.now())))
    # return df_weather


def read_data():
    conn = db.connect(sql_data)
    cur = conn.cursor()
    cur.execute("select * from Result")
    results = cur.fetchall()
    df_temp = pd.DataFrame(results, columns=['index', 'Date', 'Measured_Temp'])
    df_temp = df_temp.set_index('Date')
    df_temp = df_temp.drop(['index'], axis=1)
    df_temp.index = pd.to_datetime(df_temp.index).strftime('%Y-%m-%d %H:%M:%S')
    df_temp['Measured_Temp'] = df_temp['Measured_Temp'].astype(float)
    df_temp.index = pd.to_datetime(df_temp.index)
    return df_temp


def plot_data(df, df_temp):
    df_new = df.iloc[:24]
    ax = df_new.plot(figsize=(18, 12))
    df_temp.plot(ax=ax)
    fig = plt.gcf()
    name = datetime.datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    fig.savefig('{}.png'.format(name))
    plt.close()

lat = 39.8834
lon = 32.9013
df_weather = pd.DataFrame(columns=['Date', 'temp_measured'])
df = get_forecast(lat, lon)

create_sql(sql_data, df_weather)
schedule.every(5).minutes.do(get_data, df_weather=df_weather)
schedule.every(5).minutes.do(read_data)
df_temp = read_data()
schedule.every(5).minutes.do(plot_data, df=df, df_temp=df_temp)

# plot_data(df,df_temp)

while True:
    schedule.run_pending()
    time.sleep(1)
