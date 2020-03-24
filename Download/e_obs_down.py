import cdsapi

c = cdsapi.Client()
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'sis-agrometeorological-indicators',
    {
        'format': 'tgz',
        'variable': '2m_temperature',
        'area': '43/25/35/45',
        'statistics': [
            '24_hour_maximum', '24_hour_mean', '24_hour_minimum',
        ],
        'year': [
            # '2010', '2011', '2012', '2013',
            '2018',
            # '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
    },
    'Agrometeorological_daily_temp_2018.tar.gz')
