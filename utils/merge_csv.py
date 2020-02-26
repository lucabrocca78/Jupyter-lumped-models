import os
import glob

os.chdir("/home/cak/Desktop/jupyter/Notebook/Data/CSV")


import fileinput
from glob import glob
output = 'combined.csv'
files = glob('*.csv')


with open(output, 'w' ) as result:
    for thefile in files:
        with open(thefile) as f:
            next(f)
            for line in f:
                result.write( line )
