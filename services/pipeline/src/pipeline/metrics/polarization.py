import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from termopol_db.repositories import EdgeRepository, GraphRepository, PolarizationMetricRepository

logger = logging.getLogger(__name__)


class PolarizationMetrics:
    """
    Compute triad type counts and polarization index from backbone edges.

    Triad types are counted by number of positive edges:
      - three_positive_triads: +++
      - two_positive_triads: ++-
      - one_positive_triads: +--
      - zero_positive_triads: ---
    """

    def __init__(self):
        self.graph_repo = GraphRepository()
        self.edge_repo = EdgeRepository()
        self.metric_repo = PolarizationMetricRepository()

    def compute_all_graphs_polarization(self) -> Dict[str, int]:
        graphs = self.graph_repo.get_all_graphs()
        processed_graphs = 0

        for graph in graphs:
            self.compute_graph_polarization(graph["id"])
            processed_graphs += 1

        logger.info(
            "Finished polarization metrics for all graphs",
            extra={"graph_count": processed_graphs},
        )
        return {"graph_count": processed_graphs}

    def compute_graph_polarization(self, graph_id: int) -> Dict[str, float]:
        edges = self.edge_repo.get_edges_by_graph(graph_id)
        backbone_edges = [edge for edge in edges if edge.get("is_backbone")]

        counts = self._count_signed_triads(backbone_edges)
        triads_total = (
            counts["three_positive_triads"]
            + counts["two_positive_triads"]
            + counts["one_positive_triads"]
            + counts["zero_positive_triads"]
        )

        # Signed-balance-inspired index: fraction of unbalanced triads.
        polarization_index = 0.0
        if triads_total > 0:
            unbalanced = counts["two_positive_triads"] + counts["zero_positive_triads"]
            polarization_index = unbalanced / triads_total

        self.metric_repo.upsert_polarization_metric(
            graph_id=graph_id,
            triads_total=triads_total,
            three_positive_triads=counts["three_positive_triads"],
            two_positive_triads=counts["two_positive_triads"],
            one_positive_triads=counts["one_positive_triads"],
            zero_positive_triads=counts["zero_positive_triads"],
            polarization_index=polarization_index,
        )

        logger.info(
            "Computed polarization metrics for graph",
            extra={
                "graph_id": graph_id,
                "backbone_edges": len(backbone_edges),
                "triads_total": triads_total,
                "polarization_index": polarization_index,
            },
        )
        return {"triads_total": triads_total, "polarization_index": polarization_index}

    @staticmethod
    def _edge_sign(w_signed: float) -> int:
        return 1 if float(w_signed) >= 0 else -1

    def _count_signed_triads(self, edges: List[Dict]) -> Dict[str, int]:
        adjacency = defaultdict(set)
        sign_map: Dict[Tuple[int, int], int] = {}

        for edge in edges:
            a = edge["deputy_a"]
            b = edge["deputy_b"]
            key = (a, b) if a < b else (b, a)
            adjacency[key[0]].add(key[1])
            adjacency[key[1]].add(key[0])
            sign_map[key] = self._edge_sign(edge["w_signed"])

        three_positive_triads = 0
        two_positive_triads = 0
        one_positive_triads = 0
        zero_positive_triads = 0

        nodes = sorted(adjacency.keys())
        for u in nodes:
            for v in [node for node in adjacency[u] if node > u]:
                common_neighbors = [node for node in adjacency[u].intersection(adjacency[v]) if node > v]
                for w in common_neighbors:
                    s_uv = sign_map[(u, v)]
                    s_uw = sign_map[(u, w)]
                    s_vw = sign_map[(v, w)]
                    positive_edges = int(s_uv > 0) + int(s_uw > 0) + int(s_vw > 0)

                    if positive_edges == 3:
                        three_positive_triads += 1
                    elif positive_edges == 2:
                        two_positive_triads += 1
                    elif positive_edges == 1:
                        one_positive_triads += 1
                    else:
                        zero_positive_triads += 1

        return {
            "three_positive_triads": three_positive_triads,
            "two_positive_triads": two_positive_triads,
            "one_positive_triads": one_positive_triads,
            "zero_positive_triads": zero_positive_triads,
        }
