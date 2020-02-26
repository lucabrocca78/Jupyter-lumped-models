import cdsapi
import os
from cdo import *


os.chdir('/home/cak/Desktop/jupyter/Notebook/utils')

# c = cdsapi.Client()
#
# c.retrieve(
# 'reanalysis-era5-single-levels',
# {
#     'variable': [
#                     '2m_temperature',
#                 ],
#     'product_type':'reanalysis',
#     'year':'2019',
#     'month':'04',
#     'day': [
#                     '01', '02', '03',
#                     '04', '05', '06',
#                 ],
#     'area':'25/35/45/43',
#     'time':[
#         '00:00','01:00','02:00',
#         '03:00','04:00','05:00',
#         '06:00','07:00','08:00',
#         '09:00','10:00','11:00',
#         '12:00','13:00','14:00',
#         '15:00','16:00','17:00',
#         '18:00','19:00','20:00',
#         '21:00','22:00','23:00'
#     ],
#     'format':'netcdf'
# },
# 'precip.nc')
#
# with open('pre.csv', 'r') as f_in, open('t2m_20000801.csv', 'w') as f_out:
#     f_out.write(next(f_in))
#     [f_out.write(','.join(line.split()) + '\n') for line in f_in]
#

cdo = Cdo()
cdo.infov(input='precip.nc')