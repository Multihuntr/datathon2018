-- These are database queries that produce static data for
-- the server to quickly respond to queries
DROP TABLE IF EXISTS route_stops CASCADE;

CREATE TABLE route_stops AS
SELECT route_id, stop_id, shape_pt_sequence, shape_dist_traveled
FROM (
  SELECT DISTINCT route_id, stop_id
  FROM stop_times
  INNER JOIN trips USING(trip_id)
  GROUP BY route_id, stop_id
) a INNER JOIN

CREATE INDEX ON route_stops(route_id);
CREATE INDEX ON route_stops(stop_id);

-- Now we need to find the route intersections

-- Start with the stops which are within walking distance (500m) of each other
-- Approx run-time for this is 15mins
CREATE TABLE nearby_stops AS
SELECT a.stop_id as a_id, b.stop_id as b_id
FROM stops_gis a
  INNER JOIN stops_gis b
    ON a.stop_id <> b.stop_id and ST_DWithin(a.stop_pos, b.stop_pos, 500, false);
CREATE INDEX ON nearby_stops(a_id);

-- We want to find all the DISTINCT intersections between routes
-- But, consider that in order to find the minimum path the
-- customer has travelled we need to know the first stop
-- in the section that they overlap from either direction
--                Here                And Here
--                 v                     v
-- Route A ---------                     -------------
--                  ---------------------
-- Route B ---------                     -------------
--                  | all_intersections |
DROP VIEW IF EXISTS all_intersections;
CREATE VIEW all_intersections as
SELECT a.route_id as route_id1, b.route_id as route_id2,
    a.stop_id as stop_id1, b.stop_id as stop_id2,
    a.stop_sequence as seq_no1, b.stop_sequence as seq_no2
  FROM route_stops a
    INNER JOIN nearby_stops n ON a.stop_id = n.a_id
    INNER JOIN route_stops b ON b.stop_id = n.b_id AND a.route_id < b.route_id;

-- Now we can find the minimum and maximum sequence numbers for Route a in
-- the intersection and union them. So, when you query
--    SELECT * FROM intersections WHERE route_id1 = 'routeA';
-- You get 2 rows, one for each side of the region that it overlaps.
-- And we assume that a journey spanning more than one route goes through
-- one of these points
-- ASSUMPTION: This never happens:
-- Route A --------        ----------        ---------
--                 --------          --------
-- Route B --------        ----------        ---------
CREATE TABLE intersections as
SELECT * FROM (
  SELECT DISTINCT ON (route_id1, route_id2)
    route_id1, route_id2, stop_id1, stop_id2, seq_no1, seq_no2
  FROM all_intersections
  ORDER BY route_id1, route_id2, seq_no1 ASC
) mins
UNION
SELECT * FROM (
  SELECT DISTINCT ON (route_id1, route_id2)
    route_id1, route_id2, stop_id1, stop_id2, seq_no1, seq_no2
  FROM all_intersections
  ORDER BY route_id1, route_id2, seq_no1 DESC
) maxes;
