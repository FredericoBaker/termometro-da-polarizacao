import argparse
import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator, Iterable, Sequence

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "services/pipeline/src"))
sys.path.insert(0, str(Path(__file__).parent / "libs/termopol_db/src"))

from pipeline.ingest import PartiesIngestor, DeputiesIngestor, VotingsIngestor
from pipeline.transform.parties import PartyTransformer
from pipeline.transform.deputies import DeputyTransformer
from pipeline.transform.votings import VotingTransformer
from pipeline.transform.rollcalls import RollCallTransformer
from pipeline.graph.build import BuildGraph
from pipeline.metrics import BackboneMetrics, PolarizationMetrics
from termopol_db.repositories import (
    EdgeRepository,
    GraphRepository,
    NormalizedDeputyRepository,
    NormalizedPartyRepository,
    NormalizedRollcallRepository,
    NormalizedVotingRepository,
    RawDeputyRepository,
    RawPartyRepository,
    RawRollcallRepository,
    RawVotingRepository,
)


logger = logging.getLogger("pipeline_test_runner")
STANDARD_LOG_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())


class DynamicExtraFormatter(logging.Formatter):
    """Append any logging `extra` fields as JSON."""

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


def parse_datetime(value: str) -> datetime:
    try:
        if len(value) == 10:
            return datetime.strptime(value, "%Y-%m-%d")
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime '{value}'. Use YYYY-MM-DD or ISO format."
        ) from exc


def current_utc_naive() -> datetime:
    """Return current UTC datetime as naive, avoiding utcnow() deprecation."""
    return datetime.now(UTC).replace(tzinfo=None)


def count_records(records: Iterable[dict]) -> int:
    return sum(1 for _ in records)


def sample_records(records: Generator[dict, None, None], limit: int) -> list[dict]:
    samples = []
    for record in records:
        samples.append(record)
        if len(samples) >= limit:
            break
    return samples


def run_ingest(start_date: datetime) -> None:
    logger.info("Running ingest step", extra={"start_date": start_date.isoformat()})
    PartiesIngestor(start_date).ingest()
    DeputiesIngestor(start_date).ingest()
    VotingsIngestor(start_date).ingest()
    logger.info("Ingest step completed")


