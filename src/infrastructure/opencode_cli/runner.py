from __future__ import annotations

import subprocess
from datetime import UTC, datetime

from domain.entities import Project, RunLog
from domain.ports import TeamRunner
from domain.value_objects import RunStatus

_LOG_TAIL_CHARS = 4000


class OpenCodeRunner(TeamRunner):
    """Shells out to the `opencode` CLI to drive a generated project's
    project-manager agent. One call = one PM run; the PM itself delegates to
    subagents in-process via OpenCode's Task tool."""

    def __init__(self, timeout_seconds: int = 60 * 30):
        self.timeout_seconds = timeout_seconds

    def run_project_manager(self, project: Project) -> RunLog:
        started_at = datetime.now(UTC)
        try:
            result = subprocess.run(
                ["opencode", "run", "--agent", "project-manager", project.brief],
                cwd=project.output_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,  # non-zero exit is a normal, handled outcome here, not an error
            )
            status = RunStatus.SUCCEEDED if result.returncode == 0 else RunStatus.FAILED
            log_tail = (result.stdout + result.stderr)[-_LOG_TAIL_CHARS:]
        except (OSError, subprocess.TimeoutExpired) as exc:
            status = RunStatus.FAILED
            log_tail = str(exc)

        return RunLog(
            project_slug=project.slug,
            status=status,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            log_tail=log_tail,
        )
