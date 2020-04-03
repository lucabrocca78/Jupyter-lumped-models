#!/bin/bash
# set the base URL in two parts: URL1 and URL2
# leave our forecast hour:
export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/GFS
cd ${WORKDIR}

URL1='https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f'
URL2='&lev_2_m_above_ground=on&var_TMP=on&leftlon=25&rightlon=45&toplat=45&bottomlat=35&dir=%2Fgfs.'
URL3='%2F00'

# Let forecast hour vary from 0 to 24.
# It needs to have three digits, so we start with 1000:
cdate=$(date +"%Y%m%d")
for i in {0..120}; do
  echo $i
  TFCH=$(expr 1000 + $i)
  FCH=$(echo $TFCH | cut -c2-4)
  URL=${URL1}${FCH}${URL2}${cdate}${URL3}
  curl $URL -o GFS${FCH}.grb
done

currentdate=$(date +"%Y-%m-%d")
for file in *.grb; do wgrib2 $file -netcdf ${file%%.*}.nc; done
cdo mergetime *.nc temp.nc
cdo subc,273.15 temp.nc GFS_${currentdate}_temp.nc
rm *.grb
rm temp.nc
rm GFS0*
rm GFS1*

cdo shaded,device="png",min=-5,max=25,lat_min=35,lat_max=45,lon_min=25,lon_max=45,step_freq=1 -selvar,TMP_2maboveground GFS_${currentdate}_temp.nc SC.png
convert -delay 40 'SC.png_TMP_2maboveground.%d.png[0-120]' GFS_${currentdate}_temp.gif
mv GFS_${currentdate}_temp.gif ./GIF
mv GFS_${currentdate}_temp.nc ./Data
rm *.png
cd ./Data
tar -czvf GFS_${currentdate}_temp_bak.tar.gz GFS_${currentdate}_temp.nc
