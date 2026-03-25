import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple
import networkx as nx

from termopol_db.repositories import EdgeRepository

logger = logging.getLogger(__name__)


class BackboneMetrics:
    """
    Compute the backbone of each graph using the disparity filter (Serrano et al. 2009).

    Positive and negative edges are filtered independently: p_ij values and node
    degrees are computed within each sign subgraph, the disparity test is applied
    separately, and the surviving edges are combined before evaluating the
    largest connected component ratio.

    Alpha selection scans a predefined list from smallest to largest and picks
    the first value whose backbone keeps >= target_lcc_ratio of nodes in the
    largest connected component.
    """

    DEFAULT_ALPHA_VALUES = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]

    def __init__(
        self,
        target_lcc_ratio: float = 0.8,
        alpha_values: List[float] | None = None,
    ):
        self.edge_repo = EdgeRepository()
        self.target_lcc_ratio = target_lcc_ratio
        self.alpha_values = alpha_values or self.DEFAULT_ALPHA_VALUES
        self.p_values_batch_size = 5000

    def compute_graph_backbone(self, graph_id: int) -> Dict[str, Any]:
        updated_p_values = self.compute_graph_p_values(graph_id)
        edges = self.edge_repo.get_edges_by_graph(graph_id)
        if not edges:
            return {"updated_p_values": updated_p_values, "backbone_edges": 0}

        node_ids = self._extract_node_ids(edges)
        pos_edges, neg_edges = self._split_by_sign(edges)
        pos_degrees = self._compute_degrees(pos_edges)
        neg_degrees = self._compute_degrees(neg_edges)

        best_alpha, best_pairs, best_ratio = self._find_alpha_and_backbone_pairs(
            pos_edges=pos_edges,
            neg_edges=neg_edges,
            node_ids=node_ids,
            pos_degrees=pos_degrees,
            neg_degrees=neg_degrees,
        )

        self.edge_repo.reset_backbone_flags(graph_id)
        self.edge_repo.set_backbone_flags(graph_id, best_pairs)

        logger.info(
            "Backbone persisted for graph",
            extra={
                "graph_id": graph_id,
                "selected_alpha": best_alpha,
                "target_lcc_ratio": self.target_lcc_ratio,
                "achieved_lcc_ratio": best_ratio,
                "nodes": len(node_ids),
                "edges_total": len(edges),
                "backbone_edges": len(best_pairs),
            },
        )
        return {"updated_p_values": updated_p_values, "backbone_edges": len(best_pairs)}

    def compute_graph_p_values(self, graph_id: int) -> int:
        edges = self.edge_repo.get_edges_by_graph(graph_id)
        if not edges:
            logger.info("No edges found for graph", extra={"graph_id": graph_id})
            return 0

        pos_edges, neg_edges = self._split_by_sign(edges)
        pos_strengths = self._compute_strengths(pos_edges)
        neg_strengths = self._compute_strengths(neg_edges)

        update_rows: List[Tuple[int, int, int, float, float]] = []

        for edge in pos_edges:
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            w_abs = self._absolute_weight(edge)
            p_a = w_abs / pos_strengths[deputy_a] if pos_strengths[deputy_a] > 0 else 0.0
            p_b = w_abs / pos_strengths[deputy_b] if pos_strengths[deputy_b] > 0 else 0.0
            update_rows.append((graph_id, deputy_a, deputy_b, p_a, p_b))

        for edge in neg_edges:
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            w_abs = self._absolute_weight(edge)
            p_a = w_abs / neg_strengths[deputy_a] if neg_strengths[deputy_a] > 0 else 0.0
            p_b = w_abs / neg_strengths[deputy_b] if neg_strengths[deputy_b] > 0 else 0.0
            update_rows.append((graph_id, deputy_a, deputy_b, p_a, p_b))

        updated_edges = self.edge_repo.bulk_update_edge_p_values(
            update_rows,
            page_size=self.p_values_batch_size,
        )

        logger.info(
            "Computed p_ij for graph edges",
            extra={"graph_id": graph_id, "edge_count": len(edges), "updated_edges": updated_edges},
        )
        return updated_edges

    def _find_alpha_and_backbone_pairs(
        self,
        pos_edges: List[Dict[str, Any]],
        neg_edges: List[Dict[str, Any]],
        node_ids: List[int],
        pos_degrees: Dict[int, int],
        neg_degrees: Dict[int, int],
    ) -> Tuple[float, List[Tuple[int, int]], float]:
        for alpha in self.alpha_values:
            candidate_pairs = self._select_combined_backbone_pairs(
                pos_edges, neg_edges, pos_degrees, neg_degrees, alpha,
            )
            candidate_ratio = self._largest_component_ratio(node_ids, candidate_pairs)

            if candidate_ratio >= self.target_lcc_ratio:
                return alpha, candidate_pairs, candidate_ratio

        logger.warning(
            "Could not satisfy target LCC ratio with any predefined alpha; "
            "returning result for largest alpha tested",
            extra={
                "target_lcc_ratio": self.target_lcc_ratio,
                "alpha_values": self.alpha_values,
            },
        )

        last_alpha = self.alpha_values[-1]
        last_pairs = self._select_combined_backbone_pairs(
            pos_edges, neg_edges, pos_degrees, neg_degrees, last_alpha,
        )
        last_ratio = self._largest_component_ratio(node_ids, last_pairs)
        return last_alpha, last_pairs, last_ratio

    def _select_combined_backbone_pairs(
        self,
        pos_edges: List[Dict[str, Any]],
        neg_edges: List[Dict[str, Any]],
        pos_degrees: Dict[int, int],
        neg_degrees: Dict[int, int],
        alpha: float,
    ) -> List[Tuple[int, int]]:
        pos_pairs = self._select_backbone_pairs(pos_edges, pos_degrees, alpha)
        neg_pairs = self._select_backbone_pairs(neg_edges, neg_degrees, alpha)
        return pos_pairs + neg_pairs

    def _select_backbone_pairs(
        self,
        edges: List[Dict[str, Any]],
        degree_by_node: Dict[int, int],
        alpha: float,
    ) -> List[Tuple[int, int]]:
        selected_pairs: List[Tuple[int, int]] = []

        for edge in edges:
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            p_deputy_a = float(edge.get("p_deputy_a") or 0.0)
            p_deputy_b = float(edge.get("p_deputy_b") or 0.0)

            keep_from_a = self._passes_disparity(
                p_ij=p_deputy_a,
                node_degree=degree_by_node.get(deputy_a, 0),
                alpha=alpha,
            )
            keep_from_b = self._passes_disparity(
                p_ij=p_deputy_b,
                node_degree=degree_by_node.get(deputy_b, 0),
                alpha=alpha,
            )

            if keep_from_a or keep_from_b:
                selected_pairs.append((deputy_a, deputy_b))

        return selected_pairs

    @staticmethod
    def _passes_disparity(p_ij: float, node_degree: int, alpha: float) -> bool:
        if node_degree <= 1:
            return False
        threshold = 1.0 - (alpha ** (1.0 / (node_degree - 1)))
        return p_ij > threshold

    @staticmethod
    def _split_by_sign(
        edges: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        pos_edges: List[Dict[str, Any]] = []
        neg_edges: List[Dict[str, Any]] = []
        for edge in edges:
            w_signed = float(edge.get("w_signed", 0.0))
            if w_signed >= 0:
                pos_edges.append(edge)
            else:
                neg_edges.append(edge)
        return pos_edges, neg_edges

    @staticmethod
    def _compute_strengths(edges: List[Dict[str, Any]]) -> Dict[int, float]:
        strengths: Dict[int, float] = defaultdict(float)
        for edge in edges:
            w_abs = BackboneMetrics._absolute_weight(edge)
            strengths[edge["deputy_a"]] += w_abs
            strengths[edge["deputy_b"]] += w_abs
        return strengths

    @staticmethod
    def _extract_node_ids(edges: List[Dict[str, Any]]) -> List[int]:
        node_ids = set()
        for edge in edges:
            node_ids.add(edge["deputy_a"])
            node_ids.add(edge["deputy_b"])
        return list(node_ids)

    @staticmethod
    def _compute_degrees(edges: List[Dict[str, Any]]) -> Dict[int, int]:
        graph = nx.Graph()
        for edge in edges:
            graph.add_edge(edge["deputy_a"], edge["deputy_b"])
        return dict(graph.degree())

    @staticmethod
    def _largest_component_ratio(node_ids: List[int], edge_pairs: List[Tuple[int, int]]) -> float:
        if not node_ids:
            return 0.0

        graph = nx.Graph()
        graph.add_nodes_from(node_ids)
        graph.add_edges_from(edge_pairs)

        if graph.number_of_nodes() == 0:
            return 0.0

        largest_cc_size = max(
            (len(component) for component in nx.connected_components(graph)),
            default=0,
        )
        return largest_cc_size / float(graph.number_of_nodes())

    @staticmethod
    def _absolute_weight(edge: Dict[str, Any]) -> float:
        if edge.get("abs_w") is not None:
            return float(edge["abs_w"])
        return abs(float(edge.get("w_signed", 0.0)))
