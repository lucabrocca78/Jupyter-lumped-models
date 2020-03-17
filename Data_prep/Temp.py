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

file = '/media/D/Datasets/Temperature/Agro_temp.nc'
file1 = '/media/D/Datasets/Temperature/Era5_land_temp.nc'
shp = '/home/cak/Desktop/Jupyter-lumped-models/Data/shp/Basins.shp'
# shp = '/home/cak/Desktop/NUTS/NUTS_RG_10M_2016_4326_LEVL_0.shp'

var = ['Agro', 'Era5']


def extract_ts(file, shp, var, type='area', lat=34, lon=34):
    d = xr.open_dataset(file)
    if type == 'area':
        nuts = gpd.read_file(shp)
        num = len(nuts)
        nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.ID),
                                            abbrevs=list(nuts.ID),
                                            outlines=list(nuts.geometry.values[i] for i in range(0, num)))
        print(nuts_mask_poly)

        if var == 'Agro':
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(lat=slice(43, 35), lon=slice(25, 45)), lat_name='lat',
                                       lon_name='lon')
            lat = mask.lat.values
            lon = mask.lon.values
        else:
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(43, 35), longitude=slice(25, 45)),
                                       lat_name='latitude',
                                       lon_name='longitude')
            lat = mask.latitude.values
            lon = mask.longitude.values

        ID_REGION = 1
        # print(nuts.NUTS_ID[ID_REGION])
        print(nuts.ID[ID_REGION])

        sel_mask = mask.where(mask == ID_REGION).values

        id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
        id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

        if var == 'Agro':
            out_sel = d.sel(lat=slice(id_lat[0], id_lat[-1]), lon=slice(id_lon[0], id_lon[-1])).compute().where(
                mask == ID_REGION)
            daily = out_sel.mean(dim=('lat', 'lon'))
        else:
            out_sel = d.sel(latitude=slice(id_lat[0], id_lat[-1]),
                            longitude=slice(id_lon[0], id_lon[-1])).compute().where(
                mask == ID_REGION)
            daily = out_sel.mean(dim=('latitude', 'longitude'))
    else:
        if var == 'Agro':
            daily = d.sel(lon=lon, lat=lat, method='nearest')
        else:
            daily = d.sel(longitude=lon, latitude=lat, method='nearest')
            daily = daily.drop('time_bnds')
    for key in daily.keys():
        daily[key] = daily[key] - 273
        daily = daily.rename({key: var + '_' + key})
    df = daily.to_dataframe()
    df.index = df.index.strftime('%m/%d/%Y')

    return df


# df_Agro = extract_ts(file, shp, var[0])
# df_Era5 = extract_ts(file1, shp, var[1])

lat = 41.001
lon = 28.9431

df_Agro_p = extract_ts(file, shp, var[0], type='point', lon=lon, lat=lat)
df_Era5_p = extract_ts(file1, shp, var[1], type='point', lon=lon, lat=lat)

Cakit = pd.read_csv('../Data/Measurements/Cakit.csv', index_col='Date')
Cakit = pd.read_csv('../Data/Measurements/18567_Data.csv', index_col='Date')
Cakit = pd.read_csv('../Data/Measurements/Aksaray.csv', index_col='Date')

temp = pd.merge(Cakit, df_Agro_p, left_index=True, right_index=True)
df3 = pd.merge(temp, df_Era5_p, left_index=True, right_index=True)

df3.index.name = 'Date'
df3.to_csv('test_temp.csv')
df3.plot(y=['Aksaray', 'Agro_Temperature_Air_2m_Mean_24h', 'Era5_t2m'])
plt.show()
# plt.figure(figsize=(12, 8))
# ax = plt.axes()
# out_sel.tp.isel(time=0).plot(ax=ax)
# nuts.plot(ax=ax, alpha=0.8, facecolor='none')
# plt.show()
