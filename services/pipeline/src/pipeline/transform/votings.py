import logging
from datetime import datetime

from termopol_db.repositories import RawVotingRepository, NormalizedVotingRepository

logger = logging.getLogger(__name__)


class VotingTransformer:
    def __init__(self):
        self.raw_voting_repo = RawVotingRepository()
        self.voting_repo = NormalizedVotingRepository()

    def transform(self, start_date: datetime, end_date: datetime) -> None:
        """
            Transforms all newly ingested voting data and upserts into normalized votings table.
        """
        for voting in self.raw_voting_repo.get_votings_by_date_range_generator(
            start_date=start_date,
            end_date=end_date
        ):
            registration_datetime = voting.get('registration_datetime')
            voting_date = voting.get('date')
            if not registration_datetime and voting_date:
                registration_datetime = f"{voting_date}T00:00:00"
                logger.warning(
                    "Voting missing registration_datetime during transform; using date fallback at midnight",
                    extra={"external_voting_id": voting.get('id'), "voting_date": voting_date},
                )
            elif not registration_datetime and not voting_date:
                logger.warning(
                    "Skipping normalized voting upsert with missing date and registration_datetime",
                    extra={"external_voting_id": voting.get('id')},
                )
                continue

            self.voting_repo.upsert_voting(
                external_id=voting.get('id'),
                date=voting_date,
                registration_datetime=registration_datetime,
                approval=voting.get('approval')
            )