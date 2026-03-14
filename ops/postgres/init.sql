CREATE SCHEMA IF NOT EXISTS termopol;

CREATE TABLE IF NOT EXISTS termopol.ingestion_log (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    init_logic_ts TIMESTAMPTZ NOT NULL,
    end_logic_ts TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_parties (
    id INTEGER PRIMARY KEY,
    party_code TEXT NOT NULL,
    name TEXT NOT NULL,
    uri TEXT NOT NULL,
    transform_dirty BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_deputies (
    id INTEGER PRIMARY KEY,
    uri TEXT NOT NULL,
    name TEXT NOT NULL,
    party_code TEXT,
    party_uri TEXT,
    state_code TEXT NOT NULL,
    legislature_id INTEGER NOT NULL,
    photo_url TEXT,
    email TEXT,
    transform_dirty BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
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
    transform_dirty BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.raw_rollcalls (
    id SERIAL PRIMARY KEY,
    voting_id TEXT NOT NULL,
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
    transform_dirty BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (voting_id, deputy_id)
);

CREATE TABLE IF NOT EXISTS termopol.parties (
    id SERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL UNIQUE,
    party_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    uri TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.deputies (
    id SERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    state_code TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.deputies_legislature_terms (
    id SERIAL PRIMARY KEY,
    deputy_id INTEGER NOT NULL REFERENCES termopol.deputies(id),
    legislature_id INTEGER NOT NULL,
    party_id INTEGER NOT NULL REFERENCES termopol.parties(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (deputy_id, legislature_id)
);

CREATE TABLE IF NOT EXISTS termopol.votings (
    id SERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,
    date DATE NOT NULL,
    registration_datetime TIMESTAMPTZ NOT NULL,
    approval BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS termopol.rollcalls (
    id SERIAL PRIMARY KEY,
    voting_id INTEGER NOT NULL REFERENCES termopol.votings(id),
    voting_datetime TIMESTAMPTZ NOT NULL,
    vote INTEGER NOT NULL, -- 0 = Não, 1 = Sim -> Other possibilities are ignored
    deputy_id INTEGER NOT NULL REFERENCES termopol.deputies(id),
    legislature_term_id INTEGER NOT NULL REFERENCES termopol.deputies_legislature_terms(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(voting_id, deputy_id)
);

CREATE TABLE IF NOT EXISTS termopol.graph_time_granularities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

INSERT INTO termopol.graph_time_granularities (name) VALUES
  ('legislature'), ('year'), ('month')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS termopol.graphs (
    id SERIAL PRIMARY KEY,
    time_granularity_id INTEGER NOT NULL REFERENCES termopol.graph_time_granularities(id),
    legislature INTEGER,
    year INTEGER,
    month DATE, -- First day of month
    metrics_dirty BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (time_granularity_id, legislature, year, month),
    CHECK (
        (legislature IS NOT NULL AND year IS NULL AND month IS NULL)
        OR (legislature IS NULL AND year IS NOT NULL AND month IS NULL)
        OR (legislature IS NULL AND year IS NULL AND month IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS termopol.edges (
    graph_id INTEGER NOT NULL REFERENCES termopol.graphs(id),
    deputy_a INTEGER NOT NULL REFERENCES termopol.deputies(id),
    deputy_b INTEGER NOT NULL REFERENCES termopol.deputies(id),
    w_signed INTEGER NOT NULL,
    abs_w INTEGER NOT NULL,
    p_deputy_a DOUBLE PRECISION,
    p_deputy_b DOUBLE PRECISION,
    is_backbone BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id, deputy_a, deputy_b),
    CHECK (deputy_a < deputy_b)
);

CREATE TABLE IF NOT EXISTS termopol.polarization_metrics (
    graph_id INTEGER NOT NULL REFERENCES termopol.graphs(id),
    triads_total BIGINT NOT NULL,
    three_positive_triads BIGINT NOT NULL,
    two_positive_triads BIGINT NOT NULL,
    one_positive_triads BIGINT NOT NULL,
    zero_positive_triads BIGINT NOT NULL,
    polarization_index DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id)
);

CREATE TABLE IF NOT EXISTS termopol.graph_votings (
    graph_id INTEGER NOT NULL REFERENCES termopol.graphs(id),
    voting_id INTEGER NOT NULL REFERENCES termopol.votings(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id, voting_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_votings_date
  ON termopol.raw_votings (date);

CREATE INDEX IF NOT EXISTS idx_raw_parties_transform_dirty
  ON termopol.raw_parties (transform_dirty);

CREATE INDEX IF NOT EXISTS idx_raw_deputies_transform_dirty
  ON termopol.raw_deputies (transform_dirty);

CREATE INDEX IF NOT EXISTS idx_raw_votings_transform_dirty
  ON termopol.raw_votings (transform_dirty);

CREATE INDEX IF NOT EXISTS idx_raw_rollcalls_transform_dirty
  ON termopol.raw_rollcalls (transform_dirty);

CREATE INDEX IF NOT EXISTS idx_votings_date
  ON termopol.votings (date);

CREATE INDEX IF NOT EXISTS idx_rollcalls_voting
  ON termopol.rollcalls (voting_id);

CREATE INDEX IF NOT EXISTS idx_terms_legislature
  ON termopol.deputies_legislature_terms (legislature_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph
  ON termopol.edges (graph_id);

CREATE OR REPLACE FUNCTION termopol.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TRIGGER update_ingestion_log_modtime BEFORE UPDATE ON termopol.ingestion_log FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();

-- Triggers for Raw Tables
CREATE TRIGGER update_raw_parties_modtime BEFORE UPDATE ON termopol.raw_parties FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_raw_deputies_modtime BEFORE UPDATE ON termopol.raw_deputies FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_raw_votings_modtime BEFORE UPDATE ON termopol.raw_votings FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_raw_rollcalls_modtime BEFORE UPDATE ON termopol.raw_rollcalls FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();

-- Triggers for Normalized Tables
CREATE TRIGGER update_parties_modtime BEFORE UPDATE ON termopol.parties FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_deputies_modtime BEFORE UPDATE ON termopol.deputies FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_deputies_legislature_terms_modtime BEFORE UPDATE ON termopol.deputies_legislature_terms FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_votings_modtime BEFORE UPDATE ON termopol.votings FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_rollcalls_modtime BEFORE UPDATE ON termopol.rollcalls FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();

-- Triggers for Analytics/Graph Tables
CREATE TRIGGER update_graph_modtime BEFORE UPDATE ON termopol.graphs FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_edges_modtime BEFORE UPDATE ON termopol.edges FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
CREATE TRIGGER update_polarization_metrics_modtime BEFORE UPDATE ON termopol.polarization_metrics FOR EACH ROW EXECUTE FUNCTION termopol.update_updated_at_column();
