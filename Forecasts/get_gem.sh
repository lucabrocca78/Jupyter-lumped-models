#!/bin/bash
# set the base URL in two parts: URL1 and URL2
# leave our forecast hour:
export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/GEM
cd ${WORKDIR}


currentdate=`date +"%Y%m%d"`
URL1='https://dd.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/'
URL2='/CMC_glb_TMP_TGL_2_latlon.15x.15_'
URL3='00_P'
URL4='.grib2'


for i in {000..120..3}; do
  echo $i
  URL=${URL1}${i}${URL2}${currentdate}${URL3}${i}${URL4}
  #echo $URL
  curl $URL -o CA${i}.grib2
done
currentdate=`date +"%Y-%m-%d"`
cdo mergetime *.grib2 merge.grib2
/home/cak/Desktop/software/grib2/wgrib2/wgrib2 merge.grib2 -netcdf temp.nc
cdo subc,273.15 temp.nc GEM_$currentdate.nc
cdo shaded,device="png",min=-5,max=25,lat_min=35,lat_max=45,lon_min=25,lon_max=45,step_freq=1 GEM_$currentdate.nc SC.png
convert -delay 40 'SC.png_TMP_2maboveground.%d.png[0-41]' GEM_${currentdate}_temp.gif
rm *.grib2
rm *.png
rm temp.nc
tar -czvf GEM_${currentdate}_bak.tar.gz GEM_${currentdate}.nc
mv GEM_${currentdate}_bak.tar.gz GEM_${currentdate}.nc ./Data
mv GEM_${currentdate}_temp.gif ./GIF

