DROP TABLE IF EXISTS stop_times_calendar;
CREATE TABLE stop_times_calendar AS
SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday, st.*
FROM trips INNER JOIN calendar USING(service_id) INNER JOIN stop_times st USING(trip_id);
CREATE INDEX ON stop_times_calendar(stop_id, monday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, tuesday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, wednesday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, thursday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, friday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, saturday, departure_time);
CREATE INDEX ON stop_times_calendar(stop_id, sunday, departure_time);
