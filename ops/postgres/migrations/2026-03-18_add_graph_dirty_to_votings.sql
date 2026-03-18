BEGIN;

ALTER TABLE termopol.votings
    ADD COLUMN IF NOT EXISTS graph_dirty BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS idx_votings_graph_dirty
    ON termopol.votings (graph_dirty)
    WHERE graph_dirty = TRUE;

UPDATE termopol.votings v
SET graph_dirty = FALSE
WHERE v.id IN (
    SELECT DISTINCT gv.voting_id
    FROM termopol.graph_votings gv
);

COMMIT;
