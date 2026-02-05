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
        for party in self.raw_party_repo.get_parties_by_date_range_generator(
            start_date=start_date,
            end_date=end_date
        ):
            self.party_repo.upsert_party(
                external_id=party.get('id'),
                party_code=party.get('party_code'),
                name=party.get('name'),
                uri=party.get('uri')
            )
