import os, glob
import subprocess

folder = '/media/D/Datasets/TRMM'
folder = '/home/cak/Desktop/Datasets/GPM'

files = glob.glob1(folder, '*.nc')

os.chdir(folder)

# for file in files:
#     name = file[0:8]
#     # udo cdo settaxis,2020-01-01,12:00:00,1day 3B42RT_Daily.20191231.7.nc4 set.nc
#
#     date = name[0:4] + '-' + name[4:6] + '-' + name[6:8]
#
#     code = 'cdo settaxis,{},12:00:00,1day {file} time_{file}'.format(date, file=file)
#     os.system(code)
#
years = list(range(2000,2020))
folder = '/home/cak/Desktop/Datasets/TRMM_RT/time'
files = glob.glob1(folder, '*.nc')
os.chdir(folder)

for year in years:
    code = 'cdo mergetime time_{year}* {year}.nc'.format(year=year)
    os.system(code)
    print(str(year) + ' done')





