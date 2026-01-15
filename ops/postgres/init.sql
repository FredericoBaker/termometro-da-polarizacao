CREATE SCHEMA IF NOT EXISTS termopol;

CREATE TABLE IF NOT EXISTS termopol.raw_parties (
    id INTEGER PRIMARY KEY,
    party_code TEXT NOT NULL,
    name TEXT NOT NULL,
    uri TEXT NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_deputies (
    id INTEGER PRIMARY KEY,
    uri TEXT NOT NULL,
    name TEXT NOT NULL,
    party_code TEXT NOT NULL,
    party_uri TEXT NOT NULL,
    state_code TEXT NOT NULL,
    legislature_id INTEGER NOT NULL,
    photo_url TEXT,
    email TEXT,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_votings (
    id TEXT PRIMARY KEY,
    uri TEXT NOT NULL,
    date DATE NOT NULL,
    registration_datetime TIMESTAMPTZ NOT NULL,
    organ_code TEXT,
    organ_uri TEXT,
    event_uri TEXT,
    proposition_subject TEXT,
    proposition_subject_uri TEXT,
    description TEXT,
    approval BOOLEAN,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_rollcalls (
    id SERIAL PRIMARY KEY,
    voting_id TEXT NOT NULL,
    voting_uri TEXT NOT NULL,
    voting_datetime TIMESTAMPTZ NOT NULL,
    vote TEXT NOT NULL,
    deputy_id INTEGER NOT NULL,
    deputy_uri TEXT NOT NULL,
    deputy_name TEXT NOT NULL,
    deputy_party_code TEXT NOT NULL,
    deputy_party_uri TEXT NOT NULL,
    deputy_state_code TEXT NOT NULL,
    deputy_legislature_id INTEGER NOT NULL,
    deputy_photo_url TEXT,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.parties (
    id SERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL UNIQUE,
    party_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    uri TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS termopol.deputies (
    id SERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    state_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS termopol.deputies_legislature_terms (
    id SERIAL PRIMARY KEY,
    deputy_id INTEGER NOT NULL REFERENCES termopol.deputies(id),
    legislature_id INTEGER NOT NULL,
    party_id INTEGER NOT NULL REFERENCES termopol.parties(id)
);

CREATE TABLE IF NOT EXISTS termopol.votings (
    id SERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,
    date DATE NOT NULL,
    registration_datetime TIMESTAMPTZ NOT NULL,
    approval BOOLEAN
);

CREATE TABLE IF NOT EXISTS termopol.rollcalls (
    id SERIAL PRIMARY KEY,
    voting_id INTEGER NOT NULL REFERENCES termopol.votings(id),
    voting_datetime TIMESTAMPTZ NOT NULL,
    vote TEXT NOT NULL,
    deputy_id INTEGER NOT NULL REFERENCES termopol.deputies(id),
    legislature_term_id INTEGER NOT NULL REFERENCES termopol.deputies_legislature_terms(id)
);

CREATE TABLE IF NOT EXISTS termopol.graph_time_granularities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

INSERT INTO termopol.graph_time_granularities (name) VALUES
  ('legislature'), ('year'), ('month')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS termopol.graph (
    id SERIAL PRIMARY KEY,
    time_granularity_id INTEGER NOT NULL REFERENCES termopol.graph_time_granularities(id),
    legislature INTEGER,
    year INTEGER,
    month DATE, -- First day of month
    UNIQUE (time_granularity_id, legislature, year, month),
    CHECK (
        (legislature IS NOT NULL AND year IS NULL AND month IS NULL)
        OR (legislature IS NULL AND year IS NOT NULL AND month IS NULL)
        OR (legislature IS NULL AND year IS NULL AND month IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS termopol.edges (
    graph_id INTEGER NOT NULL REFERENCES termopol.graph(id),
    deputy_a INTEGER NOT NULL REFERENCES termopol.deputies(id),
    deputy_b INTEGER NOT NULL REFERENCES termopol.deputies(id),
    w_signed INTEGER NOT NULL,
    abs_w INTEGER NOT NULL,
    alpha_deputy_a DOUBLE PRECISION,
    alpha_deputy_b DOUBLE PRECISION,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id, deputy_a, deputy_b),
    CHECK (deputy_a < deputy_b)
);

CREATE TABLE IF NOT EXISTS termopol.polarization_metrics (
    graph_id INTEGER NOT NULL REFERENCES termopol.graph(id),
    triads_total BIGINT NOT NULL,
    three_positive_triads BIGINT NOT NULL,
    two_positive_triads BIGINT NOT NULL,
    one_positive_triads BIGINT NOT NULL,
    zero_positive_triads BIGINT NOT NULL,
    polarization_index DOUBLE PRECISION NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id)
);

CREATE INDEX IF NOT EXISTS uq_raw_rollcalls_vote
    ON termopol.raw_rollcalls (voting_id, deputy_id);

CREATE INDEX IF NOT EXISTS idx_raw_votings_date
  ON termopol.raw_votings (date);

CREATE INDEX IF NOT EXISTS idx_votings_date
  ON termopol.votings (date);

CREATE INDEX IF NOT EXISTS idx_rollcalls_voting
  ON termopol.rollcalls (voting_id);

CREATE INDEX IF NOT EXISTS idx_terms_legislature
  ON termopol.deputies_legislature_terms (legislature_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph
  ON termopol.edges (graph_id);
