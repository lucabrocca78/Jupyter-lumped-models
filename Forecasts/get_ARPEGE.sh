#!/bin/bash
export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts
cd ${WORKDIR}

python3 get_ARPEGE.py

export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/ARPEGE
cd ${WORKDIR}

currentdate=$(date +"%Y-%m-%d")

for file in *.grib2; do /home/cak/Desktop/software/grib2/wgrib2/wgrib2 $file -netcdf ${file%%.*}.nc; done
cdo mergetime *.nc ARPEGE_${currentdate}.nc
cdo selvar,TMP_2maboveground ARPEGE_${currentdate}.nc ARPEGE_${currentdate}_temp_K.nc
cdo subc,273.15 ARPEGE_${currentdate}_temp_K.nc ARPEGE_${currentdate}_temp_C.nc

cdo shaded,device="png",min=-5,max=25,lat_min=35,lat_max=45,lon_min=25,lon_max=45,step_freq=1 -selvar,TMP_2maboveground ARPEGE_${currentdate}_temp_C.nc SC.png
convert -delay 40 'SC.png_TMP_2maboveground.%d.png[0-115]' ARPEGE_${currentdate}_temp.gif
mv ARPEGE_${currentdate}_temp_K.nc ARPEGE_${currentdate}_temp_C.nc ARPEGE_${currentdate}.nc ./Data
mv ARPEGE_${currentdate}_temp.gif ./GIF

rm *.grib2
rm *.nc
rm *.png
cd ./Data
tar -czvf ARPEGE_${currentdate}.tar.gz ARPEGE_${currentdate}.nc
#rm t

