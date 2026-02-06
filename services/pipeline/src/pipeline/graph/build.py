from datetime import datetime

from termopol_db.repositories import NormalizedVotingRepository, NormalizedRollcallRepository, GraphRepository

GRAPH_GRANULARITIES_IDS = {
    'legislature': 1,
    'year': 2,
    'month': 3
}

class BuildGraph:
    def __init__(self):
        self.voting_repo = NormalizedVotingRepository()
        self.rollcall_repo = NormalizedRollcallRepository()
        self.graph_repo = GraphRepository()

    def build(self, start_date: datetime, end_date: datetime) -> None:
        for voting in self.voting_repo.get_votings_by_created_updated_range_generator(start_date, end_date)
            self._process_voting(voting)

    def _process_voting(self, voting):
        voting_datetime = voting.get('date')

        voting_legislature = self._get_legislature(voting_datetime)
        legislature_graph = self.graph_repo.get_graph_by_legislature(voting_legislature)
        if not legislature_graph:
            legislature_graph = self.graph_repo.upsert_graph(
                time_granularity_id=GRAPH_GRANULARITIES_IDS['legislature'],
                legislature=voting_legislature
            )
        
        voting_year = self._get_year(voting_datetime)
        year_graph = self.graph_repo.get_graph_by_year(voting_year)
        if not year_graph:
            year_graph = self.graph_repo.upsert_graph(
                time_granularity_id=GRAPH_GRANULARITIES_IDS['year'],
                legislature=voting_year
            )

        voting_month = self._get_month(voting_datetime)
        month_graph = self.graph_repo.get_graph_by_month(voting_month)
        if not month_graph:
            month_graph = self.graph_repo.upsert_graph(
                time_granularity_id=GRAPH_GRANULARITIES_IDS['month'],
                legislature=voting_month
            )

        # I'll probablu need other approach here
        for rollcall in self.rollcall_repo.get_rollcalls_by_voting_generator(voting.get('id')):
            


    def _get_legislature(date: datetime) -> Optional[int]:
        """
        Returns the legislature number given a datetime.
        Since legislature 46 they start on 02/01 and end four years later on 01/31.
        """
        legislature_46_start = datetime(1979, 2, 1)
        
        if date < legislature_46_start:
            return None

        # if date is january, belongs to the previous year legislature
        reference_year = date.year if date.month >= 2 else date.year - 1
        
        legislature = 46 + (reference_year - 1979) // 4
        
        return legislature

    def _get_year(date: datetime) -> Optional[int]:
        """
        Since legislatures don't exactly align with years, if date is january we will still consider to be in previous year. 
        """
        reference_year = date.year if date.month >= 2 else date.year - 1
        
        return reference_year
    
    def _get_month(date: datetime) -> Optional[int]:
        """
        Returns the first day of the respective month.
        """
        return date.replace(day=1)
