import logging
from datetime import datetime
from typing import Optional, Dict, Any
from http import HTTPStatus
import requests

from pipeline.ingest.base import BaseIngestor
from termopol_db.repositories import RawVotingRepository, RawRollcallRepository

logger = logging.getLogger(__name__)


class VotingsIngestor(BaseIngestor):
    """
    Ingest votings and their respective rollcalls from Câmara API.
    """

    def __init__(
        self,
        last_ingestion_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        super().__init__(
            last_ingestion_date=last_ingestion_date,
            end_date=end_date,
            non_fatal_http_status_codes={int(HTTPStatus.GATEWAY_TIMEOUT)},
        )
        self.voting_repo = RawVotingRepository()
        self.rollcall_repo = RawRollcallRepository()

    def get_entity_name(self) -> str:
        return "votings"

    def get_data_from_api(self, start_date: str, end_date: str, page: int) -> Dict[str, Any]:
        return self.camara_client.get_votings(start_date, end_date, page=page)

    def process_item(self, voting: Dict[str, Any]) -> None:
        voting_id = voting.get('id')
        voting_date = voting.get('data')
        registration_datetime = voting.get('dataHoraRegistro')

        if not registration_datetime and voting_date:
            registration_datetime = f"{voting_date}T00:00:00"
            logger.warning(
                "Voting missing registration_datetime; using date fallback at midnight",
                extra={"voting_id": voting_id, "voting_date": voting_date},
            )
        elif not registration_datetime and not voting_date:
            logger.warning(
                "Skipping voting with missing date and registration_datetime",
                extra={"voting_id": voting_id},
            )
            return
        
        try:
            self.voting_repo.upsert_voting({
                'id': voting_id,
                'uri': voting.get('uri'),
                'date': voting_date,
                'registration_datetime': registration_datetime,
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
                extra={"voting_id": voting_id, "voting_date": voting_date}
            )
            
            # Now fetch and process rollcalls for this voting
            self._process_rollcalls_for_voting(voting_id)

        except Exception as e:
            logger.error(
                "Failed to process voting",
                extra={"voting_id": voting_id, "voting_date": voting_date},
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

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.GATEWAY_TIMEOUT):
                logger.warning(
                    "Skipping voting rollcalls after HTTP error",
                    extra={"voting_id": voting_id, "status_code": status_code},
                )
                return
            logger.error(
                "Failed to fetch/process rollcalls for voting due to HTTP error",
                extra={"voting_id": voting_id, "status_code": status_code},
                exc_info=True
            )
            raise
                
        except Exception as e:
            logger.error(
                "Failed to fetch/process rollcalls for voting",
                extra={"voting_id": voting_id},
                exc_info=True
            )
            raise

    def _process_rollcall(self, voting_id: int, rollcall: Dict[str, Any]) -> None:
        deputy_info = rollcall.get('deputado_')
        deputy_id = deputy_info.get('id') if isinstance(deputy_info, dict) else None
        vote = rollcall.get('tipoVoto')

        try:
            if not isinstance(deputy_info, dict) or deputy_id is None:
                logger.warning(
                    "Skipping rollcall with invalid deputy payload",
                    extra={"voting_id": voting_id, "rollcall_vote": rollcall.get('tipoVoto')},
                )
                return

            if vote is None or (isinstance(vote, str) and not vote.strip()):
                logger.warning(
                    "Skipping rollcall with null/empty vote",
                    extra={"voting_id": voting_id, "deputy_id": deputy_id},
                )
                return

            self.rollcall_repo.upsert_rollcall({
                'voting_id': voting_id,
                'voting_datetime': rollcall.get('dataRegistroVoto'),
                'vote': vote,
                'deputy_id': deputy_info.get('id'),
                'deputy_name': deputy_info.get('nome'),
                'deputy_party_code': deputy_info.get('siglaPartido'),
                'deputy_state_code': deputy_info.get('siglaUf'),
                'deputy_legislature_id': deputy_info.get('idLegislatura'),
            })
            
            logger.debug(
                "Rollcall processed successfully",
                extra={"voting_id": voting_id, "deputy_id": deputy_id, "vote": vote}
            )
            
        except Exception:
            logger.error(
                "Failed to process rollcall",
                extra={"voting_id": voting_id, "deputy_id": deputy_id},
                exc_info=True
            )
            raise
