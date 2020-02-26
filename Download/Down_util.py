import cdsapi
import os
from cdo import *
import subprocess
import psycopg2
import pandas as pd
import numpy as np
import datetime

os.chdir('/home/cak/Desktop/Data')

c = cdsapi.Client()


# cdo = Cdo()


def retrieve(var, year, month, day, area):
    out_file = str(year) + '_' + var + '.nc'
    c.retrieve(
        'reanalysis-era5-land',
        {
            'variable': var,
            'year': year,
            'month': month,
            'day': day,
            'area': area,
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00'
            ],
            'format': 'netcdf'
        },
        out_file)
    return out_file


def get_daily_mean(in_file, out_file):
    # Mean Temp
    # daily_mean = 'cdo daymean -shifttime,-1hour {} {}'.format(in_file, out_file)
    # Total Preciptation
    daily_mean = 'cdo -b 32 daymean -shifttime,-1hour {} {}'.format(in_file, out_file)
    p = subprocess.Popen([daily_mean], shell=True)
    p.communicate()


def val2csv(in_file, out_file):
    write_csv = 'cdo outputtab,name,date,lon,lat,value {} > {}'.format(in_file, out_file)
    p = subprocess.Popen([write_csv], shell=True)
    p.communicate()


def edit_csv(in_file, out_file):
    with open(in_file, 'r') as f_in, open(out_file, 'w') as f_out:
        f_out.write(next(f_in))
        [f_out.write(','.join(line.split()) + '\n') for line in f_in]


def data2database():
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="localhost",
                                      port="5432",
                                      database="postgres")

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == '__main__':
    day = list(range(1, 31))
    month = list(range(1, 13))
    # day = list(range(1, 2))
    # month = list(range(1, 2))
    years = list(range(2010, 2020))
    for year in years:
        # year = 2019
        variable = ['2m_temperature', 'potential_evaporation', 'total_precipitation', 'snow_cover']
        # area = '25/35/45/43'
        area = '43/25/35/45'  # N/W/S/E Specify as North/West/South/East in Geographic lat/long degrees. Southern latitudes and Western longitudes must be given as negative numbers.
        # var = variable[3]
        for var in variable:
            in_file = retrieve(var, year, month, day, area)
            daily_mean = str(year) + '_' + var + '_daily.nc'
            get_daily_mean(in_file, daily_mean)
            raw_csv = str(year) + '_' + var + '_daily.csv'
            val2csv(daily_mean, raw_csv)
            edited_csv = str(year) + '_' + var + '_daily_final.csv'
            edit_csv(raw_csv, edited_csv)
        # data2database()

        # print("Process starterd at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), year))
        #
        # columns = ['var', 'date', 'lat', 'lon', 'pre']
        # df = pd.read_csv(edited_csv, skiprows=1, names=columns)
        # df.loc[df['pre'] == -32767.000, ['pre']] = np.nan
        #
        # from sqlalchemy import create_engine
        # from sqlalchemy.sql import select
        #
        # engine = create_engine('postgresql://postgres:kalmanQs++@185.67.125.34:5999/postgres')
        # from sqlalchemy.types import String
        #
        # result = engine.execute('SELECT lat,lon,index FROM '
        #                         '"cindex"')
        # res = result.fetchall()
        # col = ['lat', 'lon', 'index']
        # df_l = pd.DataFrame(res, columns=col)
        #
        # new_df = pd.merge(df, df_l, how='left', left_on=['lat', 'lon'], right_on=['lat', 'lon'])
        # new_df.drop(['var', 'lat', 'lon'], axis=1, inplace=True)
        # new_df.to_sql('pre', engine, if_exists='append', index=False,
        #           dtype={"date": String(), "pre": String(),"index":String()})
        # print("Process ended at {} for year : {}".format(datetime.datetime.now().strftime('%H:%M:%S'), year))
