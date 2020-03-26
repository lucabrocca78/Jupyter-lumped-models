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

file = '/mnt/e/Datasets/Soil_Moisture/Smap/2015_2020_sm_rootzone_daily.nc'
file1 = '/mnt/e/Datasets/Soil_Moisture/Smap/2015_2020_sm_surface_daily.nc'
shp = '/mnt/e/Datasets/shp/Basins.shp'
# shp = '/home/cak/Desktop/NUTS/NUTS_RG_10M_2016_4326_LEVL_0.shp'

var = ['Rootzone', 'Surface']


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



        mask = nuts_mask_poly.mask(d.isel(time=0).sel(lat=slice(35, 43), lon=slice(25, 45)),
                                   lat_name='lat',
                                   lon_name='lon')
        lat = mask.lat.values
        lon = mask.lon.values

        ID_REGION = 2
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


    daily = daily.drop(['time_bnds','crs'])

    df = daily.to_dataframe()

    df.index = df.index.astype(int)
    df.index = pd.to_datetime(df.index.astype(str))
    df.index = df.index.strftime('%m/%d/%Y')
    if type != 'area':
        df = df.drop(['lat', 'lon'], axis=1)

    return df


lat = 37
lon = 37

df_rootzone = extract_ts(file, shp, var[0], type='area', lat=lat, lon=lon)
df_surface = extract_ts(file1, shp, var[1], type='area', lat=lat, lon=lon)

df = df_surface.join([df_rootzone])
print(df.describe())
# df.cov()
df.to_csv('test.csv')
df.plot()
plt.show()
