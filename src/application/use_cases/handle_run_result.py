from __future__ import annotations

from datetime import UTC, datetime

from domain.entities import RunLog
from domain.ports import RunLogRepository
from domain.value_objects import RunStatus


def handle_run_result(
    run_log_repo: RunLogRepository,
    *,
    project_slug: str,
    status: RunStatus,
    log_tail: str = "",
) -> RunLog:
    """Called by the Kafka consumer adapter once `opencode run` for a
    project's PM agent finishes (or fails to start)."""
    run_log = RunLog(
        project_slug=project_slug,
        status=status,
        finished_at=datetime.now(UTC),
        log_tail=log_tail,
    )
    run_log_repo.save(run_log)
    return run_log
