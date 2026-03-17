from fastapi import APIRouter, Depends, Query

from api.dependencies import get_metrics_service
from api.services import MetricsService

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])

@router.get("/")
def get_current_metrics(
    legislature: int | None = None,
    year: int | None = None,
    month: str | None = None,
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    return metrics_service.get_current_metrics(
        legislature=legislature,
        year=year,
        month=month,
    )


@router.get("/timeseries")
def get_metrics_timeseries(
    granularity: str = Query("legislature", description="granularity: legislature, year, month"),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    return metrics_service.get_metrics_timeseries(granularity)
