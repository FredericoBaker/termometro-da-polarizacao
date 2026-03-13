import logging
from datetime import datetime
from typing import Optional, Dict, Any

from pipeline.ingest.base import BaseIngestor
from termopol_db.repositories import RawDeputyRepository

logger = logging.getLogger(__name__)


class DeputiesIngestor(BaseIngestor):
    def __init__(
        self,
        last_ingestion_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        super().__init__(last_ingestion_date=last_ingestion_date, end_date=end_date)
        self.deputy_repo = RawDeputyRepository()

    def get_entity_name(self) -> str:
        return "deputies"

    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        return self.camara_client.get_deputies(start_date, end_date, page=page)

    def process_item(self, deputy: Dict[str, Any]) -> None:
        deputy_id = deputy.get('id')
        deputy_name = deputy.get('nome')
        if not deputy_name:
            logger.warning(
                "Skipping deputy with null/empty name",
                extra={
                    "deputy_id": deputy_id,
                    "party_code": deputy.get('siglaPartido'),
                    "party_uri": deputy.get('uriPartido'),
                },
            )
            return

        try:
            self.deputy_repo.upsert_deputy({
                'id': deputy_id,
                'uri': deputy.get('uri'),
                'name': deputy_name,
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
                extra={"deputy_id": deputy_id, "deputy_name": deputy_name}
            )

        except Exception:
            logger.error(
                "Failed to process deputy",
                extra={"deputy_id": deputy_id, "deputy_name": deputy_name},
                exc_info=True
            )
            raise
