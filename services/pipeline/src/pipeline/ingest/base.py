import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from pipeline.client.camara_client import CamaraClient

logger = logging.getLogger(__name__)


class BaseIngestor(ABC):

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
        current_year = datetime.now().year
        start_year = self.last_ingestion_date.year
        
        logger.info(
            f"Starting {self.__class__.__name__} ingestion",
            extra={"start_year": start_year, "current_year": current_year}
        )
        
        for year in range(start_year, current_year + 1):
            # Define start_date for this year
            if year == start_year:
                start_date = self.last_ingestion_date
            else:
                start_date = datetime(year, 1, 1)
            
            # End date is always 31/12 of the year
            end_date = datetime(year, 12, 31)
            
            logger.info(
                f"Ingesting {self.get_entity_name()} for year",
                extra={
                    "year": year,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            self._ingest_date_range(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

    def _ingest_date_range(self, start_date: str, end_date: str) -> None:
        page = 1
        
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
                    extra={"start_date": start_date, "end_date": end_date, "page": page}
                )
                break

            for item in items:
                self.process_item(item)

            page += 1

    @abstractmethod
    def get_entity_name(self) -> str:
        pass

    @abstractmethod
    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def process_item(self, item: Dict[str, Any]) -> None:
        pass
