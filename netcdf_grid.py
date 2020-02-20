import xarray as xr
import numpy as np
import regionmask
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

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

    nuts_mask_poly = regionmask.Regions(name='nuts_mask', numbers=list(range(0, num)), names=list(nuts.ID),
                                        abbrevs=list(nuts.ID),
                                        outlines=list(nuts.geometry.values[i] for i in range(0, num)))

    if resample:
        new_lon = np.linspace(d.longitude[0], d.longitude[-1], d.dims['longitude'] * factor)
        new_lat = np.linspace(d.latitude[0], d.latitude[-1], d.dims['latitude'] * factor)
        d = d.interp(latitude=new_lat, longitude=new_lon)

    # print(nuts_mask_poly)
    # mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(75, 32), longitude=slice(-30, 50)), lat_name='latitude',
    #                            lon_name='longitude')

    mask = nuts_mask_poly.mask(d.isel(time=0).sel(latitude=slice(75, 32), longitude=slice(-30, 50)),
                               lat_name='latitude',
                               lon_name='longitude')

    # plt.figure(figsize=(12, 8))
    # ax = plt.axes()
    # mask.plot(ax=ax)
    # nuts.plot(ax=ax, alpha=0.8, facecolor='none', lw=1)
    # plt.show()
    lat = mask.latitude.values
    lon = mask.longitude.values

    # print(mask)
    data = {}

    for i in range(num):
        ID_REGION = i
        # print(nuts.ID[ID_REGION])
        Zone = 'Zone ' + nuts.ID[ID_REGION]
        sel_mask = mask.where(mask == ID_REGION).values

        id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
        id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

        out_sel = d.sel(latitude=slice(id_lat[0], id_lat[-1]), longitude=slice(id_lon[0], id_lon[-1])).compute().where(
            mask == ID_REGION)

        # plt.figure(figsize=(12, 8))
        # ax = plt.axes()
        # out_sel.t2m.isel(time=0).plot(ax=ax)
        # nuts.plot(ax=ax, alpha=0.8, facecolor='none')
        # plt.show()

        x = out_sel.groupby('time.day').mean(dim=('latitude', 'longitude'))
        data.update({Zone: x.t2m.values})
        # x.t2m.plot()
        # plt.show()

    time = pd.to_datetime(x.day.time.values)
    df = pd.DataFrame(data).set_index(time)
    df_h = df.resample('D').mean().subtract(273)
    df_h.plot()
    plt.show()

grid2ts(file,shp)