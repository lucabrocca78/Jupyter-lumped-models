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
date = getZ(b)

# points<-SpatialPoints(cbind(lon,lat))
# 
# plot(b[[1]], xlim=extent(points)[c(1,2)],ylim=extent(points)[c(3,4)])
# plot(points, add=T)
# 
# points_data <- b %>% 
#   raster::extract(points, df = T) %>% 
#   gather(time, value, -ID) %>% 
#   spread(ID, value) %>%   # Can be skipped if you want a "long" table
#   as_tibble()

df <- data.frame(datime = character(), data = double(),index = numeric()
                 , stringsAsFactors = FALSE)
df_index <- data.frame(index = numeric(),lon = double(),lat = double()
                 , stringsAsFactors = FALSE)

df_time <- data.frame(Date = date)
index = 1
n <- 72
for(i in 1:length(lat[,])) {
  for(j in 1:length(lon[,])) {
    row <- lat[i,]
    row1 <- lon[j,]
    points<-SpatialPoints(cbind(row1,row))
    points_data <- b %>%
      raster::extract(points, df = T) %>%
      gather(z, value, -ID) %>%
      spread(ID, value) %>%   # Can be skipped if you want a "long" table
      as_tibble()
    temp = cbind(date=date,points_data,index = index)
    df <- rbind(df, temp)
    temp1 <- cbind(index,row1,row)
    df_index <- rbind(df_index, temp1)
    index = index + 1
    print(i)
  }
  
}
df <- within(df, rm(z))
write.csv(df,'df.csv',)
write.csv(df_index,'index.csv')

      
