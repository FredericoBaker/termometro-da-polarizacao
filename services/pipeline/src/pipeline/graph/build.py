from datetime import datetime
from typing import Optional
import itertools
import math
import logging
import os
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

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
        self.edge_batch_size = max(1000, int(os.getenv("GRAPH_EDGE_BATCH_SIZE", "5000")))
        self.max_workers = max(1, int(os.getenv("GRAPH_BUILD_WORKERS", "4")))
        self.max_in_flight = max(
            self.max_workers,
            int(os.getenv("GRAPH_BUILD_MAX_IN_FLIGHT", str(self.max_workers * 4)))
        )

    def build(self) -> None:
        logger.info(
            "Starting graph build",
            extra={
                "workers": self.max_workers,
                "max_in_flight": self.max_in_flight,
                "edge_batch_size": self.edge_batch_size
            },
        )
        submitted = 0
        completed = 0
        futures = set()

        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="graph-build") as executor:
            for voting in self.voting_repo.get_graph_dirty_votings_generator():
                futures.add(executor.submit(self._process_voting, voting))
                submitted += 1

                if submitted % 10 == 0:
                    logger.info("Queued voting batch", extra={"queued_votings": submitted})

                if len(futures) >= self.max_in_flight:
                    done, futures = wait(futures, return_when=FIRST_COMPLETED)
                    for done_future in done:
                        done_future.result()
                        completed += 1

            while futures:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                for done_future in done:
                    done_future.result()
                    completed += 1

        logger.info(
            "Finished graph build",
            extra={"total_votings_queued": submitted, "total_votings_completed": completed},
        )

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
            self.voting_repo.clear_voting_graph_dirty(voting_id)
            return

        # 2. Get rollcalls and group deputies by vote
        yes_votes = set()
        no_votes = set()
        
        for rollcall in self.rollcall_repo.get_rollcalls_by_voting_generator(voting_id):
            deputy_id = rollcall.get('deputy_id')
            vote = rollcall.get('vote')

            if deputy_id is None:
                logger.warning(
                    "Skipping rollcall without deputy_id",
                    extra={"voting_id": voting_id, "rollcall_vote": vote},
                )
                continue
            
            if vote == 1: # Sim
                if deputy_id in no_votes:
                    logger.warning(
                        "Conflicting rollcall vote for deputy; keeping latest vote",
                        extra={"voting_id": voting_id, "deputy_id": deputy_id, "latest_vote": 1},
                    )
                    no_votes.discard(deputy_id)
                yes_votes.add(deputy_id)
            elif vote == 0: # Não
                if deputy_id in yes_votes:
                    logger.warning(
                        "Conflicting rollcall vote for deputy; keeping latest vote",
                        extra={"voting_id": voting_id, "deputy_id": deputy_id, "latest_vote": 0},
                    )
                    yes_votes.discard(deputy_id)
                no_votes.add(deputy_id)
        
        all_voters = sorted(yes_votes | no_votes)
        if len(all_voters) < 2:
            for graph in graphs_to_update:
                self.graph_repo.upsert_graph_voting(graph.get('id'), voting_id)
            self.voting_repo.clear_voting_graph_dirty(voting_id)
            return

        # 3. Process pairs and bulk-upsert edges
        pair_count = 0
        total_pairs = math.comb(len(all_voters), 2)
        edge_rows = []
        upserted_rows = 0

        for d1, d2 in itertools.combinations(all_voters, 2):
            # Determine weight delta
            # Same vote: +1, Different vote: -1
            v1 = 1 if d1 in yes_votes else 0
            v2 = 1 if d2 in yes_votes else 0
            
            delta_w = 1 if v1 == v2 else -1

            for graph in graphs_to_update:
                edge_rows.append(
                    (
                        graph.get('id'),
                        d1,
                        d2,
                        delta_w,
                        abs(delta_w),
                        None,
                        None,
                    )
                )
            if len(edge_rows) >= self.edge_batch_size:
                upserted_rows += self.edge_repo.bulk_upsert_edges(
                    edge_rows,
                    page_size=self.edge_batch_size,
                )
                edge_rows = []

            pair_count += 1
            if pair_count % 5000 == 0:
                logger.debug(
                    "Processed edge pairs for voting",
                    extra={"voting_id": voting_id, "processed_pairs": pair_count, "total_pairs": total_pairs},
                )

        if edge_rows:
            upserted_rows += self.edge_repo.bulk_upsert_edges(
                edge_rows,
                page_size=self.edge_batch_size,
            )
        
        # 4. Mark voting as processed for these graphs
        for graph in graphs_to_update:
            graph_id = graph.get('id')
            self.graph_repo.upsert_graph_voting(graph_id, voting_id)
            self.graph_repo.mark_graph_metrics_dirty(graph_id)
        self.voting_repo.clear_voting_graph_dirty(voting_id)
        logger.debug(
            "Finished voting graph build",
            extra={
                "voting_id": voting_id,
                "graphs_updated": len(graphs_to_update),
                "total_pairs": total_pairs,
                "upserted_edge_rows": upserted_rows,
            },
        )

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
