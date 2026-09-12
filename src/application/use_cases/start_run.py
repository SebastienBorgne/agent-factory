from __future__ import annotations

from datetime import UTC, datetime

from domain.entities import RunLog
from domain.ports import EventPublisher, ProjectRepository, RunLogRepository
from domain.value_objects import RunStatus


def start_run(
    project_repo: ProjectRepository,
    event_publisher: EventPublisher,
    run_log_repo: RunLogRepository,
    *,
    project_slug: str,
) -> RunLog:
    project = project_repo.get(project_slug)  # raises UnknownProjectError if missing
    event_publisher.publish_run_requested(project.slug)

    run_log = RunLog(
        project_slug=project.slug,
        status=RunStatus.REQUESTED,
        started_at=datetime.now(UTC),
    )
    run_log_repo.save(run_log)
    return run_log
