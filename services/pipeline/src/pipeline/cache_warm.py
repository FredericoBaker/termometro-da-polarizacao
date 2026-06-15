import logging
import os

import requests

logger = logging.getLogger("pipeline_cache_warm")

DEFAULT_API_BASE = "http://api:8000"
REQUEST_TIMEOUT_SECONDS = 30
_TRUE_VALUES = {"1", "true", "yes", "on"}


def is_enabled() -> bool:
    return os.getenv("CACHE_WARM_ENABLED", "true").strip().lower() in _TRUE_VALUES


def _base_url() -> str:
    return os.getenv("CACHE_WARM_API_BASE", DEFAULT_API_BASE).rstrip("/")


def _get(session: requests.Session, base: str, path: str, params: dict | None = None):
    url = f"{base}{path}"
    try:
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    except Exception as exc:
        logger.warning(
            "Warm request errored", extra={"path": path, "params": params, "error": str(exc)}
        )
        return None
    if resp.status_code != 200:
        logger.warning(
            "Warm request returned non-200",
            extra={"path": path, "params": params, "status_code": resp.status_code},
        )
        return None
    try:
        return resp.json()
    except ValueError:
        logger.warning("Warm request returned non-JSON", extra={"path": path, "params": params})
        return None


def _warm_all_graphs(session: requests.Session, base: str, available: dict) -> int:
    """Warm the graph page for every available graph across all granularities."""
    warmed = 0
    by_granularity = available.get("graphs_by_granularity", {})

    for entry in by_granularity.get("legislature", []):
        if entry.get("legislature") is not None:
            if _get(session, base, "/v1/graphs/", {"legislature": entry["legislature"]}) is not None:
                warmed += 1
    for entry in by_granularity.get("year", []):
        if entry.get("year") is not None:
            if _get(session, base, "/v1/graphs/", {"year": entry["year"]}) is not None:
                warmed += 1
    for entry in by_granularity.get("month", []):
        if entry.get("month"):
            if _get(session, base, "/v1/graphs/", {"month": entry["month"]}) is not None:
                warmed += 1

    return warmed


def _current_legislature(available: dict) -> int | None:
    legislatures = [
        entry["legislature"]
        for entry in available.get("graphs_by_granularity", {}).get("legislature", [])
        if entry.get("legislature") is not None
    ]
    return max(legislatures) if legislatures else None


def _warm_current_legislature_deputies(
    session: requests.Session, base: str, current_legislature: int
) -> int:
    """Warm the deputy page (detail + default subgraph) for every deputy that
    appears in the current legislature graph."""
    graph = _get(session, base, "/v1/graphs/", {"legislature": current_legislature})
    if not graph:
        logger.warning(
            "Could not fetch current legislature graph; skipping deputy warm",
            extra={"legislature": current_legislature},
        )
        return 0

    deputy_ids = [node["id"] for node in graph.get("nodes", []) if node.get("id") is not None]
    warmed = 0

    for deputy_id in deputy_ids:
        detail = _get(session, base, f"/v1/deputies/{deputy_id}")
        if detail is None:
            continue
        warmed += 1

        legislature_graphs = detail.get("graphs_by_granularity", {}).get("legislature", [])
        default_legislature = (
            legislature_graphs[0].get("legislature") if legislature_graphs else None
        )
        if default_legislature is not None:
            _get(
                session,
                base,
                f"/v1/deputies/{deputy_id}/subgraph",
                {"legislature": default_legislature},
            )

    return warmed


def warm_cache() -> None:
    base = _base_url()
    logger.info("Starting cache warming", extra={"api_base": base})

    with requests.Session() as session:
        available = _get(session, base, "/v1/graphs/available")
        if not available:
            logger.warning("Could not fetch available graphs; aborting cache warming")
            return

        graphs_warmed = _warm_all_graphs(session, base, available)
        logger.info("Warmed graph pages", extra={"graphs_warmed": graphs_warmed})

        current_legislature = _current_legislature(available)
        if current_legislature is None:
            logger.warning("No legislature graphs found; skipping deputy warm")
            deputies_warmed = 0
        else:
            deputies_warmed = _warm_current_legislature_deputies(
                session, base, current_legislature
            )
            logger.info(
                "Warmed deputy pages",
                extra={
                    "deputies_warmed": deputies_warmed,
                    "legislature": current_legislature,
                },
            )

    logger.info(
        "Cache warming finished",
        extra={"graphs_warmed": graphs_warmed, "deputies_warmed": deputies_warmed},
    )
