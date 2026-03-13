import logging
from datetime import datetime

from termopol_db.repositories import RawDeputyRepository, NormalizedDeputyRepository

logger = logging.getLogger(__name__)


class DeputyTransformer:
    def __init__(self):
        self.raw_deputy_repo = RawDeputyRepository()
        self.deputy_repo = NormalizedDeputyRepository()

    def transform(self, start_date: datetime, end_date: datetime) -> None:
        """
            Transforms all newly ingested deputy data and upserts into normalized deputies table.
        """
        for deputy in self.raw_deputy_repo.get_deputies_by_date_range_generator(
            start_date=start_date,
            end_date=end_date
        ):
            if not deputy.get('name'):
                logger.warning(
                    "Skipping normalized deputy upsert with null/empty name",
                    extra={
                        "raw_deputy_id": deputy.get('id'),
                        "party_code": deputy.get('party_code'),
                        "party_uri": deputy.get('party_uri'),
                    },
                )
                continue
            self.deputy_repo.upsert_deputy(
                external_id=deputy.get('id'),
                name=deputy.get('name'),
                state_code=deputy.get('state_code')
            )
