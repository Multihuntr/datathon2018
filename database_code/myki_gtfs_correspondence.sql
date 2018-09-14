DROP TABLE IF EXISTS myki_stops;

CREATE TABLE myki_stops
(
  stop_id           integer PRIMARY KEY,
  stop_short_name   text NULL,
  stop_long_name    text NULL,
  stop_pickup_type  text NULL,
  stop_suburb       text NULL,
  stop_postcode     integer NULL,
  stop_region       text NULL,
  stop_govnmt       text NULL,
  stop_stat_div     text NULL,
  stop_lat          double precision NULL,
  stop_lon          double precision NULL
);

\copy myki_stops from './stop_locations.txt' with csv delimiter '|';

DROP TABLE IF EXISTS myki_stops_gis;

CREATE TABLE myki_stops_gis AS
SELECT stop_id, stop_short_name, stop_long_name, stop_pickup_type,
stop_suburb, stop_postcode, stop_region, stop_govnmt, stop_stat_div,
ST_POINT(stop_lon, stop_lat) as stop_pos
FROM myki_stops;
CREATE INDEX ON myki_stops_gis USING gist(stop_pos);

DROP TABLE IF EXISTS matching_ids;
CREATE TABLE matching_ids AS
SELECT a.stop_id as stop_id
FROM myki_stops_gis a
  inner join stops_gis b
    on a.stop_id = b.stop_id;
CREATE INDEX ON matching_ids(stop_id);

DROP TABLE IF EXISTS stop_id_matching;
CREATE TABLE stop_id_matching AS
SELECT DISTINCT ON(myki_stop_id) a.stop_id myki_stop_id, b.stop_id gtfs_stop_id
from (SELECT * FROM myki_stops_gis where stop_id not in (SELECT * FROM matching_ids)) a
  inner join stops_gis b
    on a.stop_long_name = b.stop_name and a.stop_id <> b.stop_id;
CREATE INDEX ON stop_id_matching(myki_stop_id);
