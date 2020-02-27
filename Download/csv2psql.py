import os, glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.types import String
import datetime
import pathlib

path = pathlib.Path().absolute()
os.chdir(os.path.join(path, 'Downloaded_data'))

variable = ['2m_temperature', 'potential_evaporation', 'total_precipitation', 'snow_cover']
tables = ['temperature','pot','pre''snow']
var = variable[0]
files = glob.glob('*'+ var + '*_final.csv')


for i,f in enumerate(files):
    print("Process starterd at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))
    table = tables[i]
    columns = ['var', 'date', 'lat', 'lon', table]
    df = pd.read_csv(f, skiprows=1, names=columns)
    df.loc[df[table] == -32767.000, [table]] = np.nan

    engine = create_engine('postgresql://postgres:kalmanQs++@localhost:5999/postgres')

    result = engine.execute('SELECT lat,lon,index FROM '
                            '"cindex"')
    res = result.fetchall()
    col = ['lat', 'lon', 'index']
    df_l = pd.DataFrame(res, columns=col)

    new_df = pd.merge(df, df_l, how='left', left_on=['lat', 'lon'], right_on=['lat', 'lon'])
    new_df.drop(['var', 'lat', 'lon'], axis=1, inplace=True)
    new_df.to_sql(table, engine, if_exists='append', index=False,
                  dtype={"date": String(), table: String(), "index": String()})
    print("Process ended at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))
