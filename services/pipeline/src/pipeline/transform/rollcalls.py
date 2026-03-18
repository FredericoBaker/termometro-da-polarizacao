import os

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
        self.batch_size = max(100, int(os.getenv("TRANSFORM_ROLLCALL_BATCH_SIZE", "1000")))
        self.upsert_page_size = max(500, int(os.getenv("TRANSFORM_ROLLCALL_UPSERT_PAGE_SIZE", "5000")))

    def transform(self) -> None:
        """
            Transforms all newly ingested rollcall data and upserts into normalized rollcalls table.

            Important: Deputies, votings and parties must be transformed before rollcalls.
        """
        batch = []
        for rollcall in self.raw_rollcall_repo.get_dirty_rollcalls_generator():
            batch.append(rollcall)
            if len(batch) >= self.batch_size:
                self._process_batch(batch)
                batch = []

        if batch:
            self._process_batch(batch)

    def _process_batch(self, raw_rollcalls: list[dict]) -> None:
        if not raw_rollcalls:
            return

        candidate_rows = []
        for raw_rollcall in raw_rollcalls:
            vote = self._process_vote_value(raw_rollcall.get('vote'))
            if vote == -1:
                continue
            candidate_rows.append((raw_rollcall, vote))

        if not candidate_rows:
            return

        external_voting_ids = sorted({str(row[0].get('voting_id')) for row in candidate_rows})
        external_deputy_ids = sorted({row[0].get('deputy_id') for row in candidate_rows if row[0].get('deputy_id') is not None})
        party_codes = sorted({row[0].get('deputy_party_code') for row in candidate_rows if row[0].get('deputy_party_code')})

        votings = self.votings_repo.get_votings_by_external_ids(external_voting_ids)
        deputies = self.deputies_repo.get_deputies_by_external_ids(external_deputy_ids)
        parties = self.parties_repo.get_parties_by_codes(party_codes)

        voting_by_external_id = {str(v.get('external_id')): v for v in votings}
        deputy_by_external_id = {d.get('external_id'): d for d in deputies}
        party_by_code = {p.get('party_code'): p for p in parties}

        pair_candidates = []
        for raw_rollcall, _ in candidate_rows:
            deputy = deputy_by_external_id.get(raw_rollcall.get('deputy_id'))
            if not deputy:
                continue
            legislature = raw_rollcall.get('deputy_legislature_id')
            if legislature is None:
                continue
            pair_candidates.append((deputy.get('id'), legislature))
        unique_pairs = list(dict.fromkeys(pair_candidates))

        term_rows = self.deputies_repo.get_deputy_legislature_terms_by_pairs(unique_pairs)
        term_by_pair = {(t.get('deputy_id'), t.get('legislature_id')): t for t in term_rows}

        rows_to_upsert = []
        dirty_ids_to_clear = []

        for raw_rollcall, vote in candidate_rows:
            voting = voting_by_external_id.get(str(raw_rollcall.get('voting_id')))
            if not voting:
                continue

            deputy = deputy_by_external_id.get(raw_rollcall.get('deputy_id'))
            if not deputy:
                continue

            party = party_by_code.get(raw_rollcall.get('deputy_party_code'))
            if not party:
                continue

            legislature = raw_rollcall.get('deputy_legislature_id')
            if legislature is None:
                continue

            pair_key = (deputy.get('id'), legislature)
            legislature_term = term_by_pair.get(pair_key)
            if not legislature_term:
                legislature_term = self.deputies_repo.upsert_deputy_legislature_term(
                    deputy_id=deputy.get('id'),
                    party_id=party.get('id'),
                    legislature=legislature
                )
                if not legislature_term:
                    continue
                term_by_pair[pair_key] = legislature_term

            rows_to_upsert.append(
                (
                    voting.get('id'),
                    raw_rollcall.get('voting_datetime'),
                    vote,
                    deputy.get('id'),
                    legislature_term.get('id')
                )
            )
            dirty_ids_to_clear.append(raw_rollcall.get('id'))

        if rows_to_upsert:
            self.rollcall_repo.bulk_upsert_rollcalls(rows_to_upsert, page_size=self.upsert_page_size)
        if dirty_ids_to_clear:
            self.raw_rollcall_repo.clear_rollcalls_dirty_bulk(dirty_ids_to_clear)

    def _process_vote_value(self, vote_str: str) -> int:
        vote_mapping = {
            'Sim': 1,
            'Não': 0
        }
        return vote_mapping.get(vote_str, -1)
        