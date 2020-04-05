#!/bin/bash
export WORKDIR=/mnt/e/Datasets/ARPEGE
cd ${WORKDIR}

./mnt/c/Users/cagri/Desktop/Jupyter-lumped-models/Forecasts/get_ARPEGE.py

currentdate=$(date +"%Y-%m-%d")

for file in *.grib2; do wgrib2 $file -netcdf ${file%%.*}.nc; done
for file in *.nc; do cdo selvar,TMP_2maboveground $file temp_${file}; done
cdo mergetime temp*.nc temp.nc,
cdo subc,273.15 temp.nc ARPEGE_${currentdate}_temp.nc
rm *.grib2
rm W_fr*

