import logging
from concurrent.futures import ThreadPoolExecutor

from pipeline.metrics.backbone import BackboneMetrics
from pipeline.metrics.polarization import PolarizationMetrics
from pipeline.metrics.layout import LayoutMetrics
from termopol_db.repositories import GraphRepository

logger = logging.getLogger(__name__)


class MetricsRunner:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self.backbone_metrics = BackboneMetrics()
        self.polarization_metrics = PolarizationMetrics()
        self.layout_metrics = LayoutMetrics()

    def run_all(self) -> None:
        graphs = self.graph_repo.get_dirty_graphs()
        processed_graphs = 0

        for graph in graphs:
            graph_id = graph["id"]
            logger.info("Starting metrics for graph", extra={"graph_id": graph_id})

            # 1. Backbone must run first
            self.backbone_metrics.compute_graph_backbone(graph_id)

            # 2. Polarization and Layout can run in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_polarization = executor.submit(
                    self.polarization_metrics.compute_graph_polarization, graph_id
                )
                future_layout = executor.submit(
                    self.layout_metrics.compute_graph_layout, graph_id
                )

                future_polarization.result()
                future_layout.result()

            self.graph_repo.clear_graph_metrics_dirty(graph_id)
            processed_graphs += 1

        logger.info(
            "Finished all metrics computation for dirty graphs",
            extra={"graph_count": processed_graphs},
        )

__all__ = ["MetricsRunner"]
