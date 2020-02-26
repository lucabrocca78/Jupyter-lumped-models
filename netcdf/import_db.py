import netCDF4, psycopg2, time
import psycopg2.extras

# Establish connection
db1 = psycopg2.connect("host=localhost dbname=postgres user=postgres password=kalman")
cur = db1.cursor()

# Create Table in postgis
print(str(time.ctime()) + " CREATING TABLE")
try:
    cur.execute("DROP TABLE IF EXISTS table_name;")
    db1.commit()
    cur.execute(
        "CREATE TABLE table_name (gid serial PRIMARY KEY not null, thedate DATE, thepoint geometry, lon decimal, lat decimal, thevalue decimal);")
    db1.commit()
    print("TABLE CREATED")
except:
    print(psycopg2.DatabaseError)
    print("TABLE CREATION FAILED")

rawvalue_nc_file = '/home/cak/Desktop/jupyter/Notebook/Data/ERA5/test.nc'
nc = netCDF4.Dataset(rawvalue_nc_file, mode='r')
nc.variables.keys()

lat = nc.variables['latitude'][:]
lon = nc.variables['longitude'][:]
time_var = nc.variables['time']
dtime = netCDF4.num2date(time_var[:], time_var.units)
newtime = [fdate.strftime("%m/%d/%Y, %H:%M:%S") for fdate in dtime]
rawvalue = nc.variables['t2m'][:]

lathash = {}
lonhash = {}
entry1 = 0
entry2 = 0

lattemp = nc.variables['latitude'][:].tolist()
for entry1 in range(lat.size):
    lathash[entry1] = lattemp[entry1]

lontemp = nc.variables['longitude'][:].tolist()
for entry2 in range(lon.size):
    lonhash[entry2] = lontemp[entry2]

for timestep in range(dtime.size):
    print(str(time.ctime()) + " " + str(timestep + 1) + "/180")
    values = []

    cur.execute("BEGIN")

    for _lon in range(lon.size):
        for _lat in range(lat.size):
            latitude = round(lathash[_lat], 6)
            longitude = round(lonhash[_lon], 6)
            thedate = newtime[timestep]
            thevalue = round(
                float(rawvalue.data[timestep, _lat, _lon] - 273.15), 3
            )
            if thevalue > -100:
                values.append((thedate, longitude, latitude, thevalue))

    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO table_name (thedate, thepoint,lon,lat,thevalue) VALUES %s",
        values,
        template="(%s, ST_MakePoint(%s,%s,0),%s,%s, %s)"
    )
    db1.commit()
cur.close()
db1.close()

print(" Done!")


import psycopg2
from shapely.geometry import LineString
from shapely import wkb

conn = psycopg2.connect('...')
curs = conn.cursor()

# Make a Shapely geometry
ls = LineString([(2.2, 4.4, 10.2), (3.3, 5.5, 8.4)])
ls.wkt  # LINESTRING Z (2.2 4.4 10.2, 3.3 5.5 8.4)
ls.wkb_hex  # 0102000080020000009A999999999901409A999999999911406666666666662440666666...

# Send it to PostGIS
curs.execute('CREATE TEMP TABLE my_lines(geom geometry, name text)')
curs.execute(
    'INSERT INTO my_lines(geom, name)'
    'VALUES (ST_SetSRID(%(geom)s::geometry, %(srid)s), %(name)s)',
    {'geom': ls.wkb_hex, 'srid': 4326, 'name': 'First Line'})

conn.commit()  # save data

# Fetch the data from PostGIS, reading hex-encoded WKB into a Shapely geometry
curs.execute('SELECT name, geom FROM my_lines')
for name, geom_wkb in curs:
    geom = wkb.loads(geom_wkb, hex=True)
    print('{0}: {1}'.format(name, geom.wkt))
# First Line: LINESTRING Z (2.2 4.4 10.2, 3.3 5.5 8.4)