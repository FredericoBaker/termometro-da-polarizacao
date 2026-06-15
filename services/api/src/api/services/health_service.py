from termopol_db.connection import DatabaseConnectionPool
from termopol_db.repositories.ingestion_log import IngestionLogRepository


class HealthService:
    def __init__(self, db_pool: DatabaseConnectionPool) -> None:
        self.db_pool = db_pool

    def health_check(self) -> dict:
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            db_status = "ok"
        except Exception as exc:
            db_status = f"error: {str(exc)}"

        return {
            "status": "ok",
            "database": db_status,
        }

    def get_last_update(self) -> dict:
        repo = IngestionLogRepository()
        log = repo.get_last_completed()
        if not log:
            return {"last_updated_at": None}
        # Use updated_at (when the run was marked completed) — the real
        # wall-clock finish time. end_logic_ts is the logical window boundary,
        # which is always the scheduled trigger instant (03:00 UTC) and thus
        # would render as a constant midnight in Brasília time.
        return {
            "last_updated_at": (
                log.get("updated_at")
                or log.get("end_logic_ts")
                or log.get("created_at")
            ),
        }
