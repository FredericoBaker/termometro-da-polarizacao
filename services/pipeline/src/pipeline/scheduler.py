import logging
import os
import subprocess
import sys
import time
from datetime import UTC, datetime

from croniter import croniter

logger = logging.getLogger("pipeline_scheduler")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )


def seconds_until_next_run(schedule_cron: str) -> int:
    now = datetime.now(UTC)
    next_run = croniter(schedule_cron, now).get_next(datetime)
    return max(int((next_run - now).total_seconds()), 1)


def run_pipeline_once() -> int:
    cmd = [sys.executable, "services/pipeline/run.py"]
    logger.info("Triggering scheduled pipeline run", extra={"command": " ".join(cmd)})
    completed = subprocess.run(cmd, check=False)
    logger.info("Scheduled pipeline run finished", extra={"exit_code": completed.returncode})
    return completed.returncode


def main() -> None:
    setup_logging()

    schedule_cron = os.getenv("PIPELINE_SCHEDULE_CRON", "0 3 * * *")
    if not croniter.is_valid(schedule_cron):
        raise ValueError(
            "Invalid PIPELINE_SCHEDULE_CRON. Expected standard 5-field cron expression."
        )

    logger.info(
        "Starting pipeline scheduler",
        extra={"schedule_cron": schedule_cron, "timezone": "UTC"},
    )

    while True:
        sleep_seconds = seconds_until_next_run(schedule_cron)
        logger.info(
            "Sleeping until next scheduled run",
            extra={"sleep_seconds": sleep_seconds, "schedule_cron": schedule_cron},
        )
        time.sleep(sleep_seconds)
        run_pipeline_once()


if __name__ == "__main__":
    main()
