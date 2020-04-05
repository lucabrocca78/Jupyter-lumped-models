#!/bin/bash
export WORKDIR=/mnt/e/Datasets/ARPEGE
cd ${WORKDIR}

./mnt/c/Users/cagri/Desktop/Jupyter-lumped-models/Forecasts/get_ARPEGE.py

currentdate=$(date +"%Y-%m-%d")

for file in *.grib2; do wgrib2 $file -netcdf ${file%%.*}.nc; done
cdo mergetime *.nc ARPEGE_${currentdate}.nc
cdo selvar,TMP_2maboveground ARPEGE_${currentdate}.nc ARPEGE_${currentdate}_temp_K.nc
cdo subc,273.15 ARPEGE_${currentdate}_temp_K.nc ARPEGE_${currentdate}_temp_C.nc

cdo shaded,device="png",min=-5,max=25,lat_min=35,lat_max=45,lon_min=25,lon_max=45,step_freq=1 -selvar,TMP_2maboveground ARPEGE_${currentdate}_temp_C.nc SC.png
convert -delay 40 'SC.png_TMP_2maboveground.%d.png[0-120]' ARPEGE_${currentdate}_temp.gif


rm *.grib2
rm W_fr*
rm t

