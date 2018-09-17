import psycopg2
import functools

with open('conf/pass', 'r') as f:
  password = f.read().rstrip('\n')

def connect():
  return psycopg2.connect(host='172.17.0.2', database='myki', user='loader', password=password)

def fetchall(sql):
  conn = connect()
  cur = conn.cursor()
  cur.execute(sql)
  res = cur.fetchall()
  cur.close()
  conn.close()
  return res

def fetchsome(sql, args):
  conn = connect()
  cur = conn.cursor()
  cur.execute(sql, args)
  res = cur.fetchall()
  cur.close()
  conn.close()
  return res

def car_speeds(hour):
  sql = "SELECT lat, lon, mean, std FROM car WHERE hour=%s;"
  return fetchsome(sql, (hour,))

def stops():
  sql = 'SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops;'
  return fetchall(sql)

def journey_trips(sql, stop_id):
  return fetchsome(sql, (stop_id, stop_id))

def nearby_stops(stop_id):
  sql = 'SELECT b_id FROM nearby_stops WHERE a_id=%s'
  return [x[0] for x in fetchsome(sql, (stop_id,))]

def trip_stops(cur, sql, args):
  cur.execute(sql, args)
  stops = cur.fetchall() # list((stop_id, dist))
  return stops

def journeys_about(stop_id):
  # We select all journeys with this stop in them.
  sql_trips = '''
    SELECT journey_id, leg_seq, trip_id, start_stop_id, end_stop_id, start_trip_seq, end_trip_seq, leg_time
    FROM journey_leg
    WHERE journey_id IN
      (SELECT journey_id FROM journey_leg WHERE first_last=true and (start_stop_id=%s OR end_stop_id=%s))
    ORDER BY journey_id, leg_seq;
  '''
  sql_stops = '''
    SELECT stop_id, shape_dist_traveled
    FROM stop_times
    WHERE trip_id=%s and stop_sequence >=%s and stop_sequence <=%s;'''
  trips = journey_trips(sql_trips, stop_id)
  conn = connect()
  cur = conn.cursor()
  prev_journey_id = None
  journey = []
  for journey_id, leg_seq, trip_id, start_stop_id, end_stop_id, start_seq, stop_seq, leg_time in trips:
    if journey_id != prev_journey_id and prev_journey_id is not None:
      yield journey_id, journey
      journey = []
    # Get stops for this journey
    stops = trip_stops(cur, sql_stops, (trip_id, start_seq, stop_seq))
    journey.append((trip_id, leg_time, stops))
    prev_journey_id = journey_id
  yield journey_id, journey


