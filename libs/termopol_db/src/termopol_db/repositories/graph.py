import logging
from typing import Dict, Any, List, Optional
from datetime import date

from termopol_db.repositories.base import BaseRepository
from termopol_db.queries import GraphQueries

logger = logging.getLogger(__name__)


class GraphRepository(BaseRepository):
    
    def upsert_graph(
        self,
        time_granularity_id: int,
        legislature: Optional[int] = None,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a graph in graph table.
        
        Args:
            time_granularity_id: Time granularity identifier (1=legislature, 2=year, 3=month)
            legislature: Legislature number
            year: Year
            month: First day of the respective month
            
        Returns:
            The inserted/updated graph record
        """
        query = GraphQueries.upsert_graph(self.schema)
        params = (time_granularity_id, legislature, year, month)
        logger.debug(
            "Upserting graph",
            extra={
                "time_granularity_id": time_granularity_id,
                "legislature": legislature,
                "year": year,
                "month": month
            }
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_graph_by_id(self, graph_id: int) -> Optional[Dict[str, Any]]:
        query = GraphQueries.get_graph_by_id(self.schema)
        return self._execute_query(query, (graph_id,), fetch_one=True)
    
    def get_graph_by_legislature(self, legislature: int) -> Optional[Dict[str, Any]]:
        query = GraphQueries.get_graph_by_legislature(self.schema)
        return self._execute_query(query, (legislature,), fetch_one=True)
    
    def get_graph_by_year(self, year: int) -> Optional[Dict[str, Any]]:
        query = GraphQueries.get_graph_by_year(self.schema)
        return self._execute_query(query, (year,), fetch_one=True)
    
    def get_graph_by_month(self, month_date: date) -> Optional[Dict[str, Any]]:
        query = GraphQueries.get_graph_by_month(self.schema)
        return self._execute_query(query, (month_date,), fetch_one=True)
    
    def get_all_graphs(self) -> List[Dict[str, Any]]:
        query = GraphQueries.get_all_graphs(self.schema)
        return self._execute_query(query, fetch_one=False)
    
    def upsert_graph_voting(self, graph_id: int, voting_id: int) -> Optional[Dict[str, Any]]:
        """
        Record that a voting has been processed for a specific graph.
        Returns the record if it was inserted, or None if it already existed.
        """
        query = GraphQueries.upsert_graph_voting(self.schema)
        return self._execute_query(query, (graph_id, voting_id), fetch_one=True)
    
    def get_graph_voting(self, graph_id: int, voting_id: int) -> Optional[Dict[str, Any]]:
        """Check if a voting has been processed for a specific graph."""
        query = GraphQueries.get_graph_voting(self.schema)
        return self._execute_query(query, (graph_id, voting_id), fetch_one=True)


class EdgeRepository(BaseRepository):
    
    def upsert_edge(
        self,
        graph_id: int,
        deputy_a: int,
        deputy_b: int,
        w_signed: float,
        p_deputy_a: float,
        p_deputy_b: float
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update an edge in edges table.
        Automatically ensures deputy_a < deputy_b.
        
        Args:
            graph_id: Reference to graph table
            deputy_a: First deputy ID
            deputy_b: Second deputy ID
            w_signed: Signed weight (can be negative)
            p_deputy_a: Disparity fraction p_ab from deputy_a perspective
            p_deputy_b: Disparity fraction p_ab from deputy_b perspective
            
        Returns:
            The inserted/updated edge record
        """
        # Ensure deputy_a < deputy_b
        if deputy_a > deputy_b:
            deputy_a, deputy_b = deputy_b, deputy_a
        
        query = GraphQueries.upsert_edge(self.schema)
        params = (graph_id, deputy_a, deputy_b, w_signed, w_signed, p_deputy_a, p_deputy_b)
        logger.debug(
            "Upserting edge",
            extra={
                "graph_id": graph_id,
                "deputy_a": deputy_a,
                "deputy_b": deputy_b,
                "w_signed": w_signed
            }
        )
        return self._execute_query(query, params, fetch_one=True)

    def update_edge_p_values(
        self,
        graph_id: int,
        deputy_a: int,
        deputy_b: int,
        p_deputy_a: float,
        p_deputy_b: float
    ) -> Optional[Dict[str, Any]]:
        # Ensure deputy_a < deputy_b
        if deputy_a > deputy_b:
            deputy_a, deputy_b = deputy_b, deputy_a
            p_deputy_a, p_deputy_b = p_deputy_b, p_deputy_a

        query = GraphQueries.update_edge_p_values(self.schema)
        params = (p_deputy_a, p_deputy_b, graph_id, deputy_a, deputy_b)
        return self._execute_query(query, params, fetch_one=True)

    def reset_backbone_flags(self, graph_id: int) -> int:
        query = GraphQueries.reset_backbone_flags(self.schema)
        return self._execute_update(query, (graph_id,))

    def set_backbone_flags(self, graph_id: int, edge_pairs: List[tuple[int, int]]) -> int:
        if not edge_pairs:
            return 0

        deputy_a_list = [pair[0] for pair in edge_pairs]
        deputy_b_list = [pair[1] for pair in edge_pairs]
        query = GraphQueries.set_backbone_flags(self.schema)
        return self._execute_update(query, (deputy_a_list, deputy_b_list, graph_id))
    
    def get_edge(self, graph_id: int, deputy_a: int, deputy_b: int) -> Optional[Dict[str, Any]]:
        # Ensure deputy_a < deputy_b
        if deputy_a > deputy_b:
            deputy_a, deputy_b = deputy_b, deputy_a
        
        query = GraphQueries.get_edge(self.schema)
        return self._execute_query(query, (graph_id, deputy_a, deputy_b), fetch_one=True)
    
    def get_edges_by_graph(self, graph_id: int) -> List[Dict[str, Any]]:
        query = GraphQueries.get_edges_by_graph(self.schema)
        return self._execute_query(query, (graph_id,), fetch_one=False)
    
    def delete_edges_by_graph(self, graph_id: int) -> int:
        query = GraphQueries.delete_edges_by_graph(self.schema)
        return self._execute_update(query, (graph_id,))


class PolarizationMetricRepository(BaseRepository):
    
    def upsert_polarization_metric(
        self,
        graph_id: int,
        triads_total: int,
        three_positive_triads: int,
        two_positive_triads: int,
        one_positive_triads: int,
        zero_positive_triads: int,
        polarization_index: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a polarization metric in polarization_metrics table.
        
        Args:
            graph_id: Reference to graph table
            polarization_index: Calculated polarization index (0-1)
            
        Returns:
            The inserted/updated metric record
        """
        query = GraphQueries.upsert_polarization_metric(self.schema)
        params = (
            graph_id,
            triads_total,
            three_positive_triads,
            two_positive_triads,
            one_positive_triads,
            zero_positive_triads,
            polarization_index
        )
        logger.debug(
            "Upserting polarization metric",
            extra={
                "graph_id": graph_id,
                "polarization_index": polarization_index,
                "triads_total": triads_total
            }
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_metric_by_graph(self, graph_id: int) -> Optional[Dict[str, Any]]:
        query = GraphQueries.get_polarization_metric(self.schema)
        return self._execute_query(query, (graph_id,), fetch_one=True)
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        query = GraphQueries.get_all_polarization_metrics(self.schema)
        return self._execute_query(query, fetch_one=False)
