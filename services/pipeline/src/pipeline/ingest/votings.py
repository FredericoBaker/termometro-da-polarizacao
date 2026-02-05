import logging
from datetime import datetime
from typing import Optional, Dict, Any

from pipeline.ingest.base import BaseIngestor
from termopol_db.repositories import RawVotingRepository, RawRollcallRepository

logger = logging.getLogger(__name__)


class VotingsIngestor(BaseIngestor):
    """
    Ingest votings and their respective rollcalls from Câmara API.
    """

    def __init__(self, last_ingestion_date: Optional[datetime] = None):
        super().__init__(last_ingestion_date)
        self.voting_repo = RawVotingRepository()
        self.rollcall_repo = RawRollcallRepository()

    def get_entity_name(self) -> str:
        return "votings"

    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        return self.camara_client.get_votings(start_date, end_date, page=page)

    def process_item(self, voting: Dict[str, Any]) -> None:
        voting_id = voting.get('id')
        
        try:
            self.voting_repo.upsert_voting({
                'id': voting_id,
                'uri': voting.get('uri'),
                'date': voting.get('data'),
                'registration_datetime': voting.get('dataHoraRegistro'),
                'organ_code': voting.get('siglaOrgao'),
                'organ_uri': voting.get('uriOrgao'),
                'event_uri': voting.get('uriEvento'),
                'proposition_subject': voting.get('proposicaoObjeto'),
                'proposition_subject_uri': voting.get('uriProposicaoObjeto'),
                'description': voting.get('descricao'),
                'approval': voting.get('aprovacao'),
                'payload': voting,
            })
            
            logger.debug(
                "Voting processed successfully",
                extra={"voting_id": voting_id, "voting_date": voting.get('data')}
            )
            
            # Now fetch and process rollcalls for this voting
            self._process_rollcalls_for_voting(voting_id)

        except Exception as e:
            logger.error(
                "Failed to process voting",
                extra={"voting_id": voting_id, "voting_date": voting.get('data')},
                exc_info=True
            )
            raise

    def _process_rollcalls_for_voting(self, voting_id: int) -> None:
        try:
            logger.debug("Fetching rollcalls", extra={"voting_id": voting_id})
            
            rollcalls_data = self.camara_client.get_rollcalls(voting_id)
            rollcalls = rollcalls_data.get("dados", [])
            
            if not rollcalls:
                return
            
            logger.info(
                "Processing rollcalls for voting",
                extra={"voting_id": voting_id, "rollcall_count": len(rollcalls)}
            )
            
            for rollcall in rollcalls:
                self._process_rollcall(voting_id, rollcall)
                
        except Exception as e:
            logger.error(
                "Failed to fetch/process rollcalls for voting",
                extra={"voting_id": voting_id},
                exc_info=True
            )
            raise

    def _process_rollcall(self, voting_id: int, rollcall: Dict[str, Any]) -> None:
        try:
            deputy = rollcall.get('deputado_')

            self.rollcall_repo.upsert_rollcall({
                'voting_id': voting_id,
                'voting_datetime': rollcall.get('dataRegistroVoto'),
                'vote': rollcall.get('tipoVoto'),
                'deputy_id': deputy.get('id'),
                'deputy_uri': deputy.get('uri'),
                'deputy_name': deputy.get('nome'),
                'deputy_party_code': deputy.get('siglaPartido'),
                'deputy_party_uri': deputy.get('uriPartido'),
                'deputy_state_code': deputy.get('siglaUf'),
                'deputy_legislature_id': deputy.get('idLegislatura'),
                'deputy_photo_url': deputy.get('urlFoto'),
                'payload': rollcall,
            })
            
            logger.debug(
                "Rollcall processed successfully",
                extra={"voting_id": voting_id, "deputy_id": deputy.get('id'), "vote": rollcall.get('tipoVoto')}
            )
            
        except Exception as e:
            logger.error(
                "Failed to process rollcall",
                extra={"voting_id": voting_id, "deputy_id": rollcall.get('deputado_').get('id')},
                exc_info=True
            )
            raise
