import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple
import networkx as nx

from termopol_db.repositories import EdgeRepository

logger = logging.getLogger(__name__)


class BackboneMetrics:
    """
    Compute disparity filter fractions p_ij for each edge in each graph.

    For an edge (i, j) from i's perspective, we compute:
        p_ij = |w_ij| / sum_k |w_ik|
    where the denominator is the node strength (absolute weighted degree).
    """

    def __init__(
        self,
        target_lcc_ratio: float = 0.8,
        alpha_min: float = 1e-6,
        alpha_max: float = 1.0,
        alpha_tolerance: float = 1e-3,
        max_alpha_iterations: int = 25,
    ):
        self.edge_repo = EdgeRepository()
        self.target_lcc_ratio = target_lcc_ratio
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.alpha_tolerance = alpha_tolerance
        self.max_alpha_iterations = max_alpha_iterations

    def compute_graph_backbone(self, graph_id: int) -> Dict[str, Any]:
        updated_p_values = self.compute_graph_p_values(graph_id)
        edges = self.edge_repo.get_edges_by_graph(graph_id)
        if not edges:
            return {"updated_p_values": updated_p_values, "backbone_edges": 0}

        node_ids = self._extract_node_ids(edges)
        degree_by_node = self._compute_degrees(edges)

        best_alpha, best_pairs, best_ratio = self._find_alpha_and_backbone_pairs(
            edges=edges,
            node_ids=node_ids,
            degree_by_node=degree_by_node,
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

        strengths = defaultdict(float)
        for edge in edges:
            w_abs = self._absolute_weight(edge)
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            strengths[deputy_a] += w_abs
            strengths[deputy_b] += w_abs

        updated_edges = 0
        for edge in edges:
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            w_abs = self._absolute_weight(edge)

            p_deputy_a = w_abs / strengths[deputy_a] if strengths[deputy_a] > 0 else 0.0
            p_deputy_b = w_abs / strengths[deputy_b] if strengths[deputy_b] > 0 else 0.0

            self.edge_repo.update_edge_p_values(
                graph_id=graph_id,
                deputy_a=deputy_a,
                deputy_b=deputy_b,
                p_deputy_a=p_deputy_a,
                p_deputy_b=p_deputy_b,
            )
            updated_edges += 1

        logger.info(
            "Computed p_ij for graph edges",
            extra={"graph_id": graph_id, "edge_count": len(edges), "updated_edges": updated_edges},
        )
        return updated_edges

    def _find_alpha_and_backbone_pairs(
        self,
        edges: List[Dict[str, Any]],
        node_ids: List[int],
        degree_by_node: Dict[int, int],
    ) -> Tuple[float, List[Tuple[int, int]], float]:
        low = self.alpha_min
        high = self.alpha_max
        best_alpha = self.alpha_max
        best_pairs = self._select_backbone_pairs(edges, degree_by_node, self.alpha_max)
        best_ratio = self._largest_component_ratio(node_ids, best_pairs)
        found_feasible = best_ratio >= self.target_lcc_ratio

        for _ in range(self.max_alpha_iterations):
            mid = (low + high) / 2.0
            candidate_pairs = self._select_backbone_pairs(edges, degree_by_node, mid)
            candidate_ratio = self._largest_component_ratio(node_ids, candidate_pairs)

            if candidate_ratio >= self.target_lcc_ratio:
                # Keep the smallest feasible alpha to maximize pruning.
                found_feasible = True
                best_alpha = mid
                best_pairs = candidate_pairs
                best_ratio = candidate_ratio
                high = mid
            else:
                low = mid

            if high - low < self.alpha_tolerance:
                break

        if not found_feasible:
            logger.warning(
                "Could not satisfy target LCC ratio within alpha bounds; using alpha_max result",
                extra={
                    "target_lcc_ratio": self.target_lcc_ratio,
                    "alpha_min": self.alpha_min,
                    "alpha_max": self.alpha_max,
                    "achieved_lcc_ratio": best_ratio,
                },
            )

        return best_alpha, best_pairs, best_ratio

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
        # If degree <= 1, the edge is the only local connection for that node.
        if node_degree <= 1:
            return True
        threshold = 1.0 - (alpha ** (1.0 / (node_degree - 1)))
        return p_ij > threshold

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

        largest_cc_size = max((len(component) for component in nx.connected_components(graph)), default=0)
        return largest_cc_size / float(graph.number_of_nodes())

    @staticmethod
    def _absolute_weight(edge: Dict[str, Any]) -> float:
        if edge.get("abs_w") is not None:
            return float(edge["abs_w"])
        return abs(float(edge.get("w_signed", 0.0)))
