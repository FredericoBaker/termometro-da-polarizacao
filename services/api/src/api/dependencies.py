from functools import lru_cache

from api.cache import ApiCache
from termopol_db.connection import get_db_pool
from termopol_db.repositories.graph import PolarizationMetricRepository, GraphRepository, EdgeRepository
from termopol_db.repositories.normalized import NormalizedDeputyRepository, NormalizedPartyRepository
from api.services import DeputiesService, GraphsService, MetricsService, RankingsService, HealthService

def get_polarization_repo() -> PolarizationMetricRepository:
    return PolarizationMetricRepository()

def get_graph_repo() -> GraphRepository:
    return GraphRepository()

def get_edge_repo() -> EdgeRepository:
    return EdgeRepository()

def get_deputy_repo() -> NormalizedDeputyRepository:
    return NormalizedDeputyRepository()

def get_party_repo() -> NormalizedPartyRepository:
    return NormalizedPartyRepository()

@lru_cache(maxsize=1)
def get_cache() -> ApiCache:
    return ApiCache()


def get_deputies_service() -> DeputiesService:
    return DeputiesService(
        deputy_repo=get_deputy_repo(),
        graph_repo=get_graph_repo(),
        edge_repo=get_edge_repo(),
        cache=get_cache(),
    )


def get_graphs_service() -> GraphsService:
    return GraphsService(
        graph_repo=get_graph_repo(),
        edge_repo=get_edge_repo(),
        deputy_repo=get_deputy_repo(),
        cache=get_cache(),
    )


def get_metrics_service() -> MetricsService:
    return MetricsService(
        pol_repo=get_polarization_repo(),
        graph_repo=get_graph_repo(),
        cache=get_cache(),
    )


def get_rankings_service() -> RankingsService:
    return RankingsService(
        graph_repo=get_graph_repo(),
        edge_repo=get_edge_repo(),
        deputy_repo=get_deputy_repo(),
        cache=get_cache(),
    )


def get_health_service() -> HealthService:
    return HealthService(db_pool=get_db_pool())
