DROP INDEX CONCURRENTLY IF EXISTS termopol.idx_edges_graph;

ALTER TABLE termopol.edges
SET (
  autovacuum_enabled = true,
  autovacuum_vacuum_scale_factor = 0.005,
  autovacuum_analyze_scale_factor = 0.005,
  autovacuum_vacuum_threshold = 2000,
  autovacuum_analyze_threshold = 2000,
  fillfactor = 75
);
