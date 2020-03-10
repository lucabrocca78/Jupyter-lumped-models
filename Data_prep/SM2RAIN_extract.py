import netCDF4
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import xarray as xr
import pandas as pd

nc_f = '/media/D/Datasets/SM2RAIN/Data/SM2RAIN_ASCAT_0125_2019_v1.2.nc'
lat_lon = '/home/cak/Desktop/HSAF/SHP/polygon_grid_lat_lon.csv'
grid = pd.read_csv(lat_lon)
nc_fid = netCDF4.Dataset(nc_f, 'r')
lat_ = nc_fid.variables['Latitude'][:]
lon_ = nc_fid.variables['Longitude'][:]
tree = spatial.KDTree(list(zip(lon_.ravel(), lat_.ravel())))
os.chdir('/media/D/Datasets/SM2RAIN/Data')

datahub = []
DD = np.arange(datetime(2016, 1, 1), datetime(2019, 1, 1), timedelta(days=1)).astype(datetime)

data = pd.DataFrame(columns=['date', 'val', 'lat', 'lon'])

for ii in np.arange(2016, 2019):
    nc_f = 'SM2RAIN_ASCAT_0125_' + str(ii) + '_v1.1.nc'
    nc_fid = netCDF4.Dataset(nc_f, 'r')
    date = np.arange(datetime(ii, 1, 1), datetime(ii + 1, 1, 1), timedelta(days=1)).astype(datetime)
    print(nc_f)
    for index, row in grid.iterrows():
        print(index)
        stat = [row[0], row[1]]
        [d, ID] = tree.query(stat)

        Rain = nc_fid.variables['Rainfall'][ID]
        # np.concatenate does not preserve masking of MaskedArray inputs, here np.ma.concatenate is used
        # datahub = np.ma.concatenate((datahub, Rain), axis=0)
        lat = np.full((len(date)), row[0])
        lon = np.full((len(date)), row[1])
        d = {'date': date, 'val': Rain.data, 'lat': lat, 'lon': lon}
        temp = pd.DataFrame(d)
        data = data.append(temp)

DD = np.arange(datetime(2016, 1, 1), datetime(2019, 1, 1), timedelta(days=1)).astype(datetime)
plt.plot(DD, datahub)
plt.ylabel('rainfall [mm/day]')
plt.title('SM2RAIN-ASCAT lon;lat=' + str(stat[0]) + ';' + str(stat[1]))
plt.show()
