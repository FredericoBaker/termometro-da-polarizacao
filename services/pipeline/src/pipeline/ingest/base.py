import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import requests

from pipeline.client.camara_client import CamaraClient
from pipeline.config.loader import get

logger = logging.getLogger(__name__)


class BaseIngestor(ABC):
    MAX_DAYS_INTERVAL = 90

    def __init__(
        self,
        last_ingestion_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        non_fatal_http_status_codes: Optional[set[int]] = None,
        process_workers: Optional[int] = None,
    ):
        self.camara_client = CamaraClient()
        self.non_fatal_http_status_codes = set(non_fatal_http_status_codes or [])
        self.end_date = end_date
        configured_workers = int(get("ingest", "process_workers", default=1))
        self.process_workers = max(1, int(process_workers or configured_workers))
        
        if last_ingestion_date is None:
            self.last_ingestion_date = datetime(datetime.now().year, 1, 1)
        else:
            self.last_ingestion_date = last_ingestion_date
        
        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={
                "last_ingestion_date": self.last_ingestion_date.isoformat(),
                "end_date": self.end_date.isoformat() if self.end_date else None,
                "non_fatal_http_status_codes": sorted(self.non_fatal_http_status_codes),
                "process_workers": self.process_workers,
            }
        )

    def _is_non_fatal_http_error(self, exc: requests.exceptions.HTTPError) -> bool:
        status_code = exc.response.status_code if exc.response is not None else None
        return status_code in self.non_fatal_http_status_codes

    def ingest(self) -> None:
        current_date = self.end_date or datetime.now()
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

            try:
                data = self.get_data_from_api(start_date, end_date, page)
            except requests.exceptions.HTTPError as exc:
                status_code = exc.response.status_code if exc.response is not None else None
                if self._is_non_fatal_http_error(exc):
                    logger.warning(
                        "Skipping page after non-fatal HTTP error",
                        extra={
                            "entity": self.get_entity_name(),
                            "start_date": start_date,
                            "end_date": end_date,
                            "page": page,
                            "status_code": status_code,
                        },
                    )
                    page += 1
                    continue
                raise

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

            if self.process_workers == 1:
                for item in items:
                    try:
                        self.process_item(item)
                    except requests.exceptions.HTTPError as exc:
                        status_code = exc.response.status_code if exc.response is not None else None
                        if self._is_non_fatal_http_error(exc):
                            logger.warning(
                                "Skipping item after non-fatal HTTP error",
                                extra={
                                    "entity": self.get_entity_name(),
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "page": page,
                                    "status_code": status_code,
                                },
                            )
                            continue
                        raise
                    items_processed += 1
            else:
                with ThreadPoolExecutor(max_workers=self.process_workers) as executor:
                    futures = [executor.submit(self.process_item, item) for item in items]
                    for future in as_completed(futures):
                        try:
                            future.result()
                            items_processed += 1
                        except requests.exceptions.HTTPError as exc:
                            status_code = exc.response.status_code if exc.response is not None else None
                            if self._is_non_fatal_http_error(exc):
                                logger.warning(
                                    "Skipping item after non-fatal HTTP error",
                                    extra={
                                        "entity": self.get_entity_name(),
                                        "start_date": start_date,
                                        "end_date": end_date,
                                        "page": page,
                                        "status_code": status_code,
                                    },
                                )
                                continue
                            raise

            logger.debug(
                f"Completed page for {self.get_entity_name()}",
                extra={
                    "page": page,
                    "items_on_page": len(items),
                    "total_so_far": items_processed,
                    "process_workers": self.process_workers,
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
