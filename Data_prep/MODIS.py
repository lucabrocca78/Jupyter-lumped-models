import os, glob

folder = '/home/cak/Desktop/tmp'
folder = '/media/D/Datasets/Snow/MODIS'
os.chdir(folder)

files = glob.glob('*.tif')
f_list = []
for file in files:
    year = file[9:13]
    day = file[13:16]
    f_list.append(year + '-' + day)
myset = set(f_list)
print(myset)

unique = list(myset)
ff = list(range(1, 7))

for uni in unique:
    files = glob.glob('*.A' + uni[0:4] + uni[5:8] + '*' + '.tif')

    for i, file in enumerate(files):
        code = """gdalwarp -srcnodata 0 -dstnodata 0 -crop_to_cutline -cutline TR.shp {} clipped_{}""".format(file,
                                                                                                              file)
        os.system(code)
        code = """gdal_calc.py -A clipped_{} --outfile=edited_{}.tif --calc="0*(A>252)+A*(A<252)" """.format(
            file,
            ff[i])
        os.system(code)

    edited_files = glob.glob('edited*.tif')
    code = """gdal_calc.py -A edited_1.tif -B edited_2.tif -C edited_3.tif -D edited_4.tif -E edited_5.tif -F edited_6.tif --outfile={}.tif --calc="A+B+C+E+F" """.format(
        uni)
    os.system(code)
