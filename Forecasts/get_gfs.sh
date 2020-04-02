#!/bin/bash
# set the base URL in two parts: URL1 and URL2
# leave our forecast hour:
export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/GFS
cd ${WORKDIR}

URL1='https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f'
URL2='&lev_2_m_above_ground=on&var_TMP=on&subregion=&leftlon=25&rightlon=45&toplat=45&bottomlat=35&dir=%2Fgfs.20200402%2F00'
# Let forecast hour vary from 0 to 24.
# It needs to have three digits, so we start with 1000:
for i in {0..120}
do
  echo $i
  TFCH=`expr 1000 + $i`
  FCH=`echo $TFCH | cut -c2-4`
  URL=${URL1}${FCH}${URL2}
  curl $URL -o GFS${FCH}.grb
done

currentdate=`date +"%Y-%m-%d"`
for file in *.grb;do /home/cak/Desktop/software/grib2/wgrib2/wgrib2 $file -netcdf ${file%%.*}.nc;done;
cdo mergetime *.nc temp.nc
cdo subc,273.15 temp.nc GFS_${currentdate}_temp.nc
rm GFS*
rm temp.nc