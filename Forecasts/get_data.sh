#!/bin/bash
export WORKDIR=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/DWD
export ICON_GRID_FILE=//home/cak/Desktop/Jupyter-lumped-models/Forecasts/Convert/icon_grid_0026_R03B07_G.nc
export TARGET_GRID_DESCRIPTION=//home/cak/Desktop/Jupyter-lumped-models/Forecasts/Convert/target_grid_EUAU_0125.txt
export WEIGHTS_FILE=/home/cak/Desktop/Jupyter-lumped-models/Forecasts/Convert/weights.nc

cd ${WORKDIR}
wget --no-parent -r https://opendata.dwd.de/weather/nwp/icon/grib/00/t_2m/
wget --no-parent -r https://opendata.dwd.de/weather/nwp/icon/grib/00/tot_prec/
wget --no-parent -r https://opendata.dwd.de/weather/nwp/icon/grib/00/u_10m/
wget --no-parent -r https://opendata.dwd.de/weather/nwp/icon/grib/00/relhum_2m/
wget --no-parent -r https://opendata.dwd.de/weather/nwp/icon/grib/00/ps/
#https://opendata.dwd.de/weather/nwp/icon/grib/00/tot_prec/
find -iname '*.grib2*' -exec mv -t ${WORKDIR} {} +
for file in *.grib2.bz2;do bzip2 -d $file;done;
rm -rf opendata.dwd.de/
currentdate=`date +"%Y-%m-%d"`

for file in *.grib2;do cdo -f nc remap,${TARGET_GRID_DESCRIPTION},${WEIGHTS_FILE} $file  ${file%%.*}.nc;done;
cdo mergetime *T_2M*.nc temp.nc
cdo subc,273.15 temp.nc ${currentdate}_temp.nc
cdo mergetime *TOT_PREC*.nc ${currentdate}_precipitation.nc
cdo mergetime *U_10M*.nc ${currentdate}_wind.nc
cdo mergetime *RELHUM_2M*.nc ${currentdate}_humidity.nc
cdo mergetime *PS*.nc ${currentdate}_pressure.nc
rm icon*
rm temp.nc
cdo merge $currentdate*.nc $currentdate.nc
tar -czvf ${currentdate}_bak.tar.gz $currentdate.nc
rm ${currentdate}_*.nc