from datetime import datetime
from typing import Optional, List
import itertools
import logging

from termopol_db.repositories import (
    NormalizedVotingRepository, 
    NormalizedRollcallRepository, 
    GraphRepository,
    EdgeRepository
)

logger = logging.getLogger(__name__)

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
        self.edge_repo = EdgeRepository()

    def build(self, start_date: datetime, end_date: datetime) -> None:
        logger.info(f"Starting graph build from {start_date} to {end_date}")
        voting_count = 0
        for voting in self.voting_repo.get_votings_by_created_updated_range_generator(start_date, end_date):
            voting_count += 1
            if voting_count % 10 == 0:
                print(f"Processing voting {voting_count}...")
            self._process_voting(voting)
        print(f"Finished processing {voting_count} votings.")

    def _process_voting(self, voting: dict) -> None:
        voting_id = voting.get('id')
        voting_datetime = voting.get('registration_datetime')

        # 1. Determine relevant graphs and check if already processed
        potential_graphs = []

        # Legislature Graph
        voting_legislature = self._get_legislature(voting_datetime)
        if voting_legislature:
            legislature_graph = self.graph_repo.get_graph_by_legislature(voting_legislature)
            if not legislature_graph:
                legislature_graph = self.graph_repo.upsert_graph(
                    time_granularity_id=GRAPH_GRANULARITIES_IDS['legislature'],
                    legislature=voting_legislature
                )
            potential_graphs.append(legislature_graph)
        
        # Year Graph
        voting_year = self._get_year(voting_datetime)
        if voting_year:
            year_graph = self.graph_repo.get_graph_by_year(voting_year)
            if not year_graph:
                year_graph = self.graph_repo.upsert_graph(
                    time_granularity_id=GRAPH_GRANULARITIES_IDS['year'],
                    year=voting_year
                )
            potential_graphs.append(year_graph)

        # Month Graph
        voting_month_date = self._get_month(voting_datetime)
        if voting_month_date:
            month_graph = self.graph_repo.get_graph_by_month(voting_month_date)
            if not month_graph:
                month_graph = self.graph_repo.upsert_graph(
                    time_granularity_id=GRAPH_GRANULARITIES_IDS['month'],
                    month=voting_month_date
                )
            potential_graphs.append(month_graph)

        # Filter out graphs that already processed this voting
        graphs_to_update = []
        for graph in potential_graphs:
            if not self.graph_repo.get_graph_voting(graph.get('id'), voting_id):
                graphs_to_update.append(graph)
        
        if not graphs_to_update:
            return

        # 2. Get rollcalls and group deputies by vote
        yes_votes = []
        no_votes = []
        
        for rollcall in self.rollcall_repo.get_rollcalls_by_voting_generator(voting_id):
            deputy_id = rollcall.get('deputy_id')
            vote = rollcall.get('vote')
            
            if vote == 1: # Sim
                yes_votes.append(deputy_id)
            elif vote == 0: # Não
                no_votes.append(deputy_id)
        
        all_voters = yes_votes + no_votes
        if len(all_voters) < 2:
            return

        # 3. Process pairs and update edges
        # We need to update edges for all combinations of deputies who voted
        pair_count = 0
        pairs = list(itertools.combinations(sorted(all_voters), 2))
        total_pairs = len(pairs)
        
        for d1, d2 in pairs:
            # Determine weight delta
            # Same vote: +1, Different vote: -1
            v1 = 1 if d1 in yes_votes else 0
            v2 = 1 if d2 in yes_votes else 0
            
            delta_w = 1 if v1 == v2 else -1
            
            for graph in graphs_to_update:
                self.edge_repo.upsert_edge(
                    graph_id=graph.get('id'),
                    deputy_a=d1,
                    deputy_b=d2,
                    w_signed=float(delta_w),
                    abs_w=1.0,
                    alpha_deputy_a=None,
                    alpha_deputy_b=None
                )
            
            pair_count += 1
            if pair_count % 5000 == 0:
                print(f"  Processed {pair_count}/{total_pairs} pairs for voting {voting_id}...")
        
        # 4. Mark voting as processed for these graphs
        for graph in graphs_to_update:
            self.graph_repo.upsert_graph_voting(graph.get('id'), voting_id)

    def _get_legislature(self, date: datetime) -> Optional[int]:
        """
        Returns the legislature number given a datetime.
        Since legislature 46 they start on 02/01 and end four years later on 01/31.
        """
        if not date:
            return None
            
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)
            
        legislature_46_start = datetime(1979, 2, 1)
        
        if date < legislature_46_start:
            return None

        # if date is january, belongs to the previous year legislature
        reference_year = date.year if date.month >= 2 else date.year - 1
        
        legislature = 46 + (reference_year - 1979) // 4
        
        return legislature

    def _get_year(self, date: datetime) -> Optional[int]:
        """
        Since legislatures don't exactly align with years, if date is january we will still consider to be in previous year. 
        """
        if not date:
            return None
        reference_year = date.year if date.month >= 2 else date.year - 1
        
        return reference_year
    
    def _get_month(self, date: datetime) -> Optional[datetime]:
        """
        Returns the first day of the respective month.
        """
        if not date:
            return None
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
