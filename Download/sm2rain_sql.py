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

os.chdir(os.path.join(path, 'SM2RAIN'))

variable = ['pre']
tables = ['sm2rain']

for count, var in enumerate(variable):
    print('Variable : {}'.format(var))
    files = glob.glob('*.csv')
    table = tables[count]
    for i, f in enumerate(files):
        print("Process starterd at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))

        columns = ['var', 'index', 'date', 'value']
        df = pd.read_csv(f, skiprows=1, names=columns)
        df.loc[df['value'] == -2147483647, ['value']] = np.nan

        engine = create_engine('postgresql://' + username + ':' + password + '@' + server + ':5999/postgres')

        df.drop(['var'], axis=1, inplace=True)
        df.to_sql(table, engine, if_exists='append', index=False,
                  dtype={"index": String(), "date": String(), "pre": String()})
        print("Process ended at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), f))
