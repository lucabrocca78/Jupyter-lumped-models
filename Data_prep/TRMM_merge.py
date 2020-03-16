import os, glob
import subprocess

folder = '/media/D/Datasets/TRMM'
folder = '/home/cak/Desktop/Datasets/TRMM'

files = glob.glob1(folder, '*.nc4')

os.chdir(folder)




for file in files:
    name = file[0:8]
    # udo cdo settaxis,2020-01-01,12:00:00,1day 3B42RT_Daily.20191231.7.nc4 set.nc

    date = name[0:4] + '-' + name[4:6] + '-' + name[6:8]

    code = 'cdo settaxis,{},12:00:00,1day {file} time_{file}'.format(date, file=file)
    os.system(code)
