import logging

from termopol_db.repositories import RawDeputyRepository, NormalizedDeputyRepository

logger = logging.getLogger(__name__)


class DeputyTransformer:
    def __init__(self):
        self.raw_deputy_repo = RawDeputyRepository()
        self.deputy_repo = NormalizedDeputyRepository()

    def transform(self) -> None:
        """
            Transforms all newly ingested deputy data and upserts into normalized deputies table.
        """
        for deputy in self.raw_deputy_repo.get_dirty_deputies_generator():
            if not deputy.get('name'):
                logger.warning(
                    "Skipping normalized deputy upsert with null/empty name",
                    extra={
                        "raw_deputy_id": deputy.get('id'),
                        "party_code": deputy.get('party_code'),
                        "party_uri": deputy.get('party_uri'),
                    },
                )
                self.raw_deputy_repo.clear_deputy_dirty(deputy.get('id'))
                continue
            self.deputy_repo.upsert_deputy(
                external_id=deputy.get('id'),
                name=deputy.get('name'),
                state_code=deputy.get('state_code')
            )
            self.raw_deputy_repo.clear_deputy_dirty(deputy.get('id'))
