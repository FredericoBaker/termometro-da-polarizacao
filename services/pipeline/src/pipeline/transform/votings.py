import logging

from termopol_db.repositories import RawVotingRepository, NormalizedVotingRepository

logger = logging.getLogger(__name__)


class VotingTransformer:
    def __init__(self):
        self.raw_voting_repo = RawVotingRepository()
        self.voting_repo = NormalizedVotingRepository()

    def transform(self) -> None:
        """
            Transforms all newly ingested voting data and upserts into normalized votings table.
        """
        for voting in self.raw_voting_repo.get_dirty_votings_generator():
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
                self.raw_voting_repo.clear_voting_dirty(voting.get('id'))
                continue

            self.voting_repo.upsert_voting(
                external_id=voting.get('id'),
                date=voting_date,
                registration_datetime=registration_datetime,
                approval=voting.get('approval')
            )
            self.raw_voting_repo.clear_voting_dirty(voting.get('id'))