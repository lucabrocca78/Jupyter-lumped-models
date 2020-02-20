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
    lat = d.t2m.latitude.values
    lon = d.t2m.longitude.values
    data = {}

    for lat_ in lat[:2]:
        for lon_ in lon[:2]:
            dsloc = d.sel(longitude=lon_, latitude=lat_, method='nearest')
            data.update({'Date': time, 'Data': dsloc.t2m.values, 'Lat': lat_, 'lon': lon_})
            print(lat_,lon_)

    df = pd.DataFrame(data)
    conn = sqlite3.connect('./Data/export.db')
    df.to_sql('results', conn, if_exists='replace', index=False)

grid2ts(file,shp)