;-- copy shapefile_utils.ncl from 
;-- https://www.ncl.ucar.edu/Applications/Scripts/shapefile_utils.ncl
load "/mnt/e/Datasets/GFS/shapefile_utils.ncl" 

shpname  = "./TR/Turkey.shp" 
maskname = "./TR/TR_mask_era.nc" 

print_shapefile_info(shpname)

;-- open data file to get the grid to be used
f = addfile("Era5_land_temp.nc","r")

;-- read variable
var                    =  f->temp(0,:,:)
var@lat2d              =  f->lat
var@lon2d              =  f->lon

;-- shapefile mask resources
opt             =  True
opt@return_mask =  True    ;-- this forces the return of a 0s and 1s mask array

;-- create the mask based on the given shapefile
mask_array             =  shapefile_mask_data(var, shpname, opt)
mask_array!0           = "y" 
mask_array!1           = "x" 
mask_array@coordinates = "lat lon" 

;-- create new netCDF file and write mask array
system("rm -f " + maskname)
fout = addfile(maskname,"c")

fout->mask_array =  mask_array
fout->lat       =  f->lat
fout->lon      =  f->lon