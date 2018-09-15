import datetime
import psycopg2

static_conn = None

with open('conf/pass', 'r') as f:
  password = f.read().rstrip('\n')

def new_connection():
  return psycopg2.connect(host='localhost', database='myki', user='loader', password=password)

def connect():
  global static_conn
  if static_conn is None:
    static_conn = new_connection()
  return static_conn

def fetchall(sql):
  conn = connect()
  cur = conn.cursor()
  cur.execute(sql)
  res = cur.fetchall()
  cur.close()
  return res

def fetchsome(sql, args):
  conn = connect()
  cur = conn.cursor()
  cur.execute(sql, args)
  res = cur.fetchall()
  cur.close()
  return res

def stop_times():
  sql = "SELECT * FROM stop_times;"
  return fetchall(sql)

def trips():
  sql = "SELECT * FROM trips;"
  return fetchall(sql)

def stops():
  sql = "SELECT * FROM stops;"
  return fetchall(sql)

def stop_ids():
  sql = "SELECT stop_id FROM stops;"
  return [x[0] for x in fetchall(sql)]

def stop_id_matching():
  '''A lookup of stops that appear in myki, but not gtfs, and can be mapped to a gtfs stop'''
  sql = "SELECT * FROM stop_id_matching;"
  return fetchall(sql)

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def stop_dist(a, b, d):
  sql = "SELECT ST_DWithin(a.stop_pos, b.stop_pos, %s, false) FROM stops_gis " \
   + "a inner join stops_gis b on a.stop_id=%s and b.stop_id=%s;"
  return fetchsome(sql, (d,a,b))[0][0]

def stops_share_trip(a_stop_id, a_stop_time, b_stop_id, b_stop_time):
  a_weekday_str = weekdays[a_stop_time.weekday()]
  b_weekday_str = weekdays[b_stop_time.weekday()]
  sql = '''
    SELECT distinct a.trip_id, a.stop_sequence, b.stop_sequence
    FROM fuzzy_stop_times a INNER JOIN fuzzy_stop_times b USING(trip_id)
    WHERE a.stop_sequence<b.stop_sequence AND a.stop_id=%s AND b.stop_id=%s AND
    a.{:s}=true and a.departure_time >= %s and a.departure_time <= %s AND
    b.{:s}=true and b.departure_time >= %s and b.departure_time <= %s
    LIMIT 1;
  '''.format(a_weekday_str, b_weekday_str)
  a_lower = str((a_stop_time - datetime.timedelta(minutes=5)).time())
  a_upper = str((a_stop_time + datetime.timedelta(minutes=5)).time())
  b_lower = str((b_stop_time - datetime.timedelta(minutes=5)).time())
  b_upper = str((b_stop_time + datetime.timedelta(minutes=5)).time())
  return fetchsome(sql, (a_stop_id, b_stop_id, a_lower, a_upper, b_lower, b_upper))