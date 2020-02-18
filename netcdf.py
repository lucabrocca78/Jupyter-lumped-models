import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd

file = '/media/cak/AT/Datasets/EOBS/tg_ens_mean_0.1deg_reg_v20.0e.nc'

time = pd.date_range('2000-01-01', freq='1D', periods=365)
ds = xr.open_dataset(file)
# dsloc = ds.sel(longitude=37, latitude=37.0, time=time,method='nearest')
dsloc = ds.sel(longitude=[37,39], latitude=[37.0,40], time = time,method='nearest')
# dsloc['tn'].mean(dim='time')
dsloc['tg'].plot();
plt.show()
