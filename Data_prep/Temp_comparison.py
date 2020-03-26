import os, glob
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import geopandas as gpd
import regionmask
import cartopy.crs as ccrs
from osgeo import gdal, ogr
import sqlite3

file = '/mnt/e/Datasets/Temperature/rename/Agro_temp.nc'
file1 = '/mnt/e/Datasets/Temperature/rename/Era5_land_temp.nc'
file2 = '/mnt/e/Datasets/Temperature/rename/Smap_temp.nc'
file3 = '/mnt/e/Datasets/Temperature/rename/E_OBS_temp.nc'
file4 = '/mnt/e/Datasets/Temperature/rename/Merra2_temp.nc'
shp = '/mnt/e/Datasets/shp/Basins.shp'
# shp = '/home/cak/Desktop/NUTS/NUTS_RG_10M_2016_4326_LEVL_0.shp'

var = ['Agro', 'Era5', 'Smap', 'Eobs', 'Merra2']


def plot(mask, d, nuts):
    proj = ccrs.EqualEarth(central_longitude=0)
    ax = plt.subplot(111, projection=proj)
    d.isel(time=1).temp.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree())
    ax.coastlines()
    plt.show()

    plt.figure(figsize=(12, 8))
    ax = plt.axes()
    mask.plot(ax=ax)
    nuts.plot(ax=ax, alpha=0.8, facecolor='none', lw=1)
    plt.show()


def extract_ts(file, shp, var, type='area', lat=34, lon=34):
    d = xr.open_dataset(file)
    if type == 'area':
        nuts = gpd.read_file(shp)
        num = len(nuts)
        nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.ID),
                                            abbrevs=list(nuts.ID),
                                            outlines=list(nuts.geometry.values[i] for i in range(0, num)))
        print(nuts_mask_poly)

        if var in ['Smap', 'Eobs', 'Merra2']:
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(lat=slice(35, 43), lon=slice(25, 45)),
                                       lat_name='lat',
                                       lon_name='lon')
        else:
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(lat=slice(43, 35), lon=slice(25, 45)),
                                       lat_name='lat',
                                       lon_name='lon')
        lat = mask.lat.values
        lon = mask.lon.values

        ID_REGION = 0
        # print(nuts.NUTS_ID[ID_REGION])
        print(nuts.ID[ID_REGION])

        sel_mask = mask.where(mask == ID_REGION).values

        id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
        id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

        try:
            out_sel = d.sel(lat=slice(id_lat[0], id_lat[-1]),
                            lon=slice(id_lon[0], id_lon[-1])).compute().where(
                mask == ID_REGION)
            daily = out_sel.mean(dim=('lat', 'lon'), skipna=True)
        except:
            daily = d.mean(dim=('lat', 'lon'), skipna=True)
            daily['temp'] = 0

    else:
        daily = d.sel(lon=lon, lat=lat, method='nearest')

    if var in ['Era5', 'Smap']:
        daily = daily.drop('time_bnds')

    if var != 'Eobs' and daily.temp.values.max() != 0:
        daily['temp'] = daily['temp'] - 273
    daily = daily.rename({'temp': var + '_' + 'temp'})
    df = daily.to_dataframe()
    if var == 'Smap':
        df.index = df.index.astype(int)
        df.index = pd.to_datetime(df.index.astype(str))
        df = df.drop('crs', axis=1)
    df.index = df.index.strftime('%m/%d/%Y')
    if type != 'area':
        df = df.drop(['lat', 'lon'], axis=1)

    return df


conn = sqlite3.connect('/mnt/e/Datasets/Temperature/temp_db/data.sqlite')
cur = conn.cursor()

stationid = 18677
query = """SELECT  DISTINCT stations.lat,stations.lon  FROM  "Data" d join stations  on d.stationid  = stations.Station where d.stationid  = {} """.format(
    stationid)
cur.execute(query)
records = cur.fetchall()

df_Era5_p = extract_ts(file1, shp, var[1], type='area', lon=records[0][1], lat=records[0][0])
df_Agro_p = extract_ts(file, shp, var[0], type='area', lon=records[0][1], lat=records[0][0])
df_smap = extract_ts(file2, shp, var[2], type='area', lon=records[0][1], lat=records[0][0])
df_eobs = extract_ts(file3, shp, var[3], type='area', lon=records[0][1], lat=records[0][0])
df_merra2 = extract_ts(file4, shp, var[4], type='area', lon=records[0][1], lat=records[0][0])

query = """SELECT  d.date ,d."temp" FROM  "Data" d  WHERE d.stationid  = {} ORDER  by date ;""".format(stationid)
cur.execute(query)
records = cur.fetchall()
measure = pd.DataFrame(records, columns=['time', 'Measurement'])
measure = measure.set_index('time')
measure.index = pd.to_datetime(measure.index, format='%Y-%m-%d')
measure.index = measure.index.strftime('%m/%d/%Y')

df = measure.join([df_Era5_p, df_Agro_p, df_smap, df_eobs, df_merra2])
print(df.describe())
# df.cov()
df.to_csv('test.csv')
df.plot()
plt.show()
