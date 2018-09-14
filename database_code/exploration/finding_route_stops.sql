-- Given stop times, you can make a list of route_id, stop_id pairs
CREATE TABLE route_stops AS
SELECT DISTINCT route_id, stop_id
FROM stop_times
INNER JOIN trips USING(trip_id)
GROUP BY route_id, stop_id;
CREATE INDEX ON route_stops(route_id);


-- On one hand, we have the trips table which connects the routes and the
-- physical locations on a map. But these have no concept of which stop
-- the locations are...
create view route_shapes as
select route_id, shape_id, count(*) as c
from trips
group by route_id, shape_id
order by c desc;

select * from route_shapes limit 5;
--    route_id   |     shape_id     |  c
-- --------------+------------------+-----
--  3-19-mjp-1   | 3-19-mjp-1.1.H   | 529
--  3-19-mjp-1   | 3-19-mjp-1.3.R   | 529
--  11-SKY-mjp-1 | 11-SKY-mjp-1.1.H | 505
--  11-SKY-mjp-1 | 11-SKY-mjp-1.2.R | 496
--  3-58-mjp-1   | 3-58-mjp-1.5.R   | 449




-- I should check if any routes share the same shape...
select shape_id, count(*) as route_count
from route_shapes
group by shape_id
order by route_count desc
limit 5;
--       shape_id      | route_count
-- --------------------+-------------
--                     |          22
--  1-V23-G-mjp-1.31.R |           1
--  4-837-A-mjp-1.2.R  |           1
--  2-FKN-D-mjp-1.15.H |           1
--  5-V41-I-mjp-1.4.H  |           1

-- Ok, so shapes and routes have a 1-to-1 relationship.
-- Next, let's see if we can associate these points in the shape
--  table with a stop_id. If we can, we should pick a point with
--  the precise same lat/lon as noted in the shape table
select count(*) from shapes;
-- 3162588
select count(*)
from stops inner join shapes
    on stop_lat = shape_pt_lat and stop_lon = shape_pt_lon;
-- 88953

-- I guess that was too much to hope for...
-- After playing around a bit, I realise that the shapes do not
-- correspond to the stops at all... The shape defines the
-- points on the map that the service follows. i.e. the shape
-- defines every time that a service changes direction.
-- So, I have to make a decision; should I present the shape
-- locations or the stop locations?
-- The shape locations are not easily binnable, and it doesn't
-- reflect where you can actually get off the vehicle, anyway.


-- Stop redundancy

select count(*) from stops;
-- 27389

select count(*)
from stops a
  inner join stops b on a.stop_name = b.stop_name and a.stop_id <> b.stop_id;
-- 15578

-- Interestingly, they are not at the same positions
select count(*)
from stops a
  inner join stops b
    on a.stop_name = b.stop_name
      and a.stop_lat = b.stop_lat
      and a.stop_lon = b.stop_lon
      and a.stop_id <> b.stop_id;
-- 40

-- So how far away are they, actually?
select max(abs(a.stop_lat - b.stop_lat)) as lat, max(abs(a.stop_lon - b.stop_lon)) as lon
from stops a
  inner join stops b on a.stop_name = b.stop_name and a.stop_id <> b.stop_id;
--         lat         |         lon
-- --------------------+---------------------
--  0.0081606483640968 | 0.00561660888999427

-- https://www.movable-type.co.uk/scripts/latlong.html
-- Using an online tool, starting with a point in Melbourne,
-- I calculated the difference in distance:
-- a: -37.809173571755     144.943974981477
-- b: -37.8010129233909    144.949591590367
-- Gives a straight line distance of just over 1km

-- What about stops that have the same location, but not the same name?
select *
from stops a
  inner join stops b
    on a.stop_name <> b.stop_name
      and a.stop_lat = b.stop_lat
      and a.stop_lon = b.stop_lon
      and a.stop_id <> b.stop_id;
-- 18
-- Manually inspecting these tells me that these can be considered the same location without any problems