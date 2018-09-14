CREATE EXTENSION postgis;

DROP TABLE IF EXISTS stops_gis;
DROP TABLE IF EXISTS shapes_gis;
DROP TABLE IF EXISTS car_gis;

CREATE TABLE stops_gis AS
SELECT stop_id, stop_name, ST_POINT(stop_lon, stop_lat) AS stop_pos
FROM stops;
CREATE INDEX ON stops_gis(stop_id);
CREATE INDEX ON stops_gis USING gist(stop_pos);

CREATE TABLE shapes_gis AS
SELECT shape_id,
        ST_POINT(shape_pt_lon, shape_pt_lat) AS shape_pos,
        shape_pt_sequence, shape_dist_traveled
FROM shapes;
CREATE INDEX ON shapes_gis USING gist(shape_pos);

CREATE TABLE car_gis AS
SELECT idx, ST_POINT(lon, lat) AS car_pos, hour, mean, std
FROM car;
