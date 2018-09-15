\copy agency from './agency.txt' with csv header




CREATE TEMP TABLE tmp_table AS
SELECT * FROM calendar
WITH NO DATA;

\copy tmp_table from './calendar.txt' with csv header

INSERT INTO calendar
SELECT DISTINCT ON (service_id) *
FROM tmp_table
ON CONFLICT DO NOTHING;
DROP TABLE tmp_table;



CREATE TEMP TABLE tmp_table AS
SELECT * FROM stops
WITH NO DATA;

\copy tmp_table from './stops.txt' with csv header

INSERT INTO stops
SELECT DISTINCT ON (stop_id) *
FROM tmp_table
ON CONFLICT DO NOTHING;

DROP TABLE tmp_table;




\copy routes from './routes.txt' with csv header
\copy shapes from './shapes.txt' with csv header
\copy trips from './trips.txt' with csv header
\copy stop_times from './stop_times.txt' with csv header
