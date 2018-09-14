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

def routes():
  sql = "SELECT route_id, stop_id, shape_dist_traveled FROM route_stops;"
  return fetchall(sql)

def intersections():
  sql = "SELECT route_id1, route_id2, stop_id1, stop_id2, seq_no1, seq_no2 FROM intersections;"
  return fetchall(sql)

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

def trips_by_stop_time(stop_id, stop_time):
  '''Finds trips based on a stop time and stop id

  Args:
      stop_id (id): stop_id in question
      stop_time (datetime.datetime): time to search around

  Returns:
      list(tuple(trip_id, stop_seq)): the trip and where it appears in the trip
  '''
  stop_time_lower = str((stop_time - datetime.timedelta(minutes=5)).time())
  stop_time_upper = str((stop_time + datetime.timedelta(minutes=5)).time())
  weekday_str = weekdays[stop_time.weekday()]
  sql = """SELECT DISTINCT trip_id, stop_sequence
    FROM stop_times_calendar
    WHERE stop_id=%s and {:s}=true and departure_time >= %s and departure_time <= %s"""\
    .format(weekday_str)
  return fetchsome(sql, (stop_id, stop_time_lower, stop_time_upper))

def stop_dist(a, b, d):
  sql = "SELECT ST_DWithin(a.stop_pos, b.stop_pos, %s, false) FROM stops_gis " \
   + "a inner join stops_gis b on a.stop_id=%s and b.stop_id=%s;"
  return fetchsome(sql, (d,a,b))[0][0]

def valid_trip(id, first, second):
  sql = "SELECT stop_sequence FROM stop_times WHERE stop_id=%s"
  first_seq = fetchsome(sql, (first,))[0][0]
  second_seq = fetchsome(sql, (second,))[0][0]
  return first_seq < second_seq