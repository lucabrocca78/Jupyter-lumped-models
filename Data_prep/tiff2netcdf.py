import os, glob

folder = '/home/cak/Desktop/Datasets/SM2RAIN/10km'

os.chdir(folder)

files = glob.glob('*.tif')

for file in files:
    name = file.split('.tif')[0][15:25]
    date = name
    infile = file
    outfile = name + '.nc'

    os.system("""gdal_translate -of netCDF -co "FORMAT=NC4" {} {}""".format(infile, outfile))
    os.system("""ncrename -v Band1,{} {}""".format('tp', outfile))
    os.system("""ncatted -O -a long_name,{},o,c,sm2rain {}""".format('tp', outfile))
    os.system("""cdo settaxis,{},12:00:00,1day {} {}""".format(date, outfile, 't_' + outfile))
    os.remove(outfile)
    print(date)

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
years = list(range(2007, 2020))
#
for year in years:
    files = glob.glob('t_' + str(year) + '*.nc')

    code = """cdo mergetime t_{year}*.nc {year}.nc""".format(year=str(year))
    os.system(code)
    print(str(year) + ' done')
