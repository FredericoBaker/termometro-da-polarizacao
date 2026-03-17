from datetime import date, datetime

from fastapi import HTTPException

from termopol_db.repositories.graph import EdgeRepository, GraphRepository
from termopol_db.repositories.normalized import NormalizedDeputyRepository


class RankingsService:
    def __init__(
        self,
        graph_repo: GraphRepository,
        edge_repo: EdgeRepository,
        deputy_repo: NormalizedDeputyRepository,
    ) -> None:
        self.graph_repo = graph_repo
        self.edge_repo = edge_repo
        self.deputy_repo = deputy_repo

    @staticmethod
    def _parse_month_identifier(month: str) -> date:
        formats = ("%Y-%m", "%m-%Y")
        for fmt in formats:
            try:
                parsed = datetime.strptime(month, fmt)
                return date(parsed.year, parsed.month, 1)
            except ValueError:
                continue
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM or MM-YYYY.")

    def _resolve_graph(
        self,
        legislature: int | None = None,
        year: int | None = None,
        month: str | None = None,
    ) -> dict:
        provided = [legislature is not None, year is not None, month is not None]
        if sum(provided) != 1:
            raise HTTPException(status_code=400, detail="Provide exactly one filter: legislature, year, or month.")

        if legislature is not None:
            graph = self.graph_repo.get_graph_by_legislature(legislature)
        elif year is not None:
            graph = self.graph_repo.get_graph_by_year(year)
        else:
            graph = self.graph_repo.get_graph_by_month(self._parse_month_identifier(month))

        if not graph:
            raise HTTPException(status_code=404, detail="Graph not found for provided identifier")
        return graph

    @staticmethod
    def _deputy_payload(deputy: dict | None, party_row: dict | None) -> dict | None:
        if not deputy:
            return None
        external_id = deputy.get("external_id")
        return {
            "id": deputy.get("id"),
            "external_id": external_id,
            "name": deputy.get("name"),
            "state_code": deputy.get("state_code"),
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
        }

    def get_rankings(
        self,
        legislature: int | None = None,
        year: int | None = None,
        month: str | None = None,
        limit: int = 10,
    ) -> dict:
        graph = self._resolve_graph(legislature=legislature, year=year, month=month)
        graph_id = graph["id"]

        top_agreements = self.edge_repo.get_top_agreement_edges_by_graph(graph_id, limit=limit)
        top_disagreements = self.edge_repo.get_top_disagreement_edges_by_graph(graph_id, limit=limit)

        edge_rows = top_agreements + top_disagreements
        deputy_ids = sorted({d for edge in edge_rows for d in (edge["deputy_a"], edge["deputy_b"])})
        deputies = self.deputy_repo.get_deputies_by_ids(deputy_ids)
        deputy_map = {row["id"]: row for row in deputies}

        if graph.get("legislature") is not None:
            party_rows = self.deputy_repo.get_terms_with_party_by_deputies_and_legislature(
                deputy_ids,
                graph["legislature"],
            )
        else:
            party_rows = self.deputy_repo.get_latest_terms_with_party_by_deputies(deputy_ids)
        party_map = {row["deputy_id"]: row for row in party_rows}

        def _format_edge(edge: dict) -> dict:
            deputy_a_id = edge["deputy_a"]
            deputy_b_id = edge["deputy_b"]
            return {
                "id": f'{graph_id}:{deputy_a_id}-{deputy_b_id}',
                "graph_id": graph_id,
                "deputy_a_id": deputy_a_id,
                "deputy_b_id": deputy_b_id,
                "w_signed": edge.get("w_signed"),
                "abs_w": edge.get("abs_w"),
                "is_backbone": edge.get("is_backbone"),
                "deputy_a": self._deputy_payload(deputy_map.get(deputy_a_id), party_map.get(deputy_a_id)),
                "deputy_b": self._deputy_payload(deputy_map.get(deputy_b_id), party_map.get(deputy_b_id)),
            }

        return {
            "graph": graph,
            "top_agreements": [_format_edge(edge) for edge in top_agreements],
            "top_disagreements": [_format_edge(edge) for edge in top_disagreements],
        }
