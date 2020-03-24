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

folder = '/mnt/e/Datasets/Precipitation/att_fixed'
os.chdir(folder)
files = glob.glob('*.nc')


# for file in files:


def extract_ts(file, shp, var, type='area', lat=34, lon=34):
    d = xr.open_dataset(file)
    name = file.split('_')[0]

    # if name in ['TRMM']:
    #     d = d.transpose('time','latitude', 'longitude')

    print(name)
    if type == 'area':
        nuts = gpd.read_file(shp)
        num = len(nuts)
        nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.ID),
                                            abbrevs=list(nuts.ID),
                                            outlines=list(nuts.geometry.values[i] for i in range(0, num)))
        print(nuts_mask_poly)

        if name not in ['sm2rain', 'GPM', 'TRMM', 'TRMMRT', 'Chirps']:
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(43, 35), longitude=slice(25, 45)),
                                       lat_name='latitude',
                                       lon_name='longitude')
        else:
            mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(35, 43), longitude=slice(25, 45)),
                                       lat_name='latitude',
                                       lon_name='longitude')

        lat = mask.latitude.values
        lon = mask.longitude.values

        proj = ccrs.EqualEarth(central_longitude=0)
        ax = plt.subplot(111, projection=proj)
        d.isel(time=0).tp.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree())
        ax.coastlines()
        plt.show()

        ID_REGION = 1
        # print(nuts.NUTS_ID[ID_REGION])
        print(nuts.ID[ID_REGION])

        sel_mask = mask.where(mask == ID_REGION).values

        id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
        id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

        try:
            out_sel = d.sel(latitude=slice(id_lat[0], id_lat[-1]),
                            longitude=slice(id_lon[0], id_lon[-1])).compute().where(
                mask == ID_REGION)
            daily = out_sel.mean(dim=('latitude', 'longitude'), skipna=True)
        except:
            daily = d.mean(dim=('latitude', 'longitude'), skipna=True)
            daily['tp'] = 0
    else:
        daily = d.sel(longitude=lon, latitude=lat, method='nearest')

    for key in daily.keys():
        daily = daily.rename({key: name + '_' + key})
    df = daily.to_dataframe()
    if name == 'Era5':
        df['Era5_tp'] = df['Era5_tp'] * 1e3

    if name == 'PERSIANN':
        df = df.drop(['PERSIANN_crs'], axis=1)
        df.loc[(df.PERSIANN_tp < 0), 'PERSIANN_tp'] = 0

    if name in ['sm2rain', 'TRMM', 'TRMMRT']:
        df.index = df.index.astype(int)
        df.index = pd.to_datetime(df.index.astype(str))
    df.index = df.index.strftime('%m/%d/%Y')

    return df


variables = locals()
for file in files:
    name = file.split('_')[0]
    variables["df_{0}".format(name)] = extract_ts(file, shp, var, type='area')

df = pd.concat([df_TRMMRT, df_TRMM, df_sm2rain, df_Era5, df_GPM, df_PERSIANN, df_Chirps], axis=1)
df.plot()
plt.show()
print("a")
