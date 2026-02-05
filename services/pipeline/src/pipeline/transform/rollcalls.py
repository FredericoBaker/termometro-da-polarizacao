from datetime import datetime
from typing import Optional

from termopol_db.repositories import (
    RawRollcallRepository,
    NormalizedRollcallRepository,
    NormalizedDeputyRepository,
    NormalizedVotingRepository,
    NormalizedPartyRepository,
)


class RollCallTransformer:
    def __init__(self):
        self.raw_rollcall_repo = RawRollcallRepository()
        self.rollcall_repo = NormalizedRollcallRepository()

        self.deputies_repo = NormalizedDeputyRepository()
        self.votings_repo = NormalizedVotingRepository()
        self.parties_repo = NormalizedPartyRepository()

    def transform(self, start_date: datetime, end_date: datetime) -> None:
        """
            Transforms all newly ingested rollcall data and upserts into normalized rollcalls table.

            Important: Deputies, votings and parties must be transformed before rollcalls.
        """
        for rollcall in self.raw_rollcall_repo.get_rollcalls_by_date_range_generator(
            start_date=start_date,
            end_date=end_date
        ):
            transformed_rollcall = self._transform_rollcall(rollcall)
            if transformed_rollcall:
                self.rollcall_repo.upsert_rollcall(
                    voting_id = transformed_rollcall.get('voting_id'),
                    voting_datetime = transformed_rollcall.get('voting_datetime'),
                    vote = transformed_rollcall.get('vote'),
                    deputy_id = transformed_rollcall.get('deputy_id'),
                    legislature_term_id = transformed_rollcall.get('legislature_term_id')
                )

    def _transform_rollcall(self, raw_rollcall: dict) -> Optional[dict]:
        """
            Transforms a raw rollcall record into normalized format.
        """
        vote = self._process_vote_value(raw_rollcall.get('vote'))
        if vote == -1:
            # Ignore votes that are not 'Sim' or 'Não'
            return None
        
        voting = self.votings_repo.get_voting_by_external_id(
            external_id=raw_rollcall.get('voting_id')
        )
        if not voting:
            return None

        deputy = self.deputies_repo.get_deputy_by_external_id(
            external_id=raw_rollcall.get('deputy_id')
        )
        if not deputy:
            return None

        party = self.parties_repo.get_party_by_code(
            party_code=raw_rollcall.get('deputy_party_code')
        )
        if not party:
            return None
        
        legislature_term = self._get_legislature_term(deputy.get('id'), party.get('id'), raw_rollcall.get('deputy_legislature_id'))
        if not legislature_term:
            return None

        transformed = {
            'voting_id': voting.get('id'),
            'voting_datetime': raw_rollcall.get('voting_datetime'),
            'vote': vote,
            'deputy_id': deputy.get('id'),
            'legislature_term_id': legislature_term.get('id')
        }
        return transformed
    
    def _get_legislature_term(self, deputy_id: int, party_id: int, legislature: int) -> Optional[dict]:
        legislature_term = self.deputies_repo.get_deputy_legislature_term(deputy_id, legislature)

        if legislature_term:
            return legislature_term
        
        legislature_term = self.deputies_repo.upsert_deputy_legislature_term(
            deputy_id=deputy_id,
            party_id=party_id,
            legislature=legislature
        )
        return legislature_term
    
    def _process_vote_value(self, vote_str: str) -> int:
        vote_mapping = {
            'Sim': 1,
            'Não': 0
        }
        return vote_mapping.get(vote_str, -1)
        