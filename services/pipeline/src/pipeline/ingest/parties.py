import logging
from datetime import datetime
from typing import Optional, Dict, Any

from pipeline.ingest.base import BaseIngestor
from termopol_db.repositories import RawPartyRepository

logger = logging.getLogger(__name__)


class PartiesIngestor(BaseIngestor):

    def __init__(self, last_ingestion_date: Optional[datetime] = None):
        super().__init__(last_ingestion_date)
        self.party_repo = RawPartyRepository()

    def get_entity_name(self) -> str:
        return "parties"

    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        return self.camara_client.get_parties(start_date, end_date, page=page)

    def process_item(self, party: Dict[str, Any]) -> None:
        try:
            self.party_repo.upsert_party({
                'id': party.get('id'),
                'name': party.get('nome'),
                'party_code': party.get('sigla'),
                'uri': party.get('uri'),
                'payload': party,
            })
            
            logger.debug(
                "Party processed successfully",
                extra={"party_id": party.get('id'), "party_code": party.get('sigla')}
            )

        except Exception as e:
            logger.error(
                "Failed to process party",
                extra={"party_id": party.get('id'), "party_code": party.get('sigla')},
                exc_info=True
            )
            raise

