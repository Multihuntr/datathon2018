import psycopg2
import functools

static_conn = None

with open('conf/pass', 'r') as f:
  password = f.read().rstrip('\n')

def new_connection():
  return psycopg2.connect(host='172.17.0.2', database='myki', user='loader', password=password)

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

def car_speeds(hour):
  sql = "SELECT lat, lon, mean, std FROM car WHERE hour=%s"
  return fetchsome(sql, (hour,))