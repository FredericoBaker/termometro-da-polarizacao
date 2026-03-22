"""
Production pipeline runner.

Determines the data window automatically from the last successful execution
recorded in termopol.ingestion_log, then runs all pipeline steps and persists
the run result (completed / failed + error traceback) back to the DB.

Usage examples:
    # Normal daily run (auto window from last completed run)
    python services/pipeline/run.py

    # Override overlap (default 3 days)
    python services/pipeline/run.py --overlap-days 7

    # Force a specific window
    python services/pipeline/run.py --start-date 2024-01-01 --end-date 2024-06-30

    # Verbose logging
    python services/pipeline/run.py --verbose
"""

import argparse
import json
import logging
import sys
import time
import traceback
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Repo root is two levels up from this file (services/pipeline/run.py).
_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "services/pipeline/src"))
sys.path.insert(0, str(_REPO_ROOT / "libs/termopol_db/src"))

from pipeline.graph.build import BuildGraph
from pipeline.ingest import DeputiesIngestor, PartiesIngestor, VotingsIngestor
from pipeline.metrics import MetricsRunner
from pipeline.transform.deputies import DeputyTransformer
from pipeline.transform.parties import PartyTransformer
from pipeline.transform.rollcalls import RollCallTransformer
from pipeline.transform.votings import VotingTransformer
from termopol_db.repositories import IngestionLogRepository

# The earliest date from which the pipeline can fetch data.
EPOCH_START = datetime(1987, 2, 1)

logger = logging.getLogger("pipeline_runner")
STANDARD_LOG_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class DynamicExtraFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in STANDARD_LOG_RECORD_ATTRS and not key.startswith("_")
        }
        if not extras:
            return message
        return f"{message} | extra={json.dumps(extras, ensure_ascii=True, default=str, sort_keys=True)}"


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(DynamicExtraFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def current_utc_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def parse_datetime(value: str) -> datetime:
    try:
        if len(value) == 10:
            return datetime.strptime(value, "%Y-%m-%d")
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime '{value}'. Use YYYY-MM-DD or ISO format."
        ) from exc


def determine_window(
    log_repo: IngestionLogRepository,
    overlap_days: int,
    start_override: datetime | None,
    end_override: datetime | None,
) -> tuple[datetime, datetime]:
    """
    Return (start_date, end_date) for the current pipeline run.

    If --start-date / --end-date are provided they take full precedence.
    Otherwise the window is derived from the last completed run:
        start_date = max(EPOCH_START, last_end_logic_ts - overlap_days)
        end_date   = now()
    """
    end_date = end_override or current_utc_naive()

    if start_override:
        return start_override, end_date

    last = log_repo.get_last_completed()
    if last and last.get("end_logic_ts"):
        last_end = last["end_logic_ts"]
        if hasattr(last_end, "tzinfo") and last_end.tzinfo is not None:
            last_end = last_end.replace(tzinfo=None)
        start_date = max(EPOCH_START, last_end - timedelta(days=overlap_days))
    else:
        logger.info(
            "No completed run found; starting from EPOCH_START",
            extra={"epoch": EPOCH_START.isoformat()},
        )
        start_date = EPOCH_START

    return start_date, end_date


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------


def run_ingest(start_date: datetime, end_date: datetime) -> None:
    logger.info(
        "Running ingest step",
        extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    PartiesIngestor(start_date, end_date=end_date).ingest()
    DeputiesIngestor(start_date, end_date=end_date).ingest()
    VotingsIngestor(start_date, end_date=end_date).ingest()
    logger.info("Ingest step completed")


def run_transform() -> None:
    logger.info("Running transform step")
    PartyTransformer().transform()
    DeputyTransformer().transform()
    VotingTransformer().transform()
    RollCallTransformer().transform()
    logger.info("Transform step completed")


def run_graph() -> None:
    logger.info("Running graph step")
    BuildGraph().build()
    logger.info("Graph step completed")


def run_metrics() -> None:
    logger.info("Running all graph metrics (Backbone, Polarization, Layout, PageRank)")
    MetricsRunner().run_all()
    logger.info("All graph metrics completed")

def run_step(name: str, fn) -> None:
    started_at = time.time()
    logger.info("Starting step", extra={"step": name})
    fn()
    elapsed = round(time.time() - started_at, 2)
    logger.info("Finished step", extra={"step": name, "elapsed_seconds": elapsed})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Production pipeline runner. Runs all steps and persists the result to ingestion_log."
    )
    parser.add_argument(
        "--overlap-days",
        type=int,
        default=3,
        help=(
            "Days of overlap with the previous completed run window "
            "(default: 3). Ignored when --start-date is set."
        ),
    )
    parser.add_argument(
        "--start-date",
        type=parse_datetime,
        default=None,
        help="Override start date (YYYY-MM-DD or ISO). Skips auto-window logic.",
    )
    parser.add_argument(
        "--end-date",
        type=parse_datetime,
        default=None,
        help="Override end date (YYYY-MM-DD or ISO). Defaults to now().",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    log_repo = IngestionLogRepository()

    start_date, end_date = determine_window(
        log_repo=log_repo,
        overlap_days=args.overlap_days,
        start_override=args.start_date,
        end_override=args.end_date,
    )

    if start_date >= end_date:
        logger.error(
            "start_date must be before end_date; aborting",
            extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        )
        sys.exit(1)

    logger.info(
        "Starting production pipeline run",
        extra={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "overlap_days": args.overlap_days,
        },
    )

    log_entry = log_repo.insert_ingestion_log(start_date, end_date)
    if not log_entry:
        logger.error("Failed to insert ingestion_log entry; aborting")
        sys.exit(1)

    log_id = log_entry["id"]
    log_repo.mark_in_progress(log_id)

    try:
        run_step("ingest", lambda: run_ingest(start_date, end_date))
        run_step("transform", run_transform)
        run_step("graph", run_graph)
        run_step("metrics", run_metrics)

        log_repo.mark_completed(log_id)
        logger.info(
            "Pipeline run completed successfully",
            extra={
                "log_id": log_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

    except Exception:
        error_msg = traceback.format_exc()
        log_repo.mark_failed(log_id, error_msg)
        logger.exception(
            "Pipeline run failed; status recorded in ingestion_log",
            extra={"log_id": log_id},
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
