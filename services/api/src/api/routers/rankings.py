from fastapi import APIRouter, Depends, Query

from api.dependencies import get_rankings_service
from api.services import RankingsService

router = APIRouter(prefix="/api/v1/rankings", tags=["Rankings"])

@router.get("/")
def get_rankings(
    legislature: int | None = None,
    year: int | None = None,
    month: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    rankings_service: RankingsService = Depends(get_rankings_service),
):
    return rankings_service.get_rankings(
        legislature=legislature,
        year=year,
        month=month,
        limit=limit,
    )
