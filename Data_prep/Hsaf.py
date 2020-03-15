import gdal
from osgeo import osr
from osgeo import ogr

raster_path = '/home/cak/Desktop/H05B/h05B_data/out1.tiff'
shapefile = '/home/cak/Desktop/H05B/shp/grid.shp'


# 1) opening the shapefile    

source_ds = ogr.Open(shapefile)
source_layer = source_ds.GetLayer()


# 2) Creating the destination raster data source

pixelWidth = pixelHeight = 3 # depending how fine you want your raster ##COMMENT 1
x_min, x_max, y_min, y_max = source_layer.GetExtent()
cols = int((x_max - x_min) / pixelHeight)
rows = int((y_max - y_min) / pixelWidth)

target_ds = gdal.GetDriverByName('GTiff').Create(raster_path, cols, rows, 1, 
gdal.GDT_Float32) ##COMMENT 2

target_ds.SetGeoTransform((x_min, pixelWidth, 0, y_max, 0, -pixelHeight)) ##COMMENT 3

# 5) Adding a spatial reference ##COMMENT 4
target_dsSRS = osr.SpatialReference()
target_dsSRS.ImportFromEPSG(4326)
target_ds.SetProjection(target_dsSRS.ExportToWkt())

band = target_ds.GetRasterBand(1) 
band.SetNoDataValue(-9999) ##COMMENT 5

gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE = value"]) ##COMMENT 6

target_ds = None ##COMMENT 7