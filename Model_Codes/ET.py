import pandas as pd
import numpy as np
import os
from pyeto import thornthwaite, monthly_mean_daylight_hours, deg2rad


os.chdir(r"C:\Users\PC3\Desktop\Hydro")

df = pd.read_csv('data.csv')

df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df = df.set_index('Date')
df_m = df.resample("M").mean()


data = []
lat = deg2rad(41.3)
for i in range(2015,2019):

    mmdlh = monthly_mean_daylight_hours(lat, i)
    monthly_t = df_m['Temp'][(df_m.Year == i)]
    PET = thornthwaite(monthly_t.values.tolist(), mmdlh)
    data.append(PET)

print("a")
