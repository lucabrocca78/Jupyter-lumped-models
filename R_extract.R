library(raster)
library(dplyr)
library(tidyr)
library(lubridate)
library(stringr)
library(tibble)

b<-brick('~/Desktop/jupyter/Notebook/Data/ERA5/test.nc')
setwd('/home/cak/Desktop/jupyter/Notebook/')
lat <- read.csv("lat.csv",header=F)
lon <- read.csv("lon.csv",header=F)	

points<-SpatialPoints(cbind(lon,lat))

plot(b[[1]], xlim=extent(points)[c(1,2)],ylim=extent(points)[c(3,4)])
plot(points, add=T)

points_data <- b %>% 
  raster::extract(points, df = T) %>% 
  gather(time, value, -ID) %>% 
  spread(ID, value) %>%   # Can be skipped if you want a "long" table
  as_tibble()

for(i in 1:nrow(lat)) {
  for(j in 1:nrow(lon)) {
    row <- lat[i,]
    row1 <- lon[j,]
    points<-SpatialPoints(cbind(row1,row))
    points_data <- b %>% 
      raster::extract(points, df = T) %>% 
      gather(time, value, -ID) %>% 
      spread(ID, value) %>%   # Can be skipped if you want a "long" table
      as_tibble()
  }
}


      