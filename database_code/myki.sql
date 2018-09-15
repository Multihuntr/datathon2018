DROP TABLE IF EXISTS journey_leg CASCADE;
DROP TABLE IF EXISTS journey CASCADE;

CREATE TABLE journey
(
	journey_id       BIGSERIAL PRIMARY KEY
);

CREATE TABLE journey_leg
(
  journey_id       bigint NOT NULL references journey(journey_id),
  leg_seq          int NOT NULL,
  first_last       boolean NOT NULL,
  trip_id          text NOT NULL,
  start_stop_id    int NOT NULL references stops(stop_id),
  end_stop_id      int NOT NULL references stops(stop_id),
  start_trip_seq   int NOT NULL,
  end_trip_seq     int NOT NULL,
  leg_time         real NOT NULL
);

CREATE INDEX ON journey_leg(start_stop_id);
CREATE INDEX ON journey_leg(end_stop_id);
CREATE INDEX ON journey_leg(journey_id);