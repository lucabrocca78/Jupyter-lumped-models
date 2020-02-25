import os, glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.types import String
import datetime


os.chdir('/media/cak/D/Datasets/ERA5_Land/Houtly2Daily/Temp')

files = glob.glob('*_final.csv')



for f in files:
    print("Process starterd at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))
    columns = ['var', 'date', 'lat', 'lon', 'temp']
    df = pd.read_csv(f, skiprows=1, names=columns)
    df.loc[df['temp'] == -32767.000, ['temp']] = np.nan

    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    result = engine.execute('SELECT lat,lon,index FROM '
                            '"cindex"')
    res = result.fetchall()
    col = ['lat', 'lon', 'index']
    df_l = pd.DataFrame(res, columns=col)

    new_df = pd.merge(df, df_l, how='left', left_on=['lat', 'lon'], right_on=['lat', 'lon'])
    new_df.drop(['var', 'lat', 'lon'], axis=1, inplace=True)
    new_df.to_sql('daily', engine, if_exists='append', index=False,
                  dtype={"date": String(), "temp": String(), "index": String()})
    print("Process ended at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))
