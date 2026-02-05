
class IngestionLogQueries:

    @staticmethod
    def insert_ingestion_log(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.ingestion_log 
            (init_logic_ts, end_logic_ts)
            VALUES (%s, %s)
            RETURNING *;
        """

    @staticmethod
    def update_ingestion_log(schema: str) -> str:
        return f"""
            UPDATE {schema}.ingestion_log
            SET 
                status = %s,
                init_logic_ts = %s,
                end_logic_ts = %s,
                error_message = %s
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def mark_in_progress(schema: str) -> str:
        return f"""
            UPDATE {schema}.ingestion_log
            SET status = 'in_progress'
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def mark_completed(schema: str) -> str:
        return f"""
            UPDATE {schema}.ingestion_log
            SET 
                status = 'completed'
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def mark_failed(schema: str) -> str:
        return f"""
            UPDATE {schema}.ingestion_log
            SET 
                status = 'failed',
                error_message = %s
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def get_ingestion_log_by_id(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.ingestion_log
            WHERE id = %s;
        """

    @staticmethod
    def get_latest_ingestion_log(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.ingestion_log
            ORDER BY created_at DESC
            LIMIT 1;
        """

    @staticmethod
    def get_all_ingestion_logs(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.ingestion_log
            ORDER BY created_at DESC;
        """
