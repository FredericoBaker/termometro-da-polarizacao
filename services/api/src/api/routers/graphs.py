from fastapi import APIRouter, Depends

from api.dependencies import get_graphs_service
from api.services import GraphsService

router = APIRouter(prefix="/api/v1/graphs", tags=["Graphs"])

@router.get("/available")
def get_available_graphs(
    graphs_service: GraphsService = Depends(get_graphs_service),
):
    return graphs_service.get_available_graphs()


@router.get("/")
def get_graph_details(
    legislature: int | None = None,
    year: int | None = None,
    month: str | None = None,
    graphs_service: GraphsService = Depends(get_graphs_service),
):
    return graphs_service.get_graph_details(
        legislature=legislature,
        year=year,
        month=month,
    )
