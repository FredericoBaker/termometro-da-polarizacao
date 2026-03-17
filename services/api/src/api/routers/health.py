from fastapi import APIRouter, Depends

from api.dependencies import get_health_service
from api.services import HealthService

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check(health_service: HealthService = Depends(get_health_service)):
    return health_service.health_check()
