BEGIN;

CREATE TEMP TABLE tmp_graph_duplicates (
    old_graph_id INTEGER PRIMARY KEY,
    new_graph_id INTEGER NOT NULL
) ON COMMIT DROP;

INSERT INTO tmp_graph_duplicates (old_graph_id, new_graph_id)
WITH ranked AS (
    SELECT
        g.id,
        MIN(g.id) OVER (
            PARTITION BY g.time_granularity_id, g.legislature, g.year, g.month
        ) AS keep_id,
        ROW_NUMBER() OVER (
            PARTITION BY g.time_granularity_id, g.legislature, g.year, g.month
            ORDER BY g.id
        ) AS rn
    FROM termopol.graphs g
)
SELECT id AS old_graph_id, keep_id AS new_graph_id
FROM ranked
WHERE rn > 1;

INSERT INTO termopol.graph_votings (graph_id, voting_id, created_at)
SELECT d.new_graph_id, gv.voting_id, gv.created_at
FROM termopol.graph_votings gv
JOIN tmp_graph_duplicates d
  ON d.old_graph_id = gv.graph_id
ON CONFLICT (graph_id, voting_id) DO NOTHING;

DELETE FROM termopol.graph_votings gv
USING tmp_graph_duplicates d
WHERE gv.graph_id = d.old_graph_id;

WITH merged_edges AS (
    SELECT
        d.new_graph_id AS graph_id,
        e.deputy_a,
        e.deputy_b,
        SUM(e.w_signed)::INTEGER AS w_signed,
        MIN(e.created_at) AS created_at,
        MAX(e.updated_at) AS updated_at
    FROM termopol.edges e
    JOIN tmp_graph_duplicates d
      ON d.old_graph_id = e.graph_id
    GROUP BY d.new_graph_id, e.deputy_a, e.deputy_b
)
INSERT INTO termopol.edges (
    graph_id, deputy_a, deputy_b, w_signed, abs_w,
    p_deputy_a, p_deputy_b, is_backbone, created_at, updated_at
)
SELECT
    m.graph_id,
    m.deputy_a,
    m.deputy_b,
    m.w_signed,
    ABS(m.w_signed),
    NULL,
    NULL,
    FALSE,
    m.created_at,
    m.updated_at
FROM merged_edges m
ON CONFLICT (graph_id, deputy_a, deputy_b) DO UPDATE
SET w_signed = termopol.edges.w_signed + EXCLUDED.w_signed,
    abs_w = ABS(termopol.edges.w_signed + EXCLUDED.w_signed),
    p_deputy_a = NULL,
    p_deputy_b = NULL,
    is_backbone = FALSE,
    updated_at = now();

DELETE FROM termopol.edges e
USING tmp_graph_duplicates d
WHERE e.graph_id = d.old_graph_id;

INSERT INTO termopol.nodes (graph_id, deputy_id, x, y, created_at, updated_at)
SELECT d.new_graph_id, n.deputy_id, n.x, n.y, n.created_at, n.updated_at
FROM termopol.nodes n
JOIN tmp_graph_duplicates d
  ON d.old_graph_id = n.graph_id
ON CONFLICT (graph_id, deputy_id) DO NOTHING;

DELETE FROM termopol.nodes n
USING tmp_graph_duplicates d
WHERE n.graph_id = d.old_graph_id;

DELETE FROM termopol.polarization_metrics pm
USING tmp_graph_duplicates d
WHERE pm.graph_id = d.old_graph_id
   OR pm.graph_id = d.new_graph_id;

UPDATE termopol.graphs g
SET metrics_dirty = TRUE,
    updated_at = now()
WHERE g.id IN (SELECT DISTINCT new_graph_id FROM tmp_graph_duplicates);

DELETE FROM termopol.graphs g
USING tmp_graph_duplicates d
WHERE g.id = d.old_graph_id;

ALTER TABLE termopol.graphs
DROP CONSTRAINT IF EXISTS graphs_time_granularity_id_legislature_year_month_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_graphs_legislature
ON termopol.graphs (time_granularity_id, legislature)
WHERE legislature IS NOT NULL AND year IS NULL AND month IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_graphs_year
ON termopol.graphs (time_granularity_id, year)
WHERE legislature IS NULL AND year IS NOT NULL AND month IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_graphs_month
ON termopol.graphs (time_granularity_id, month)
WHERE legislature IS NULL AND year IS NULL AND month IS NOT NULL;

COMMIT;
