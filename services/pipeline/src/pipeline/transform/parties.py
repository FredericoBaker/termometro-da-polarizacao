from datetime import datetime

from termopol_db.repositories import RawPartyRepository, NormalizedPartyRepository


class PartyTransformer:
    def __init__(self):
        self.raw_party_repo = RawPartyRepository()
        self.party_repo = NormalizedPartyRepository()

    def transform(self, start_date: datetime, end_date: datetime) -> None:
        """
            Transforms all newly ingested party data and upserts into normalized parties table.
        """
        for party in self.raw_party_repo.get_dirty_parties_generator():
            self.party_repo.upsert_party(
                external_id=party.get('id'),
                party_code=party.get('party_code'),
                name=party.get('name'),
                uri=party.get('uri')
            )
            self.raw_party_repo.clear_party_dirty(party.get('id'))
