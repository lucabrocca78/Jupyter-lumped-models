library(raster)
library(dplyr)
library(tidyr)
library(lubridate)
library(stringr)
library(tibble)

setwd('/home/cak/Desktop/jupyter/Notebook/')
lat <- read.csv("lat.csv",header=F)
lon <- read.csv("lon.csv",header=F)	

folder <- '/home/cak/Desktop/jupyter/Notebook/Data/ERA5/'
files <- list.files(folder, pattern="\\.nc$", recursive=TRUE, full.names=TRUE)
file <- '/home/cak/Desktop/jupyter/Notebook/Data/ERA5/temp_daily.nc'
index <- 1
file_num <- 1
for (currentFile in files) {
  b<-brick(currentFile)
  #b<-brick(file)
  
  date = getZ(b)
  
  df <- data.frame(datime = character(), data = double(),index = numeric()
                   , stringsAsFactors = FALSE)
  df_index <- data.frame(index = numeric(),lon = double(),lat = double()
                         , stringsAsFactors = FALSE)
  df_time <- data.frame(Date = date)
  n <- 72
  sprintf("Started at: %s", format(Sys.time(), "%a %b %d %X %Y"))
  for(i in 1:length(lat[2,])) {
    for(j in 1:length(lon[2,])) {
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
    }
    
  }
  out_file = paste0(toString(file_num),'_.csv')
  out_index = paste0(toString(file_num),'_index.csv')
  df <- within(df, rm(z))
  write.csv(df,out_file)
  write.csv(df_index,out_index)
}





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




