import xarray as xr
import os, glob
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sqlite3
import numpy as np

file = '/mnt/e/Datasets/ICON/GFS_2020-04-04_temp.nc'
file2 = '/mnt/e/Datasets/ICON/ICON_2020-04-04.nc'
measurements = '/mnt/e/Datasets/ICON/2020-04-03_measurements.sqlite'
d = xr.open_dataset(file)
lat = 39.92
lon = 32.85


def get_point_data(file):
    d = xr.open_dataset(file)
    try:
        daily = d.sel(longitude=lon, latitude=lat, method='nearest')
    except:
        ds = d['2t']
        daily = ds.sel(lon=lon, lat=lat, method='nearest')

    df = daily.to_dataframe()
    return df


df_gfs = get_point_data(file)
df_icon = get_point_data(file2)
name = 'GFS_Temp_{}'.format(os.path.basename(file)[4:14])
df_gfs.rename(columns={'TMP_2maboveground': name}, inplace=True)
df_gfs = df_gfs.drop(['longitude', 'latitude'], axis=1)
name = 'ICON_Temp_{}'.format(os.path.basename(file2)[4:14])
df_icon = df_icon.reset_index(level=[0,1])
df_icon.rename(columns={'2t': name}, inplace=True)
df_icon = df_icon.drop(['lon', 'lat','height'], axis=1)
df_icon = df_icon.set_index('time')

conn = sqlite3.connect(measurements)
cur = conn.cursor()

query = """SELECT m.Date ,m."temp" from Measurements m where m.location = "Ankara" GROUP by m.Date order by m.Date"""
cur.execute(query)
records = cur.fetchall()

df_measure = pd.DataFrame(records,columns=['time','Measurement'])
df_measure['time'] = pd.to_datetime(df_measure['time'],format='%Y-%m-%d %H:%M:%S')
df_measure['time'] = df_measure['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_measure['time'] = pd.to_datetime(df_measure['time'])
df_measure = df_measure.set_index('time')
df_measure['Measurement'] = df_measure['Measurement'].astype(np.float64)

df = df_gfs.join(df_icon)

ax = df_measure.plot()
df.plot(ax=ax)
plt.show()
print("a")

# df.plot()
# plt.show()
