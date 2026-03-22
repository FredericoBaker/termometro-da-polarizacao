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
        return {
            "last_updated_at": log.get("end_logic_ts") or log.get("created_at"),
        }
