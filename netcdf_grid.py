import xarray as xr
import numpy as np
import regionmask
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

file = '/media/cak/AT/Datasets/EOBS/temp2.nc'
# file = '/media/cak/AT/Datasets/SM2RAIN/SM2RAIN_ASCAT_0125_2016_v1.1.nc'
shp = '/home/cak/Desktop/SHP/Karasu_all.shp'
shp = '/home/cak/Desktop/at/NUTS_RG_60M_2016_4326_LEVL_0.shp'
num = 37

nuts = gpd.read_file(shp)
nuts.head()
d = xr.open_mfdataset(file, chunks={'time': 10})
d = d.assign_coords(longitude=(((d.longitude + 180) % 360) - 180)).sortby('longitude')

nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.NUTS_ID),
                                        abbrevs=list(nuts.NUTS_ID),
                                        outlines=list(nuts.geometry.values[i] for i in range(0, num)))

print(nuts_mask_poly)
mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(75, 32), longitude=slice(-30, 50)), lat_name='latitude',
                           lon_name='longitude')

#
plt.figure(figsize=(12,8))
ax = plt.axes()
mask.plot(ax = ax)
nuts.plot(ax = ax, alpha = 0.8, facecolor = 'none', lw = 1)
plt.show()
lat = mask.latitude.values
lon = mask.longitude.values


print(mask)

ID_REGION = 35
print(nuts.NUTS_ID[ID_REGION])

sel_mask = mask.where(mask == ID_REGION).values

id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

out_sel = d.sel(latitude = slice(id_lat[0], id_lat[-1]), longitude = slice(id_lon[0], id_lon[-1])).compute().where(mask == ID_REGION)

plt.figure(figsize=(12,8))
ax = plt.axes()
out_sel.t2m.isel(time = 0).plot(ax = ax)
nuts.plot(ax = ax, alpha = 0.8, facecolor = 'none')
plt.show()

x = out_sel.groupby('time.day').reduce(np.mean).mean()(scheduler='sync')

x.t2m.plot()
plt.show()



# time = pd.date_range('2000-01-01', freq='1D', periods=365)
# ds = xr.open_dataset(file)
# # dsloc = ds.sel(longitude=37, latitude=37.0, time=time,method='nearest')
# dsloc = ds.sel(longitude=[37, 39], latitude=[37.0, 40], time=time, method='nearest')
# # dsloc['tn'].mean(dim='time')
# dsloc['tg'].plot();
# plt.show()
