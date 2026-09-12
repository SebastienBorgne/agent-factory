from __future__ import annotations

import re
from enum import Enum

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class AgentMode(str, Enum):
    PRIMARY = "primary"
    SUBAGENT = "subagent"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class RunStatus(str, Enum):
    REQUESTED = "requested"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def slugify_strict(value: str) -> str:
    """Turn arbitrary text into a lowercase-hyphen slug, without any Django dependency."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"cannot derive a slug from {value!r}")
    return slug


def is_valid_slug(value: str) -> bool:
    return bool(_SLUG_RE.match(value))
