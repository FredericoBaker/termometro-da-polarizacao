import os

from termopol_db.repositories import RawPartyRepository, NormalizedPartyRepository


class PartyTransformer:
    def __init__(self):
        self.raw_party_repo = RawPartyRepository()
        self.party_repo = NormalizedPartyRepository()
        self.clear_batch_size = max(100, int(os.getenv("TRANSFORM_CLEAR_BATCH_SIZE", "1000")))

    def transform(self) -> None:
        """
            Transforms all newly ingested party data and upserts into normalized parties table.
        """
        dirty_ids_to_clear = []
        for party in self.raw_party_repo.get_dirty_parties_generator():
            self.party_repo.upsert_party(
                external_id=party.get('id'),
                party_code=party.get('party_code'),
                name=party.get('name'),
                uri=party.get('uri')
            )
            dirty_ids_to_clear.append(party.get('id'))
            if len(dirty_ids_to_clear) >= self.clear_batch_size:
                self.raw_party_repo.clear_parties_dirty_bulk(dirty_ids_to_clear)
                dirty_ids_to_clear = []

        if dirty_ids_to_clear:
            self.raw_party_repo.clear_parties_dirty_bulk(dirty_ids_to_clear)
