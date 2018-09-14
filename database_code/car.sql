DROP TABLE IF EXISTS car;

CREATE TABLE car(
  idx INTEGER,
  lat double precision,
  lon double precision,
  hour INTEGER,
  mean double precision,
  std double precision
);

GRANT ALL PRIVILEGES ON TABLE car TO loader;