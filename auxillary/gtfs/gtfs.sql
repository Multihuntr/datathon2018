DROP TABLE IF EXISTS agency CASCADE;
DROP TABLE IF EXISTS calendar CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS shapes CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS stop_times CASCADE;

CREATE TABLE agency
(
  agency_id         text UNIQUE NULL,
  agency_name       text NOT NULL,
  agency_url        text NOT NULL,
  agency_timezone   text NOT NULL,
  agency_lang       text NOT NULL
);

CREATE TABLE calendar
(
  service_id        text PRIMARY KEY,
  monday            boolean NOT NULL,
  tuesday           boolean NOT NULL,
  wednesday         boolean NOT NULL,
  thursday          boolean NOT NULL,
  friday            boolean NOT NULL,
  saturday          boolean NOT NULL,
  sunday            boolean NOT NULL,
  start_date        integer,
  end_date          integer
);

CREATE TABLE stops
(
  stop_id           integer PRIMARY KEY,
  stop_name         text NOT NULL,
  stop_lat          double precision NOT NULL,
  stop_lon          double precision NOT NULL
);

CREATE TABLE routes
(
  route_id          text PRIMARY KEY,
  agency_id         text NULL,
  route_short_name  text NULL,
  route_long_name   text NULL,
  route_type        integer NULL,
  route_color       text NULL,
  route_text_color  text NULL
);

CREATE TABLE shapes
(
  shape_id          text NOT NULL,
  shape_pt_lat      double precision NOT NULL,
  shape_pt_lon      double precision NOT NULL,
  shape_pt_sequence integer NOT NULL,
  shape_dist_traveled text NULL
);
CREATE INDEX ON shapes(shape_id);

CREATE TABLE trips
(
  route_id          text NOT NULL references routes(route_id),
  service_id        text NOT NULL references calendar(service_id),
  trip_id           text NOT NULL PRIMARY KEY,
  shape_id          text NOT NULL,
  trip_headsign     text NULL,
  direction_id      boolean NULL
);

CREATE TABLE stop_times
(
  trip_id           text NOT NULL references trips(trip_id),
  arrival_time      interval NOT NULL,
  departure_time    interval NOT NULL,
  stop_id           integer NOT NULL references stops(stop_id),
  stop_sequence     integer NOT NULL,
  stop_headsign     text NULL,
  pickup_type       integer NULL CHECK(pickup_type >= 0 and pickup_type <=3),
  drop_off_type     integer NULL CHECK(drop_off_type >= 0 and drop_off_type <=3),
  shape_dist_traveled double precision NULL
);
CREATE INDEX ON stop_times(stop_id);
CREATE INDEX ON stop_times(trip_id, stop_sequence);
