from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .value_objects import AgentMode, RunStatus


@dataclass(frozen=True)
class Skill:
    slug: str
    name: str
    description: str
    content_md: str


@dataclass(frozen=True)
class AgentRole:
    slug: str
    name: str
    description: str
    mode: AgentMode
    guidelines_md: str
    skills: tuple[Skill, ...] = ()


@dataclass(frozen=True)
class Team:
    project_slug: str
    member_role_slugs: tuple[str, ...] = ()


@dataclass
class Project:
    slug: str
    name: str
    brief: str
    output_path: str
    created_at: datetime


@dataclass
class RunLog:
    project_slug: str
    status: RunStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    log_tail: str = ""
