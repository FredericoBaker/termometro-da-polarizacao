from datetime import datetime

from termopol_db.repositories import RawVotingRepository, NormalizedVotingRepository


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
            self.voting_repo.upsert_voting(
                external_id=voting.get('id'),
                date= voting.get('date'),
                registration_datetime=voting.get('registration_datetime'),
                approval=voting.get('approval')
            )