def run_transform(start_date: datetime, end_date: datetime) -> None:
    logger.info(
        "Running transform step",
        extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    PartyTransformer().transform(start_date, end_date)
    DeputyTransformer().transform(start_date, end_date)
    VotingTransformer().transform(start_date, end_date)
    RollCallTransformer().transform(start_date, end_date)
    logger.info("Transform step completed")


def run_graph(start_date: datetime, end_date: datetime) -> None:
    logger.info(
        "Running graph step",
        extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    BuildGraph().build(start_date, end_date)
    logger.info("Graph step completed")


def run_metrics_backbone() -> None:
    logger.info("Running backbone metrics step")
    BackboneMetrics().compute_all_graphs_backbone()
    logger.info("Backbone metrics step completed")


def run_metrics_polarization() -> None:
    logger.info("Running polarization metrics step")
    PolarizationMetrics().compute_all_graphs_polarization()
    logger.info("Polarization metrics step completed")


def validate_ingest(start_date: datetime, end_date: datetime) -> None:
    raw_party_repo = RawPartyRepository()
    raw_deputy_repo = RawDeputyRepository()
    raw_voting_repo = RawVotingRepository()
    raw_rollcall_repo = RawRollcallRepository()

    parties_count = count_records(raw_party_repo.get_parties_by_date_range_generator(start_date, end_date))
    deputies_count = count_records(raw_deputy_repo.get_deputies_by_date_range_generator(start_date, end_date))
    votings_count = count_records(raw_voting_repo.get_votings_by_date_range_generator(start_date, end_date))
    rollcalls_count = count_records(
        raw_rollcall_repo.get_rollcalls_by_date_range_generator(start_date, end_date)
    )

    logger.info(
        "Ingest validation counts",
        extra={
            "raw_parties": parties_count,
            "raw_deputies": deputies_count,
            "raw_votings": votings_count,
            "raw_rollcalls": rollcalls_count,
        },
    )
    if votings_count == 0:
        raise AssertionError("No raw votings found in date range; ingest likely failed.")


def validate_transform(start_date: datetime, end_date: datetime, sample_size: int) -> None:
    raw_party_repo = RawPartyRepository()
    raw_deputy_repo = RawDeputyRepository()
    raw_voting_repo = RawVotingRepository()
    raw_rollcall_repo = RawRollcallRepository()

    normalized_party_repo = NormalizedPartyRepository()
    normalized_deputy_repo = NormalizedDeputyRepository()
    normalized_voting_repo = NormalizedVotingRepository()
    normalized_rollcall_repo = NormalizedRollcallRepository()

    raw_party_samples = sample_records(
        raw_party_repo.get_parties_by_date_range_generator(start_date, end_date), sample_size
    )
    for raw_party in raw_party_samples:
        normalized = normalized_party_repo.get_party_by_external_id(raw_party["id"])
        if not normalized:
            raise AssertionError(f"Missing normalized party for external_id={raw_party['id']}")

    raw_deputy_samples = sample_records(
        raw_deputy_repo.get_deputies_by_date_range_generator(start_date, end_date), sample_size
    )
    for raw_deputy in raw_deputy_samples:
        normalized = normalized_deputy_repo.get_deputy_by_external_id(raw_deputy["id"])
        if not normalized:
            raise AssertionError(f"Missing normalized deputy for external_id={raw_deputy['id']}")

    raw_voting_samples = sample_records(
        raw_voting_repo.get_votings_by_date_range_generator(start_date, end_date), sample_size
    )
    for raw_voting in raw_voting_samples:
        normalized = normalized_voting_repo.get_voting_by_external_id(raw_voting["id"])
        if not normalized:
            raise AssertionError(f"Missing normalized voting for external_id={raw_voting['id']}")

    raw_rollcall_samples = sample_records(
        raw_rollcall_repo.get_rollcalls_by_date_range_generator(start_date, end_date), sample_size
    )
    checked_rollcalls = 0
    for raw_rollcall in raw_rollcall_samples:
        vote = raw_rollcall.get("vote")
        if vote not in ("Sim", "Não"):
            continue

        normalized_voting = normalized_voting_repo.get_voting_by_external_id(raw_rollcall["voting_id"])
        normalized_deputy = normalized_deputy_repo.get_deputy_by_external_id(raw_rollcall["deputy_id"])
        if not normalized_voting or not normalized_deputy:
            continue

        normalized_rollcall = normalized_rollcall_repo.get_rollcall(
            normalized_voting["id"], normalized_deputy["id"]
        )
        if not normalized_rollcall:
            raise AssertionError(
                "Missing normalized rollcall for "
                f"voting_external_id={raw_rollcall['voting_id']} deputy_external_id={raw_rollcall['deputy_id']}"
            )
        checked_rollcalls += 1

    logger.info(
        "Transform validation completed",
        extra={
            "sample_parties": len(raw_party_samples),
            "sample_deputies": len(raw_deputy_samples),
            "sample_votings": len(raw_voting_samples),
            "sample_rollcalls_checked": checked_rollcalls,
        },
    )


def validate_graph(max_graphs_validate: int) -> None:
    graph_repo = GraphRepository()
    edge_repo = EdgeRepository()

    graphs = graph_repo.get_all_graphs()
    if not graphs:
        raise AssertionError("No graphs found; graph build likely failed.")

    graphs_to_validate = graphs[:max_graphs_validate]
    for graph in graphs_to_validate:
        graph_id = graph["id"]
        edges = edge_repo.get_edges_by_graph(graph_id)
        for edge in edges:
            if edge["deputy_a"] >= edge["deputy_b"]:
                raise AssertionError(
                    f"Invalid edge ordering in graph_id={graph_id}: "
                    f"deputy_a={edge['deputy_a']} deputy_b={edge['deputy_b']}"
                )
            if edge["abs_w"] < 0:
                raise AssertionError(
                    f"Negative abs_w in graph_id={graph_id}: abs_w={edge['abs_w']}"
                )

    logger.info(
        "Graph validation completed",
        extra={"graphs_total": len(graphs), "graphs_validated": len(graphs_to_validate)},
    )


def run_step(name: str, fn) -> None:
    started_at = time.time()
    logger.info("Starting step", extra={"step": name})
    fn()
    elapsed = round(time.time() - started_at, 2)
    logger.info("Finished step", extra={"step": name, "elapsed_seconds": elapsed})


def parse_steps(steps_arg: Sequence[str]) -> list[str]:
    if "all" in steps_arg:
        return ["ingest", "transform", "graph", "metrics_backbone", "metrics_polarization"]
    return list(steps_arg)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="End-to-end pipeline smoke test runner.")
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=["all", "ingest", "transform", "graph", "metrics_backbone", "metrics_polarization"],
        default=["all"],
        help="Pipeline steps to run.",
    )
    parser.add_argument(
        "--start-date",
        type=parse_datetime,
        default=datetime(2024, 1, 1),
        help="Start datetime (YYYY-MM-DD or ISO).",
    )
    parser.add_argument(
        "--end-date",
        type=parse_datetime,
        default=current_utc_naive(),
        help="End datetime (YYYY-MM-DD or ISO).",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=20,
        help="Sample size for transform validation checks.",
    )
    parser.add_argument(
        "--max-graphs-validate",
        type=int,
        default=3,
        help="How many graphs to inspect in graph validation.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Run pipeline steps but skip DB validation checks.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logs.",
    )
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.start_date >= args.end_date:
        raise ValueError("start_date must be before end_date.")

    steps = parse_steps(args.steps)
    logger.info(
        "Starting pipeline test runner",
        extra={
            "steps": steps,
            "start_date": args.start_date.isoformat(),
            "end_date": args.end_date.isoformat(),
            "skip_validation": args.skip_validation,
        },
    )

    try:
        if "ingest" in steps:
            run_step("ingest", lambda: run_ingest(args.start_date))
            if not args.skip_validation:
                run_step(
                    "validate_ingest",
                    lambda: validate_ingest(args.start_date, args.end_date),
                )

        if "transform" in steps:
            run_step("transform", lambda: run_transform(args.start_date, args.end_date))
            if not args.skip_validation:
                run_step(
                    "validate_transform",
                    lambda: validate_transform(args.start_date, args.end_date, args.sample_size),
                )

        if "graph" in steps:
            run_step("graph", lambda: run_graph(args.start_date, args.end_date))
            if not args.skip_validation:
                run_step(
                    "validate_graph",
                    lambda: validate_graph(args.max_graphs_validate),
                )

        if "metrics_backbone" in steps:
            run_step("metrics_backbone", run_metrics_backbone)

        if "metrics_polarization" in steps:
            run_step("metrics_polarization", run_metrics_polarization)

        logger.info("All selected steps completed successfully")
    except Exception:
        logger.exception("Pipeline test runner failed")
        sys.exit(1)


if __name__ == "__main__":
    main()