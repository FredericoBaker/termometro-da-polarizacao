from fastapi import APIRouter, Depends

from api.dependencies import get_deputies_service
from api.services import DeputiesService

router = APIRouter(prefix="/api/v1/deputies", tags=["Deputies"])

@router.get("/{deputy_id}")
def get_deputy(
    deputy_id: int,
    deputies_service: DeputiesService = Depends(get_deputies_service),
):
    return deputies_service.get_deputy(deputy_id)

@router.get("/{deputy_id}/subgraph")
def get_deputy_subgraph(
    deputy_id: int,
    legislature: int | None = None,
    year: int | None = None,
    month: str | None = None,
    deputies_service: DeputiesService = Depends(get_deputies_service),
):
    return deputies_service.get_deputy_subgraph(
        deputy_id=deputy_id,
        legislature=legislature,
        year=year,
        month=month,
    )
