import os, glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.types import String
import datetime
import pathlib
import yaml

path = pathlib.Path().absolute()

# 'CAK', 'HSAF', 'WR'
PC = 'HSAF'
# PC = 'CAK'

with open(r'server.yaml') as file:
    server_list = yaml.load(file, Loader=yaml.FullLoader)

server = server_list['server']
username = server_list['user']
password = server_list['password']

if PC == 'HSAF':
    server = 'localhost'
else:
    server = server

print('Server started at {} '.format(server))

os.chdir(os.path.join(path, 'Downloaded_data','pot','CSV'))

variable = ['2m_temperature', 'potential_evaporation', 'total_precipitation', 'snow_cover']
tables = ['temperature', 'pot', 'pre', 'snow']

variable = ['potential_evaporation']
tables = ['pot']


for count, var in enumerate(variable):
    print('Variable : {}'.format(var))
    files = glob.glob('*.csv')
    table = tables[count]
    for i, f in enumerate(files):
        print("Process starterd at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))

        columns = ['var', 'date', 'lon', 'lat', table]
        df = pd.read_csv(f, skiprows=1, names=columns)
        df.loc[df[table] == -32767.000, [table]] = np.nan

        engine = create_engine('postgresql://' + username + ':' + password + '@' + server + ':5999/postgres')

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
