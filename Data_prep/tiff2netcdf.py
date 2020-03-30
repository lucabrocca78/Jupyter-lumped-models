import os, glob

folder = '/home/cak/Desktop/Datasets/SM2RAIN/10km'
folder = '/mnt/e/Test/T_2m'

os.chdir(folder)

files = glob.glob('*.grib2')

# for file in files:
#     name = file.split('.tif')[0][15:25]
#     date = name
#     infile = file
#     outfile = name + '.nc'
#
#     os.system("""gdal_translate -of netCDF -co "FORMAT=NC4" {} {}""".format(infile, outfile))
#     os.system("""ncrename -v Band1,{} {}""".format('tp', outfile))
#     os.system("""ncatted -O -a long_name,{},o,c,sm2rain {}""".format('tp', outfile))
#     os.system("""cdo settaxis,{},12:00:00,1day {} {}""".format(date, outfile, 't_' + outfile))
#     os.remove(outfile)
#     print(date)

# os.system("""cdo mergetime t*.nc {}.nc""".format(channel))
# os.system("""mv {}.nc ./done""".format(channel))
# os.system("""rm *.nc""")
# print(channel + ' done')

# df.index = df.index.astype(int)
# df.index = pd.to_datetime(df.index,format = '%Y%m%d')
# df[['36gv','36gh']].plot()
# plt.show()

# folder = '/home/cak/Desktop/H13_ALL/h13_swe/projected'
# folder = '/home/cak/Desktop/H10_ALL'
# os.chdir(folder)
#
# years = list(range(2009, 2021))
import datetime


files = glob.glob('*.grib2')
# _2020032909_000_1_T.grib2
for file in files:

    year =  int(file[43:47])
    mount = int(file[47:49])
    day = int(file[49:51])
    run_time = int(file[51:53])
    time_delta = int(file.split('_')[-2])
    day = datetime.datetime(year, mount, day, run_time, 0, 0)
    time = day + datetime.timedelta(hours=int(time_delta))
    day = time.strftime('%Y-%m-%d')
    hour = time.strftime('%H:%M:%S')
    nc_out = file.split('.grib2')[0] + '.nc'
    code = """grib_to_netcdf -o {} {}""".format(nc_out, file)
    os.system(code)
    outfile = str(time_delta) + '_.nc'

    code = """cdo shifttime,{}hour {} {}""".format(time_delta, nc_out, outfile)
    os.system(code)

#
# for year in years:
#     files = glob.glob('t_' + str(year) + '*.nc')
#
#     code = """cdo mergetime t_{year}*.nc {year}.nc""".format(year=str(year))
#     os.system(code)
#     print(str(year) + ' done')
