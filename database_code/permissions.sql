ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO loader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO loader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO loader;
GRANT ALL PRIVILEGES ON TABLE journey TO loader;
GRANT USAGE,SELECT ON SEQUENCE journey_journey_id_seq TO loader;
GRANT ALL PRIVILEGES ON TABLE journey_leg TO loader;
