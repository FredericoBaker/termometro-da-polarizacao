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

    Polarization points are anchored so that:
      - share(+--) among balanced triads = 0.00 -> 0 points
      - share(+--) among balanced triads = 0.75 -> 100 points
      - values above 0.75 can exceed 100 points
    """
    POLARIZATION_REFERENCE_SHARE = 0.75

    def __init__(self):
        self.edge_repo = EdgeRepository()
        self.metric_repo = PolarizationMetricRepository()

    def compute_graph_polarization(self, graph_id: int) -> Dict[str, float]:
        backbone_edges = self.edge_repo.get_backbone_edges_by_graph(graph_id)

        counts = self._count_signed_triads(backbone_edges)
        triads_total = (
            counts["three_positive_triads"]
            + counts["two_positive_triads"]
            + counts["one_positive_triads"]
            + counts["zero_positive_triads"]
        )

        balanced_triads = counts["three_positive_triads"] + counts["one_positive_triads"]
        two_negative_share_balanced = (
            counts["one_positive_triads"] / balanced_triads if balanced_triads > 0 else 0.0
        )
        polarization_index = (
            100.0 * (two_negative_share_balanced / self.POLARIZATION_REFERENCE_SHARE)
            if self.POLARIZATION_REFERENCE_SHARE > 0
            else 0.0
        )
        balance_ratio = balanced_triads / triads_total if triads_total > 0 else 0.0

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
                "balanced_triads": balanced_triads,
                "two_negative_share_balanced": two_negative_share_balanced,
                "balance_ratio": balance_ratio,
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
