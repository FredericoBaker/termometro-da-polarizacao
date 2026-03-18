import logging
from typing import Dict, Any, List
import networkx as nx

from termopol_db.repositories import EdgeRepository, GraphRepository

logger = logging.getLogger(__name__)


class LayoutMetrics:
    """
    Compute spatial layout (x, y) coordinates for nodes in each graph.
    
    Uses Fruchterman-Reingold force directed algorithm.
    Treats positive edges as attractive forces and negative edges as repulsive forces.
    """

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

        G = nx.Graph()
        
        for edge in backbone_edges:
            w = float(edge["w_signed"])
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            
            G.add_node(deputy_a)
            G.add_node(deputy_b)
            
            # Since standard Fruchterman-Reingold doesn't handle negative weights well directly 
            # in networkx, we will add edges where weight > 0 for attraction.
            # Negative edges will be implicitly repulsed by the algorithm's global node repulsion.
            if w > 0:
                G.add_edge(deputy_a, deputy_b, weight=w)

        pos = nx.spring_layout(G, weight="weight", iterations=self.iterations, scale=self.scale, seed=42)

        nodes_positioned = 0
        for node_id, (x, y) in pos.items():
            self.graph_repo.upsert_node(
                graph_id=graph_id,
                deputy_id=node_id,
                x=float(x),
                y=float(y)
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
