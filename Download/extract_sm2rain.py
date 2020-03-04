from osgeo import gdal, ogr
import os, glob
import pathlib
import pandas as pd

tif_folder = '/media/cak/D/Datasets/SM2RAIN/SM2RAIN_Data'
os.chdir(tif_folder)
files = glob.glob('*.tif')
# shp_filename = ('/home/cak')
shp_filename = '/home/cak/Desktop/Jupyter-lumped-models/Grid/Grid_point.shp'
li_values = list()
n = len(files)
i = 1
j = 1
for file in files:
    name = file.split('.tif')[0][15:25]
    # name = name[0:4] + '-' + name[4:6] + '-' + name[6:8]
    src_ds = gdal.Open(files[0])
    gt = src_ds.GetGeoTransform()
    rb = src_ds.GetRasterBand(1)

    ds = ogr.Open(shp_filename)
    lyr = ds.GetLayer()

    data = pd.DataFrame(columns=['index', 'Date', 'value'])
    for feat in lyr:
        geom = feat.GetGeometryRef()
        feat_id = feat.GetField('index')
        mx, my = geom.GetX(), geom.GetY()

        px = int((mx - gt[0]) / gt[1])
        py = int((my - gt[3]) / gt[5])

        intval = rb.ReadAsArray(px, py, 1, 1)
        li_values.append([feat_id, name, intval[0][0]])
        # data = data.append({'index': feat_id, 'Date': name, 'value': intval[0][0]}, ignore_index=True)
    print('Date {} compleated {} / {} '.format(name, i, n))
    if i % 1000 == 0:
        data = pd.DataFrame(li_values, columns=['index', 'date', 'value'])
        data.to_csv(str(j) +  '_hsaf.csv')
        li_values = []
        j += 1
    i += 1
data = pd.DataFrame(li_values, columns=['index', 'date', 'value'])
data.to_csv('hsaf.csv')
import csv
