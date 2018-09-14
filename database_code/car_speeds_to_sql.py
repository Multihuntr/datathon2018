import csv
import sys
import psycopg2
import psycopg2.extras

import db

col = ['idx','lat','lon','hour','mean','std']
col_str = (', '.join(['%({:s})s'] * len(col))).format(*col)
sql = "INSERT INTO car VALUES({:s});".format(col_str)

def to_list(s):
  return [float(q.strip()) for q in s[1:-1].split(',')]

def load(filename):
  with open(filename, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    i = 0
    for row in reader:
      # location index,lat,lon,mean_speed,std_speed
      idx = int(row[0])
      lat = float(row[1])
      lon = float(row[2])
      mean_spd = to_list(row[3])
      std_spd = to_list(row[4])
      for t, (mean, std) in enumerate(zip(mean_spd, std_spd)):
        i += 1
        print(i, end='\r', flush=True)
        yield dict(zip(col, (idx, lat, lon, t, mean, std)))

conn = db.new_connection()
cur = conn.cursor()
lines = load(sys.argv[1])
psycopg2.extras.execute_batch(cur, sql, lines, 1000)
conn.commit()
conn.close()