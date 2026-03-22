from datetime import date, datetime

from fastapi import HTTPException

from api.cache import ApiCache
from termopol_db.repositories.graph import GraphRepository, PolarizationMetricRepository


class MetricsService:
    def __init__(
        self,
        pol_repo: PolarizationMetricRepository,
        graph_repo: GraphRepository,
        cache: ApiCache,
    ) -> None:
        self.pol_repo = pol_repo
        self.graph_repo = graph_repo
        self.cache = cache

    @staticmethod
    def _percent_change(current: float, previous: float | None) -> float | None:
        if current is None:
            return None
        if previous is None:
            return None
        if previous == 0:
            return None
        return ((current - previous) / abs(previous)) * 100.0

    @staticmethod
    def _trend(current: float, previous: float | None) -> str:
        if current is None:
            return "unknown"
        if previous is None:
            return "no_previous"
        if current > previous:
            return "up"
        if current < previous:
            return "down"
        return "stable"

    @staticmethod
    def _graph_identifier(graph: dict) -> str | int | None:
        if graph.get("legislature") is not None:
            return graph.get("legislature")
        if graph.get("year") is not None:
            return graph.get("year")
        month = graph.get("month")
        return month.strftime("%m-%Y") if month else None

    @staticmethod
    def _parse_month_identifier(month: str) -> date:
        formats = ("%Y-%m", "%m-%Y")
        for fmt in formats:
            try:
                parsed = datetime.strptime(month, fmt)
                return date(parsed.year, parsed.month, 1)
            except ValueError:
                continue
        raise HTTPException(
            status_code=400,
            detail="Invalid month format. Use YYYY-MM or MM-YYYY.",
        )

    @staticmethod
    def _sort_graphs_by_granularity(graphs: list[dict], granularity: str, descending: bool = False) -> list[dict]:
        if granularity == "month":
            graphs.sort(key=lambda g: g.get("month") or date.min, reverse=descending)
        elif granularity == "year":
            graphs.sort(key=lambda g: g.get("year") or 0, reverse=descending)
        else:
            graphs.sort(key=lambda g: g.get("legislature") or 0, reverse=descending)
        return graphs

    def _get_previous_graph(self, graph: dict, granularity: str) -> dict | None:
        if granularity == "legislature":
            legislature = graph.get("legislature")
            if legislature is None:
                return None
            return self.graph_repo.get_graph_by_legislature(legislature - 1)

        if granularity == "year":
            year = graph.get("year")
            if year is None:
                return None
            return self.graph_repo.get_graph_by_year(year - 1)

        month_value = graph.get("month")
        if not month_value:
            return None
        if month_value.month == 1:
            previous_month = date(month_value.year - 1, 12, 1)
        else:
            previous_month = date(month_value.year, month_value.month - 1, 1)
        return self.graph_repo.get_graph_by_month(previous_month)

    @staticmethod
    def _enrich_metric(metric: dict, voting_count: int, node_count: int) -> dict:
        triads_total = metric.get("triads_total", 0) or 0
        three_positive = metric.get("three_positive_triads", 0) or 0
        two_positive = metric.get("two_positive_triads", 0) or 0
        one_positive = metric.get("one_positive_triads", 0) or 0
        zero_positive = metric.get("zero_positive_triads", 0) or 0

        balanced_triads = three_positive + one_positive
        balanced_triads_ratio = (balanced_triads / triads_total) if triads_total > 0 else None
        unbalanced_triads_ratio = ((two_positive + zero_positive) / triads_total) if triads_total > 0 else None
        one_positive_share_among_balanced = (
            (one_positive / balanced_triads) if balanced_triads > 0 else None
        )

        return {
            "polarization_index": metric.get("polarization_index"),
            "triads_total": triads_total,
            "balanced_triads_ratio": balanced_triads_ratio,
            "unbalanced_triads_ratio": unbalanced_triads_ratio,
            "one_positive_share_among_balanced": one_positive_share_among_balanced,
            "voting_count": voting_count,
            "node_count": node_count,
            "raw": metric,
        }

    def get_current_metrics(
        self,
        legislature: int | None = None,
        year: int | None = None,
        month: str | None = None,
    ) -> dict:
        cache_key = self.cache.make_key(
            "metrics:get_current_metrics:v1",
            legislature=legislature,
            year=year,
            month=month,
        )

        def _build() -> dict:
            provided_filters = [legislature is not None, year is not None, month is not None]
            if sum(provided_filters) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Provide exactly one filter: legislature, year, or month.",
                )

            if legislature is not None:
                graph = self.graph_repo.get_graph_by_legislature(legislature)
                granularity = "legislature"
            elif year is not None:
                graph = self.graph_repo.get_graph_by_year(year)
                granularity = "year"
            else:
                graph = self.graph_repo.get_graph_by_month(self._parse_month_identifier(month))
                granularity = "month"

            if not graph:
                raise HTTPException(status_code=404, detail="Graph not found for provided identifier")

            all_graphs = self.graph_repo.get_all_graphs()
            same_granularity_graphs = [
                g for g in all_graphs if g.get("time_granularity_id") == graph.get("time_granularity_id")
            ]
            same_granularity_graphs = self._sort_graphs_by_granularity(
                same_granularity_graphs,
                granularity,
                descending=True,
            )

            graph_ids = [g["id"] for g in same_granularity_graphs]
            metrics_rows = self.pol_repo.get_metrics_by_graph_ids(graph_ids)
            metrics_by_graph_id = {m["graph_id"]: m for m in metrics_rows}
            current_metric_row = metrics_by_graph_id.get(graph["id"])
            if not current_metric_row:
                raise HTTPException(status_code=404, detail="Metrics not found for provided graph")

            voting_count_rows = self.graph_repo.get_graph_voting_counts_by_graph_ids(graph_ids)
            voting_count_by_graph_id = {row["graph_id"]: row["voting_count"] for row in voting_count_rows}
            node_count_rows = self.graph_repo.get_node_counts_by_graph_ids(graph_ids)
            node_count_by_graph_id = {row["graph_id"]: row["node_count"] for row in node_count_rows}

            previous_graph = self._get_previous_graph(graph, granularity)
            previous_metric_row = (
                metrics_by_graph_id.get(previous_graph["id"]) if previous_graph else None
            )

            current_pol = current_metric_row.get("polarization_index")
            previous_pol = previous_metric_row.get("polarization_index") if previous_metric_row else None

            return {
                "granularity": granularity,
                "current": {
                    "graph": graph,
                    "identifier": self._graph_identifier(graph),
                    "metrics": self._enrich_metric(
                        current_metric_row,
                        voting_count_by_graph_id.get(graph["id"], 0),
                        node_count_by_graph_id.get(graph["id"], 0),
                    ),
                },
                "previous": (
                    {
                        "graph": previous_graph,
                        "identifier": self._graph_identifier(previous_graph),
                        "metrics": self._enrich_metric(
                            previous_metric_row,
                            voting_count_by_graph_id.get(previous_graph["id"], 0),
                            node_count_by_graph_id.get(previous_graph["id"], 0),
                        ),
                    }
                    if previous_graph and previous_metric_row
                    else None
                ),
                "variation": {
                    "delta_polarization_index": (
                        (current_pol - previous_pol) if previous_pol is not None else None
                    ),
                    "delta_polarization_index_pct": self._percent_change(current_pol, previous_pol),
                    "trend": self._trend(current_pol, previous_pol),
                },
            }

        return self.cache.get_or_set(cache_key, _build)

    def get_metrics_timeseries(self, granularity: str) -> list[dict]:
        cache_key = self.cache.make_key(
            "metrics:get_metrics_timeseries:v1",
            granularity=granularity,
        )

        def _build() -> list[dict]:
            gran_map = {"legislature": 1, "year": 2, "month": 3}
            if granularity not in gran_map:
                raise HTTPException(status_code=400, detail="Invalid granularity. Must be legislature, year, or month.")

            gran_id = gran_map[granularity]
            graphs = self.graph_repo.get_all_graphs()

            filtered_graphs = [g for g in graphs if g["time_granularity_id"] == gran_id]
            filtered_graphs = self._sort_graphs_by_granularity(filtered_graphs, granularity, descending=False)
            graph_ids = [g["id"] for g in filtered_graphs]
            voting_count_rows = self.graph_repo.get_graph_voting_counts_by_graph_ids(graph_ids)
            node_count_rows = self.graph_repo.get_node_counts_by_graph_ids(graph_ids)
            voting_count_by_graph_id = {row["graph_id"]: row["voting_count"] for row in voting_count_rows}
            node_count_by_graph_id = {row["graph_id"]: row["node_count"] for row in node_count_rows}

            history = []
            for graph in filtered_graphs:
                metric = self.pol_repo.get_metric_by_graph(graph["id"])
                if metric:
                    history.append(
                        {
                            "graph": graph,
                            "metrics": self._enrich_metric(
                                metric,
                                voting_count_by_graph_id.get(graph["id"], 0),
                                node_count_by_graph_id.get(graph["id"], 0),
                            ),
                        }
                    )
            return history

        return self.cache.get_or_set(cache_key, _build)
