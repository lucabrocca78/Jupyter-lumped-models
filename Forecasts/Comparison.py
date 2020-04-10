#!/usr/bin/python3
import xarray as xr
import os, glob
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sqlite3
import numpy as np

plt.style.use(['ieee'])
# plt.style.use(['high-vis'])

day = datetime.date.today().strftime("%Y-%m-%d")
day = '2020-04-05'
file = '/home/cak/Desktop/Jupyter-lumped-models/Forecasts/GFS/Data/GFS_{}_temp.nc'.format(
    day)
file2 = '/home/cak/Desktop/Jupyter-lumped-models/Forecasts/DWD/Data/ICON_{}.nc'.format(
    day)
file3 = '/home/cak/Desktop/Jupyter-lumped-models/Forecasts/GEM/Data/GEM_{}.nc'.format(
    day)
file4 = '/home/cak/Desktop/Jupyter-lumped-models/Forecasts/ARPEGE/Data/ARPEGE_{}_temp_C.nc'.format(day)

# file = '/mnt/e/Datasets/ICON/GFS_2020-04-04_temp.nc'
# file2 = '/mnt/e/Datasets/ICON/ICON_2020-04-04.nc'
# file3 = '/mnt/e/koray/Data/GEM_2020-04-05.nc'
# file4 = '/mnt/e/Datasets/ICON/ARPEGE_2020-04-05_temp_C.nc'
measurements = '/home/cak/Desktop/Jupyter-lumped-models/Measurements/2020-04-06_measurements.sqlite'
w_s = '/home/cak/Desktop/Jupyter-lumped-models/Data_prep/weather_stations.csv'
stations = pd.read_csv(w_s, header=None)
os.chdir('/home/cak/Desktop/Jupyter-lumped-models/Forecasts/compare')


def get_point_data(file, lat, lon):
    d = xr.open_dataset(file)
    try:
        daily = d.sel(longitude=lon, latitude=lat, method='nearest')
    except:
        ds = d['2t']
        daily = ds.sel(lon=lon, lat=lat, method='nearest')

    df = daily.to_dataframe()
    return df


for i, row in stations.iterrows():
    lat = row[2]
    lon = row[3]
    city = row[0]
    station_id = row[1]
    df_gfs = get_point_data(file, lat, lon)
    name = 'GFS'
    df_gfs.rename(columns={'TMP_2maboveground': name}, inplace=True)
    df_gfs = df_gfs.drop(['longitude', 'latitude'], axis=1)

    name = 'ICON'
    df_icon = get_point_data(file2, lat, lon)
    df_icon = df_icon.reset_index(level=[0, 1])
    df_icon.rename(columns={'2t': name}, inplace=True)
    df_icon = df_icon.drop(['lon', 'lat', 'height'], axis=1)
    df_icon = df_icon.set_index('time')

    name = 'GEM'
    df_gem = get_point_data(file3, lat, lon)
    df_gem = df_gem.drop(['longitude', 'latitude'], axis=1)
    df_gem.rename(columns={'TMP_2maboveground': name}, inplace=True)

    name = 'ARPEGE'
    df_arpege = get_point_data(file4, lat, lon)
    df_arpege = df_arpege.drop(['longitude', 'latitude'], axis=1)
    df_arpege.rename(columns={'TMP_2maboveground': name}, inplace=True)

    conn = sqlite3.connect(measurements)
    cur = conn.cursor()

    query = """SELECT m.Date,m."temp" from Measurements m where m.station_id ={} GROUP by m.Date ORDER by m.Date ;""".format(
        station_id)
    cur.execute(query)
    records = cur.fetchall()

    df_measure = pd.DataFrame(records, columns=['time', 'Measurement'])
    df_measure['time'] = pd.to_datetime(df_measure['time'], format='%Y-%m-%d %H:%M:%S')
    df_measure['time'] = df_measure['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_measure['time'] = pd.to_datetime(df_measure['time'])
    df_measure = df_measure.set_index('time')
    df_measure['Measurement'] = df_measure['Measurement'].astype(np.float64)

    df = df_gfs.join(df_icon)
    df = df.join(df_arpege)
    # axs[i].plot(df.index, df[['GFS_Temp_2020-04-04','ICON_Temp__2020-04-0']],df_measure.index, df_measure['Measurement'])

    # df_measure.plot(ax=axes[0,0])
    # with plt.style.context(['science', 'ieee', 'high-vis']):
    with plt.style.context(['science', 'ieee', 'high-vis', 'no-latex']):
        # with plt.style.context(['science', 'ieee']):
        ax = df_measure.plot(figsize=(12, 6))
        ax1 = df.plot(ax=ax)
        df_gem.plot(ax=ax1)
        ax.set(title=city)
        ax.set(xlabel='Date')
        ax.set(ylabel='Temprature , C')
    # ax.autoscale(tight=True)

    # plt.title(city)
    # plt.ylabel('Temprature , C')
    # plt.xlabel('Date')
    print(city)
    plt.savefig(city + '.png', dpi=300)

    query = """SELECT m.Date,m."rain" from Measurements m where m.station_id ={} GROUP by m.Date ORDER by m.Date ;""".format(
        station_id)
    cur.execute(query)
    records = cur.fetchall()

    df_measure = pd.DataFrame(records, columns=['time', 'Measurement'])
    df_measure['time'] = pd.to_datetime(df_measure['time'], format='%Y-%m-%d %H:%M:%S')
    df_measure['time'] = df_measure['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_measure['time'] = pd.to_datetime(df_measure['time'])
    df_measure = df_measure.set_index('time')
    df_measure['Measurement'] = df_measure['Measurement'].astype(np.float64)
    print("a")
# for i, col in enumerate(df2.columns):
#     print(col)
#     df2[col].plot(kind="box", ax=axes[i])

    df_measure = pd.DataFrame(records, columns=['time', 'Measurement'])
    df_measure['time'] = pd.to_datetime(df_measure['time'], format='%Y-%m-%d %H:%M:%S')
    df_measure['time'] = df_measure['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_measure['time'] = pd.to_datetime(df_measure['time'])
    df_measure = df_measure.set_index('time')
    df_measure['Measurement'] = df_measure['Measurement'].astype(np.float64)
    d = df_measure.groupby(pd.Grouper(freq='1D')).sum()
    # print("a")
