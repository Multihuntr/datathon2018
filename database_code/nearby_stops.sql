-- The stops which are very close to each other
-- Approx run-time for this is 15mins
DROP TABLE IF EXISTS nearby_stops;
CREATE TABLE nearby_stops AS
SELECT a.stop_id as a_id, b.stop_id as b_id
FROM stops_gis a
  INNER JOIN stops_gis b
    ON a.stop_id <> b.stop_id and ST_DWithin(a.stop_pos, b.stop_pos, 200, false);
CREATE INDEX ON nearby_stops(a_id);

-- We want to be able to use time to search the stop_times, so we need the days of the week per row
DROP VIEW IF EXISTS stop_times_calendar;
CREATE VIEW stop_times_calendar AS
SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday, st.*
FROM trips INNER JOIN calendar USING(service_id) INNER JOIN stop_times st USING(trip_id);

-- Then we can construct a fuzzy sort of stop_times, where we only care if it stops nearby
-- to one of the stops
-- This essentially lists all of the variations we could have at each stop_sequence
-- By indexing by stop_id, the day of the week and the time, queries that use only these
--  will be pretty damn fast
--  (yeah, yeah, it'll take up a few GB to do this, but the speed is worth it:
--    on my machine, I'm getting over 1000 inner joins on this table with time ranges per second)
--      (I promise that I'm not addicted to speed (the drug))
--             (This is what happens when you write comments at 2am on a Sunday)
DROP TABLE IF EXISTS fuzzy_stop_times;
CREATE TABLE fuzzy_stop_times AS
SELECT trip_id, departure_time, b.b_id as stop_id, stop_sequence, shape_dist_traveled,
  monday,tuesday,wednesday,thursday,friday,saturday,sunday
FROM stop_times_calendar a INNER JOIN
  nearby_stops b ON a.stop_id=b.a_id
UNION
SELECT trip_id, departure_time, stop_id, stop_sequence, shape_dist_traveled,
  monday,tuesday,wednesday,thursday,friday,saturday,sunday
FROM stop_times_calendar;
CREATE INDEX ON fuzzy_stop_times(stop_id);
CREATE INDEX ON fuzzy_stop_times(trip_id);
CREATE INDEX ON fuzzy_stop_times(stop_id, monday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, tuesday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, wednesday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, thursday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, friday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, saturday, departure_time);
CREATE INDEX ON fuzzy_stop_times(stop_id, sunday, departure_time);

-- We can use this as a fast way of checking if two stops approximately share a trip
--  instead of only being able to check for exact stop matches.
--  (Hence can we map the stops they probably went through on their way/trust a touchon/touchoff pair)
-- (see db.py:stops_share_trip())