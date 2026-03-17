from termopol_db.connection import DatabaseConnectionPool


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
