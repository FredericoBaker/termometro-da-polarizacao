import logging
from typing import Dict, Any, List
import networkx as nx

from termopol_db.repositories import EdgeRepository, GraphRepository

logger = logging.getLogger(__name__)


class LayoutMetrics:
    """
    Compute spatial layout (x, y) coordinates for nodes in each graph.

    Uses Fruchterman-Reingold force directed algorithm on backbone edges.
    Positive edges keep their original weight (strong attraction = same cluster).
    Negative edges are included with a small fraction of the median positive
    weight so that every backbone node stays connected to the graph without
    pulling opponents together.
    """

    NEGATIVE_WEIGHT_FRACTION = 0.01

    def __init__(self, iterations: int = 50, scale: float = 1000.0):
        self.edge_repo = EdgeRepository()
        self.graph_repo = GraphRepository()
        self.iterations = iterations
        self.scale = scale

    def compute_graph_layout(self, graph_id: int) -> Dict[str, int]:
        backbone_edges = self.edge_repo.get_backbone_edges_by_graph(graph_id)

        if not backbone_edges:
            logger.info("No backbone edges found for graph layout", extra={"graph_id": graph_id})
            return {"nodes_positioned": 0}

        pos_weights = [float(e["w_signed"]) for e in backbone_edges if float(e["w_signed"]) > 0]
        if not pos_weights:
            logger.info("No positive backbone edges for layout", extra={"graph_id": graph_id})
            return {"nodes_positioned": 0}

        pos_weights.sort()
        median_pos = pos_weights[len(pos_weights) // 2]
        neg_layout_weight = median_pos * self.NEGATIVE_WEIGHT_FRACTION

        G = nx.Graph()
        for edge in backbone_edges:
            w = float(edge["w_signed"])
            layout_w = w if w > 0 else neg_layout_weight
            G.add_edge(edge["deputy_a"], edge["deputy_b"], weight=layout_w)

        pos = nx.spring_layout(G, weight="weight", iterations=self.iterations, scale=self.scale, seed=42)
        nodes_positioned = 0
        for node_id, (x, y) in pos.items():
            self.graph_repo.upsert_node(
                graph_id=graph_id,
                deputy_id=node_id,
                x=float(x),
                y=float(y),
            )
            nodes_positioned += 1

        logger.info(
            "Computed layout for graph",
            extra={
                "graph_id": graph_id,
                "nodes_positioned": nodes_positioned,
            },
        )
        return {"nodes_positioned": nodes_positioned}
