#!/bin/bash
apt-get update
apt-get install -y build-essential libaec-dev zlib1g-dev libcurl4-openssl-dev libboost-dev curl wget zip unzip bzip2 gfortran gcc g++
rm -rf /usr/local/grib2/
mkdir -p /usr/local/grib2/
cd /code/
if [ ! -f "/tmp/wgrib2.tgz" ]; then
	    wget ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz.v2.0.6c -O /tmp/wgrib2.tgz
fi
tar -xf /tmp/wgrib2.tgz
mv /tmp/grib2/ /usr/local/grib2/
cd /usr/local/grib2/grib2
export FC=gfortran && export CC=gcc
make && rm -rf /usr/local/bin/wgrib2
ln -s /usr/local/grib2/grib2/wgrib2/wgrib2 /usr/local/bin/wgrib2
rm /tmp/wgrib2.tgz
