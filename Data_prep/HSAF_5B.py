import glob, re
import reconnecting_ftp
import os, sys, gzip
from ftplib import FTP
import datetime
# Reprojection
import pandas as pd

os.chdir('/home/cak/Desktop/H05B')


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#" * x, "." * (size - x), j, count))
        file.flush()

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def grabFile(product_flag, date_tag, ftp):
    try:
        dir = os.path.join(os.getcwd(), product_flag + '_data')
        tail = None
        if product_flag == "h10" or product_flag == "h34":
            tail = "_day_merged.H5.gz"
        else:
            tail = "_0000_24_fdk.grb.gz"

        file_ = product_flag + "_" + date_tag + tail
        if file_ not in ftp.nlst():
            print(file_, "given date is not accesible in the FTP")
        else:
            localfile = open(os.path.join(dir, file_), 'wb')
            ftp.retrbinary('RETR ' + file_, localfile.write, 1024)
            localfile.close()
            compressed_file = os.path.join(dir, file_)
            input = gzip.GzipFile(compressed_file, 'rb')
            s = input.read()
            input.close()
            output = open(os.path.join(dir, file_[:-3]), 'wb')
            output.write(s)
            output.close()
            os.remove(compressed_file)
    except:
        print("There is a problem downlading the product")


def download(username, password, product, indate, outdate):
    try:
        with reconnecting_ftp.Client(hostname="ftphsaf.meteoam.it", port=21, user=username, password=password) as ftp:
            print('Connected')
            dir = product + '/' + product + '_cur_mon_data'
            ftp.cwd(dir)
            in_ = indate
            last_ = outdate
            init_date = datetime.datetime.strptime(in_, "%Y%m%d")
            last_date = datetime.datetime.strptime(last_, "%Y%m%d")
            filelist = []
            days = last_date - init_date

            if not os.path.exists(product + '_data'):
                os.makedirs(product + '_data')

            for i in progressbar(range(days.days), "Downloading: ", 40):
                date = ((init_date + datetime.timedelta(days=i)).strftime("%Y%m%d"))
                grabFile(product, date, ftp)
            print("Download Process has been finished")
    except:
        print("username or password is not correct")


username = 'cagri.karaman@hidrosaf.com'
password = 'kalman01'
product = 'h05B'
indate = '2020-01-09'
outdate = '2020-01-19'
# download(username, password, str(product), str(indate).replace('-', ''), str(outdate).replace('-', ''))

files = glob.glob1('./' + product + '_data', '*.grb')
file = files[0]
name = file[5:9] + '-' + file[9:11] + '-' + file[11:13]

os.chdir(os.path.join(os.getcwd(), product + '_data'))
# os.system('wgrib2 {} -csv out.csv'.format(file))
# code = """awk '{FS = ","}; { print $5, $6, $7}' out.csv > out.csv_new"""
# os.system(code)
df = pd.read_csv('out.csv', names=['Date', 'Date1', 'Var', 'lon', 'lat', 'value'])
df.reset_index(drop=True, inplace=True)
df_new = df[['lon', 'lat', 'value']]
indexNames = df_new[
    (df_new['lat'] < -500) | (df_new['lat'] > 500) | (df_new['lon'] < -500) | (df_new['lon'] > 500)].index
df_new.drop(indexNames, inplace=True)
df_new.to_csv('grid.csv', index=False)
code = """gdal_grid -zfield value -l grid grid.vrt {}_h05b.tif""".format(name)
os.system(code)
os.remove('grid.csv')
os.remove('out.csv')
