import xarray as xr
import numpy as np
import regionmask
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

file = './Data/ERA5/test.nc'
# shp = './Data/shp/Karasu_all.shp'
shp = './Data/shp/Karasu.shp'
shp = './Data/shp/test_data.shp'
shp = './file_uploads/drawed.shp'
lat = np.loadtxt('lat.txt')
lon = np.loadtxt('lon.txt')

def grid2ts(file, shp):
    # file = '/media/cak/AT/Datasets/EOBS/temp2.nc'

    # file = '/media/cak/AT/Datasets/SM2RAIN/SM2RAIN_ASCAT_0125_2016_v1.1.nc'
    # shp = '/home/cak/Desktop/SHP/Karasu_all.shp'
    # shp = '/home/cak/Desktop/at/NUTS_RG_60M_2016_4326_LEVL_0.shp'
    resample = False
    factor = 2

    nuts = gpd.read_file(shp)
    # nuts.head()
    num = len(nuts)
    d = xr.open_mfdataset(file, chunks={'time': 10})
    d = d.assign_coords(longitude=(((d.longitude + 180) % 360) - 180)).sortby('longitude')

    time = d.time.values
    all = len(lat) * len(lon)
    # lat = d.t2m.latitude.values
    # lon = d.t2m.longitude.values
    data = {}
    # time = pd.date_range('2019-01-01', freq='H', periods=2)
    data = pd.DataFrame(columns=['Date', 'Data', 'ID'])
    index_db = pd.DataFrame(columns=['ID', 'Lat', 'Lon'])
    index = 1
    for lat_ in lat[:2]:
        for lon_ in lon:
            dsloc = d.sel(longitude=lon_, latitude=lat_, time=time, method='nearest')
            t = {'Date': time, 'Data': dsloc.t2m.values, 'ID': len(time) * [index]}
            temp = pd.DataFrame(t)
            data = data.append(temp)
            index_db = index_db.append({'ID': index, 'Lat': lat_, 'Lon': lon_}, ignore_index=True)
            print(lat_, lon_, index, '/', all)
            index += 1

    # data = data.subtract(273, axis='Data')
    conn = sqlite3.connect('./Data/export.db')
    data.to_sql('results', conn, if_exists='replace', index=False)
    conn = sqlite3.connect('./Data/index.db')
    index_db.to_sql('Coordinates', conn, if_exists='replace', index=False)


grid2ts(file, shp)
