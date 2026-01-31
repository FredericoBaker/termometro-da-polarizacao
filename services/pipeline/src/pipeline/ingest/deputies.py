import logging
from datetime import datetime
from typing import Optional, Dict, Any

from base import BaseIngestor
from termopol_db.repositories import RawDeputyRepository

logger = logging.getLogger(__name__)


class DeputiesIngestor(BaseIngestor):
    def __init__(self, last_ingestion_date: Optional[datetime] = None):
        super().__init__(last_ingestion_date)
        self.deputy_repo = RawDeputyRepository()

    def get_entity_name(self) -> str:
        return "deputies"

    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        return self.camara_client.get_deputies(start_date, end_date, page=page)

    def process_item(self, deputy: Dict[str, Any]) -> None:
        try:
            self.deputy_repo.upsert_deputy({
                'id': deputy.get('id'),
                'uri': deputy.get('uri'),
                'name': deputy.get('nome'),
                'party_code': deputy.get('siglaPartido'),
                'party_uri': deputy.get('uriPartido'),
                'state_code': deputy.get('siglaUf'),
                'legislature_id': deputy.get('idLegislatura'),
                'photo_url': deputy.get('urlFoto'),
                'email': deputy.get('email'),
                'payload': deputy,
            })
            
            logger.debug(
                "Deputy processed successfully",
                extra={"deputy_id": deputy.get('id'), "deputy_name": deputy.get('nome')}
            )

        except Exception as e:
            logger.error(
                "Failed to process deputy",
                extra={"deputy_id": deputy.get('id'), "deputy_name": deputy.get('nome')},
                exc_info=True
            )
            raise
