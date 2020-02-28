import cdstoolbox as ct


@ct.application(title='Daily aggregation')
@ct.output.download()
@ct.output.download()
@ct.output.figure()
@ct.output.figure()
def application():
    # retrieve temperature and total precipitation
    temp, total_prec = ct.catalogue.retrieve(
        'reanalysis-era5-single-levels',
        {
            'variable': ['2m_temperature', 'total_precipitation'],
            'product_type': 'reanalysis',
            'year': '2017',
            'month': '01',
            'day': ['01', '02'],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00'
            ]
        }
    )

    # compute daily daily temperature mean
    temp_daily_mean = ct.cube.resample(temp, freq='D', how='mean')
    print(temp_daily_mean)

    # compute daily accumulation of precipitation
    prec_daily_acc = ct.cube.resample(total_prec, freq='D', how='sum', closed='right')
    print(prec_daily_acc)

    # plot daily mean temperature for a selected day
    temp_plot = ct.cdsplot.geomap(
        ct.cube.select(temp_daily_mean, time='2017-01-01'),
        title='Daily mean temperature',
        projection=ct.cdsplot.crs.PlateCarree()
    )

    # plot daily mean temperature for a selected day
    prec_plot = ct.cdsplot.geomap(
        ct.cube.select(prec_daily_acc, time='2017-01-01'),
        title='Daily accumulated precipitation',
        projection=ct.cdsplot.crs.PlateCarree()
    )

    return temp_daily_mean, prec_daily_acc, temp_plot, prec_plot
