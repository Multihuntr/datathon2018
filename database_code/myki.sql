DROP TABLE IF EXISTS journey CASCADE;
DROP TABLE IF EXISTS journey_leg CASCADE;

CREATE TABLE journey
(
	journey_id       BIGSERIAL PRIMARY KEY
);

CREATE TABLE journey_leg
(
  journey_id       bigint NOT NULL references journey(journey_id),
  trip_id          text NOT NULL,
  start_stop_id    int NOT NULL,
  end_stop_id      int NOT NULL,
  journey_time     int NOT NULL
);

CREATE INDEX ON journey_leg(start_stop_id);
CREATE INDEX ON journey_leg(end_stop_id);
CREATE INDEX ON journey_leg(journey_id);