from datetime import date, datetime

from fastapi import HTTPException

from api.cache import ApiCache
from termopol_db.repositories.graph import EdgeRepository, GraphRepository
from termopol_db.repositories.normalized import NormalizedDeputyRepository


class DeputiesService:
    def __init__(
        self,
        deputy_repo: NormalizedDeputyRepository,
        graph_repo: GraphRepository,
        edge_repo: EdgeRepository,
        cache: ApiCache,
    ) -> None:
        self.deputy_repo = deputy_repo
        self.graph_repo = graph_repo
        self.edge_repo = edge_repo
        self.cache = cache

    @staticmethod
    def _format_month_year(month_value: date | None) -> str | None:
        if not month_value:
            return None
        return month_value.strftime("%m-%Y")

    def get_deputy(self, deputy_id: int) -> dict:
        def _build() -> dict:
            deputy = self.deputy_repo.get_deputy_by_id(deputy_id)
            if not deputy:
                raise HTTPException(status_code=404, detail="Deputy not found")

            terms = self.deputy_repo.get_terms_by_deputy(deputy["id"])
            latest_term = self.deputy_repo.get_latest_term_with_party_by_deputy(deputy["id"])
            graph_rows = self.graph_repo.get_graphs_by_deputy(deputy["id"])

            legislature_graphs = []
            year_graphs = []
            month_graphs = []

            for row in graph_rows:
                granularity_id = row.get("time_granularity_id")
                if granularity_id == 1:
                    legislature_graphs.append(
                        {
                            "graph_id": row["graph_id"],
                            "legislature": row.get("legislature"),
                        }
                    )
                elif granularity_id == 2:
                    year_graphs.append(
                        {
                            "graph_id": row["graph_id"],
                            "year": row.get("year"),
                        }
                    )
                elif granularity_id == 3:
                    month_graphs.append(
                        {
                            "graph_id": row["graph_id"],
                            "month": self._format_month_year(row.get("month")),
                        }
                    )

            external_id = deputy.get("external_id")
            photo_url = (
                f"https://www.camara.leg.br/internet/deputado/bandep/{external_id}.jpg"
                if external_id
                else None
            )

            latest_party = None
            if latest_term:
                latest_party = {
                    "legislature": latest_term.get("legislature_id"),
                    "party": {
                        "id": latest_term.get("party_id"),
                        "external_id": latest_term.get("party_external_id"),
                        "code": latest_term.get("party_code"),
                        "name": latest_term.get("party_name"),
                        "uri": latest_term.get("party_uri"),
                    },
                }

            return {
                "deputy": {
                    **deputy,
                    "photo_url": photo_url,
                },
                "terms": terms,
                "latest_party": latest_party,
                "graphs_by_granularity": {
                    "legislature": legislature_graphs,
                    "year": year_graphs,
                    "month": month_graphs,
                },
            }

        cache_key = self.cache.make_key("deputies:get_deputy:v1", deputy_id=deputy_id)
        return self.cache.get_or_set(cache_key, _build)

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

    def get_deputy_subgraph(
        self,
        deputy_id: int,
        legislature: int | None = None,
        year: int | None = None,
        month: str | None = None,
    ) -> dict:
        cache_key = self.cache.make_key(
            "deputies:get_deputy_subgraph:v1",
            deputy_id=deputy_id,
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
                graph_identifier = f"legislature {legislature}"
            elif year is not None:
                graph = self.graph_repo.get_graph_by_year(year)
                graph_identifier = f"year {year}"
            else:
                month_date = self._parse_month_identifier(month)
                graph = self.graph_repo.get_graph_by_month(month_date)
                graph_identifier = f"month {month}"

            if not graph:
                raise HTTPException(status_code=404, detail=f"Graph for {graph_identifier} not found")

            graph_id = graph["id"]
            subgraph_edges = self.edge_repo.get_backbone_edges_by_deputy(graph_id, deputy_id)
            connected_deputy_ids = {deputy_id}
            for edge in subgraph_edges:
                connected_deputy_ids.add(edge["deputy_a"])
                connected_deputy_ids.add(edge["deputy_b"])

            deputy_ids = sorted(connected_deputy_ids)
            deputies = self.deputy_repo.get_deputies_by_ids(deputy_ids)
            deputy_map = {row["id"]: row for row in deputies}

            node_positions = self.graph_repo.get_nodes_by_deputies(graph_id, deputy_ids)
            position_map = {row["deputy_id"]: row for row in node_positions}

            if graph.get("legislature") is not None:
                party_rows = self.deputy_repo.get_terms_with_party_by_deputies_and_legislature(
                    deputy_ids,
                    graph["legislature"],
                )
            else:
                party_rows = self.deputy_repo.get_latest_terms_with_party_by_deputies(deputy_ids)
            party_map = {row["deputy_id"]: row for row in party_rows}

            nodes = []
            for node_id in deputy_ids:
                deputy = deputy_map.get(node_id)
                if not deputy:
                    continue

                party_row = party_map.get(node_id)
                pos = position_map.get(node_id)
                external_id = deputy.get("external_id")

                nodes.append(
                    {
                        "id": node_id,
                        "key": str(node_id),
                        "label": deputy.get("name"),
                        "name": deputy.get("name"),
                        "state_code": deputy.get("state_code"),
                        "external_id": external_id,
                        "photo_url": (
                            f"https://www.camara.leg.br/internet/deputado/bandep/{external_id}.jpg"
                            if external_id
                            else None
                        ),
                        "party": (
                            {
                                "id": party_row.get("party_id"),
                                "external_id": party_row.get("party_external_id"),
                                "code": party_row.get("party_code"),
                                "name": party_row.get("party_name"),
                                "uri": party_row.get("party_uri"),
                                "legislature": party_row.get("legislature_id"),
                            }
                            if party_row
                            else None
                        ),
                        "x": pos.get("x") if pos else None,
                        "y": pos.get("y") if pos else None,
                        "is_focal": node_id == deputy_id,
                    }
                )

            edges = []
            for edge in subgraph_edges:
                source_id = edge["deputy_a"]
                target_id = edge["deputy_b"]
                edges.append(
                    {
                        "id": f"{graph_id}:{source_id}-{target_id}",
                        "source": str(source_id),
                        "target": str(target_id),
                        "source_id": source_id,
                        "target_id": target_id,
                        "w_signed": edge.get("w_signed"),
                        "abs_w": edge.get("abs_w"),
                        "p_deputy_a": edge.get("p_deputy_a"),
                        "p_deputy_b": edge.get("p_deputy_b"),
                        "is_backbone": edge.get("is_backbone"),
                    }
                )

            return {
                "graph": graph,
                "focal_deputy_id": deputy_id,
                "nodes": nodes,
                "edges": edges,
            }

        return self.cache.get_or_set(cache_key, _build)
