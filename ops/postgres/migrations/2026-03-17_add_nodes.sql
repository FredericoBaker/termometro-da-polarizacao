BEGIN;

CREATE SCHEMA IF NOT EXISTS termopol;

CREATE TABLE IF NOT EXISTS termopol.nodes (
    graph_id INTEGER NOT NULL REFERENCES termopol.graphs(id),
    deputy_id INTEGER NOT NULL REFERENCES termopol.deputies(id),
    x DOUBLE PRECISION,
    y DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (graph_id, deputy_id)
);

ALTER TABLE termopol.nodes
    ADD COLUMN IF NOT EXISTS x DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS y DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE c.conname = 'nodes_pkey'
          AND n.nspname = 'termopol'
    ) THEN
        ALTER TABLE termopol.nodes
            ADD CONSTRAINT nodes_pkey PRIMARY KEY (graph_id, deputy_id);
    END IF;
END
$$;

CREATE OR REPLACE FUNCTION termopol.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_nodes_modtime
BEFORE UPDATE ON termopol.nodes
FOR EACH ROW
EXECUTE FUNCTION termopol.update_updated_at_column();

COMMIT;
