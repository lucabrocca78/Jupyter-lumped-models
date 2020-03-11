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

var = 'pre'

file = '/home/cak/Desktop/Sentinel/test/SD_20190101.nc'
file = '/media/D/Datasets/PERSIANN_CCS/Data/CCS_Turkey_2020-03-07122131pm_2018.nc'

file = '/media/D/Datasets/ERA5_Land/Temp/Temp_daily.nc'
file = '/media/D/Datasets/ERA5_Land/pre/pre_daily.nc'
file = '/media/D/Datasets/GPM/pre_daily_tr.nc'
file = '/media/D/Datasets/GPM/2015_2019_daily.nc'
shp = '/home/cak/Desktop/Jupyter-lumped-models/Data/shp/Basins.shp'
# shp = '/home/cak/Desktop/NUTS/NUTS_RG_10M_2016_4326_LEVL_0.shp'

nuts = gpd.read_file(shp)
num = len(nuts)

d = xr.open_dataset(file)

nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.ID),
                                    abbrevs=list(nuts.ID),
                                    outlines=list(nuts.geometry.values[i] for i in range(0, num)))

# nuts_mask_poly = regionmask.Regions_cls(name = 'nuts_mask', numbers = list(range(0,37)), names = list(nuts.NUTS_ID), abbrevs = list(nuts.NUTS_ID), outlines = list(nuts.geometry.values[i] for i in range(0,37)))
print(nuts_mask_poly)

mask = nuts_mask_poly.mask(d.isel(time=0).sel(lat=slice(35, 43), lon=slice(25, 45)), lat_name='lat',
                           lon_name='lon')

# proj = ccrs.EqualEarth(central_longitude=0)
# ax = plt.subplot(111, projection=proj)
# if var == 'pre':
#     d.isel(time=0).HQprecipitation.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree())
# else:
#     d.isel(time=1).t2m.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree())
# ax.coastlines()
# plt.show()
#
# plt.figure(figsize=(12, 8))
# ax = plt.axes()
# mask.plot(ax=ax)
# nuts.plot(ax=ax, alpha=0.8, facecolor='none', lw=1)
# plt.show()

lat = mask.lat.values
lon = mask.lon.values

ID_REGION = 1
# print(nuts.NUTS_ID[ID_REGION])
print(nuts.ID[ID_REGION])

sel_mask = mask.where(mask == ID_REGION).values

id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

out_sel = d.sel(lat=slice(id_lat[0], id_lat[-1]), lon=slice(id_lon[0], id_lon[-1])).compute().where(
    mask == ID_REGION)

daily = out_sel.mean(dim=('lat', 'lon'))

if var == 'pre':
    df = daily.precipitationCal.to_dataframe()
    daily.precipitationCal.plot()
else:
    df = daily.t2m.to_dataframe()
    df['t2m'] = df['t2m'] - 273
    daily.tp.plot()
plt.show()

Cakit = pd.read_csv('../Data/Measurements/Cakit.csv', index_col='Date')
df.index = df.index.strftime('%m/%d/%Y')

df3 = pd.merge(Cakit, df, left_index=True, right_index=True)
df3.index.name = 'Date'

if var == 'pre':
    df3.plot.bar(y=['P', 'precipitationCal'])
    df3.plot(y=['P', 'precipitationCal'])
else:
    df3.plot(y=['Temp', 't2m'])
plt.show()
plt.figure(figsize=(12, 8))
ax = plt.axes()
out_sel.precipitationCal.isel(time=0).plot(ax=ax)
nuts.plot(ax=ax, alpha=0.8, facecolor='none')
plt.show()
