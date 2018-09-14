
import psycopg2
import psycopg2.extras

def a_point():
  for x in range(10):
    yield (x, x+1)

conn = psycopg2.connect(host='localhost', database='myki_gis', user='loader', password='bgtyhnBGTYHN')
cur = conn.cursor()

sql = "INSERT INTO temp VALUES(ST_POINT(%s,%s))"
psycopg2.extras.execute_batch(cur, sql, a_point())

conn.commit()
conn.close()