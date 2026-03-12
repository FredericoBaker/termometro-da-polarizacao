import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from termopol_db.repositories.base import BaseRepository
from termopol_db.queries import IngestionLogQueries

logger = logging.getLogger(__name__)


class IngestionLogRepository(BaseRepository):

    def insert_ingestion_log(
        self, 
        init_logic_ts: datetime = None,
        end_logic_ts: datetime = None
    ) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.insert_ingestion_log(self.schema)
        params = (init_logic_ts, end_logic_ts)
        logger.debug(
            "Inserting ingestion log"
        )
        return self._execute_query(query, params, fetch_one=True)

    def mark_in_progress(self, log_id: int) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.mark_in_progress(self.schema)
        params = (log_id,)
        logger.debug(
            "Marking ingestion log as in_progress",
            extra={"log_id": log_id}
        )
        return self._execute_query(query, params, fetch_one=True)

    def mark_completed(
        self,
        log_id: int
    ) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.mark_completed(self.schema)
        params = (log_id,)
        logger.debug(
            "Marking ingestion log as completed",
            extra={"log_id": log_id}
        )
        return self._execute_query(query, params, fetch_one=True)

    def mark_failed(
        self, 
        log_id: int, 
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.mark_failed(self.schema)
        now = datetime.utcnow()
        params = (error_message, log_id)
        logger.debug(
            "Marking ingestion log as failed",
            extra={"log_id": log_id, "error_message": error_message}
        )
        return self._execute_query(query, params, fetch_one=True)

    def get_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.get_ingestion_log_by_id(self.schema)
        return self._execute_query(query, (log_id,), fetch_one=True)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.get_latest_ingestion_log(self.schema)
        return self._execute_query(query, fetch_one=True)

    def get_last_completed(self) -> Optional[Dict[str, Any]]:
        query = IngestionLogQueries.get_last_completed(self.schema)
        return self._execute_query(query, fetch_one=True)

    def get_all(self) -> List[Dict[str, Any]]:
        query = IngestionLogQueries.get_all_ingestion_logs(self.schema)
        return self._execute_query(query, fetch_one=False)
