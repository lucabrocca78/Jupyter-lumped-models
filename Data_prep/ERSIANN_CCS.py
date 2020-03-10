import numpy as np
import os, glob
import pandas as pd
import xarray as xr

path = '/media/D/Datasets/PERSIANN_CCS'
file = '/media/D/Datasets/PERSIANN_CCS/CCS_Turkey_2020-03-07083347am_2015.nc'

lat = [line.rstrip('\n') for line in open(os.path.join(path, 'grid', 'lat.csv'))]
lon = [line.rstrip('\n') for line in open(os.path.join(path, 'grid', 'lon.csv'))]

grid = []

i = 1
for lat_ in lat:
    for lon_ in lon:
        grid.append([lat_, lon_, i])
        i += 1
files = glob.glob1(os.path.join(path,'Data'), '*.nc')

for file in files:
    print(file)
    name = file[-7:][:4]
    d = xr.open_dataset(os.path.join(path,'Data', file))
    d.precip.to_dataframe().to_csv(os.path.join(path, 'CSV', '{}.csv'.format(name)))

    columns = ['date', 'lat', 'lon', 'pre']
    df = pd.read_csv(os.path.join(path, 'CSV', '{}.csv'.format(name)), skiprows=1, names=columns)
    df.loc[df['pre'] == -99, ['pre']] = np.nan

    df_l = pd.DataFrame(grid, columns=['lat', 'lon', 'index'])
    df_l['lat'] = df['lat'].astype(float)
    df_l['lon'] = df['lon'].astype(float)

    new_df = pd.merge(df, df_l, how='left', left_on=['lat', 'lon'], right_on=['lat', 'lon'])
    new_df.drop(['lat', 'lon'], axis=1, inplace=True)

    number_of_chunks = 20
    [new_df.to_csv(os.path.join(path, 'CSV', '{name}_{id}.csv'.format(name=name, id=id)), index=False) for id, new_df in
     enumerate(np.array_split(new_df, number_of_chunks))]
    os.remove(os.path.join(path, 'CSV', '{}.csv'.format(name)))
