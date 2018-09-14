-- SELECT *
-- FROM stops_gis a
-- WHERE ST_DWithin(a.stop_pos, (SELECT b.stop_pos FROM stops_gis b LIMIT 1), 500, false);

-- DROP TABLE IF EXISTS nearby_stops;

-- CREATE TABLE nearby_stops AS
-- SELECT a.stop_id as a_id, b.stop_id as b_id
-- FROM (SELECT * FROM stops_gis LIMIT 1000) a
--   INNER JOIN stops_gis b
--     ON a.stop_id <> b.stop_id and ST_DWithin(a.stop_pos, b.stop_pos, 500, false);
-- CREATE INDEX ON nearby_stops(a_id);

DROP VIEW IF EXISTS all_intersections;
CREATE VIEW all_intersections as
SELECT a.route_id as route_id1, b.route_id as route_id2,
    a.stop_id as stop_id1, b.stop_id as stop_id2,
    a.stop_sequence as seq_no1, b.stop_sequence as seq_no2
  FROM route_stops a
    INNER JOIN nearby_stops n ON a.stop_id = n.a_id
    INNER JOIN route_stops b ON b.stop_id = n.b_id AND a.route_id < b.route_id;

SELECT COUNT(*) FROM (
  SELECT * FROM (
    SELECT DISTINCT ON (route_id1, route_id2)
      route_id1, route_id2, stop_id1, stop_id2, seq_no1, seq_no2
    FROM all_intersections
    ORDER BY route_id1, route_id2, seq_no1 ASC
  ) abc
  UNION
  SELECT * FROM (
    SELECT DISTINCT ON (route_id1, route_id2)
      route_id1, route_id2, stop_id1, stop_id2, seq_no1, seq_no2
    FROM all_intersections
    ORDER BY route_id1, route_id2, seq_no1 DESC
  ) abs
) aa;
