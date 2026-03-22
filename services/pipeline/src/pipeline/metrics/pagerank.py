import logging
from typing import Dict

import networkx as nx

from termopol_db.repositories import EdgeRepository, GraphRepository

logger = logging.getLogger(__name__)


class PageRankMetrics:
    """
    Compute PageRank centrality on backbone edges (positive weights only).
    """

    def __init__(self):
        self.edge_repo = EdgeRepository()
        self.graph_repo = GraphRepository()

    def compute_graph_pagerank(self, graph_id: int) -> Dict[str, int]:
        backbone_edges = self.edge_repo.get_backbone_edges_by_graph(graph_id)
        if not backbone_edges:
            return {"nodes_ranked": 0}

        graph = nx.Graph()
        for edge in backbone_edges:
            deputy_a = edge["deputy_a"]
            deputy_b = edge["deputy_b"]
            w = abs(float(edge["w_signed"]))
            graph.add_node(deputy_a)
            graph.add_node(deputy_b)
            graph.add_edge(deputy_a, deputy_b, weight=w)

        if graph.number_of_nodes() == 0:
            return {"nodes_ranked": 0}

        pagerank_by_node = nx.pagerank(graph, weight="weight")
        nodes_ranked = 0

        for deputy_id, pagerank in pagerank_by_node.items():
            self.graph_repo.update_node_pagerank(
                graph_id=graph_id,
                deputy_id=deputy_id,
                pagerank=float(pagerank),
            )
            nodes_ranked += 1

        logger.info(
            "Computed pagerank for graph",
            extra={"graph_id": graph_id, "nodes_ranked": nodes_ranked},
        )
        return {"nodes_ranked": nodes_ranked}
