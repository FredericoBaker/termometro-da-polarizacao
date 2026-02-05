import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from pipeline.client.camara_client import CamaraClient

logger = logging.getLogger(__name__)


class BaseIngestor(ABC):
    MAX_DAYS_INTERVAL = 90

    def __init__(self, last_ingestion_date: Optional[datetime] = None):
        self.camara_client = CamaraClient()
        
        if last_ingestion_date is None:
            self.last_ingestion_date = datetime(datetime.now().year, 1, 1)
        else:
            self.last_ingestion_date = last_ingestion_date
        
        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={"last_ingestion_date": self.last_ingestion_date.isoformat()}
        )

    def ingest(self) -> None:
        current_date = datetime.now()
        start_date = self.last_ingestion_date
        
        logger.info(
            f"Starting {self.__class__.__name__} ingestion",
            extra={"start_date": start_date.isoformat(), "current_date": current_date.isoformat()}
        )
        
        total_items = 0
        while start_date < current_date:
            # Calculate end_date as start + 3 months
            end_date = start_date + timedelta(days=self.MAX_DAYS_INTERVAL)
            
            # If end_date crosses year boundary, truncate to 31/12 of current year
            if end_date.year > start_date.year:
                end_date = datetime(start_date.year, 12, 31)
            
            # Ensure we don't go beyond today
            if end_date > current_date:
                end_date = current_date
            
            logger.info(
                f"Ingesting {self.get_entity_name()} for period",
                extra={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days,
                    "year": start_date.year
                }
            )
            
            items_in_period = self._ingest_date_range(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            total_items += items_in_period
            
            # Move to next period (next day after end_date)
            start_date = end_date + timedelta(days=1)
        
        logger.info(
            f"Completed {self.__class__.__name__} ingestion",
            extra={"total_items_ingested": total_items}
        )

    def _ingest_date_range(self, start_date: str, end_date: str) -> int:
        """Ingest all pages for a date range. Returns number of items processed."""
        page = 1
        items_processed = 0
        
        while True:
            logger.debug(
                f"Fetching {self.get_entity_name()} page",
                extra={"start_date": start_date, "end_date": end_date, "page": page}
            )
            
            data = self.get_data_from_api(start_date, end_date, page)
            items = data.get("dados", [])
            
            if not items:
                logger.info(
                    f"No more {self.get_entity_name()} for date range",
                    extra={
                        "start_date": start_date,
                        "end_date": end_date,
                        "last_page": page - 1,
                        "total_items_in_range": items_processed
                    }
                )
                break

            for item in items:
                self.process_item(item)
                items_processed += 1

            logger.debug(
                f"Completed page for {self.get_entity_name()}",
                extra={
                    "page": page,
                    "items_on_page": len(items),
                    "total_so_far": items_processed
                }
            )
            page += 1
        
        return items_processed

    @abstractmethod
    def get_entity_name(self) -> str:
        pass

    @abstractmethod
    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def process_item(self, item: Dict[str, Any]) -> None:
        pass
