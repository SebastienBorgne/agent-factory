from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

from .entities import AgentRole, Project, RunLog, Team


class AgentRoleRepository(ABC):
    @abstractmethod
    def list_all(self) -> Sequence[AgentRole]: ...

    @abstractmethod
    def get(self, slug: str) -> AgentRole: ...

    @abstractmethod
    def upsert(self, role: AgentRole) -> None: ...


class ProjectRepository(ABC):
    @abstractmethod
    def save(self, project: Project) -> None: ...

    @abstractmethod
    def get(self, slug: str) -> Project: ...

    @abstractmethod
    def list_all(self) -> Sequence[Project]: ...

    @abstractmethod
    def exists(self, slug: str) -> bool: ...


class TeamRepository(ABC):
    @abstractmethod
    def save(self, team: Team) -> None: ...

    @abstractmethod
    def get_for_project(self, project_slug: str) -> Team: ...


class RunLogRepository(ABC):
    @abstractmethod
    def save(self, run_log: RunLog) -> None: ...

    @abstractmethod
    def latest_for_project(self, project_slug: str) -> RunLog | None: ...


class ScaffoldWriter(ABC):
    """Writes the generated team folder: opencode config, tracking.json,
    docker-compose (Infisical for secrets), and docs."""

    @abstractmethod
    def write(self, project: Project, team: Team, roles: Sequence[AgentRole]) -> None: ...


class TeamRunner(ABC):
    @abstractmethod
    def run_project_manager(self, project: Project) -> RunLog: ...


class EventPublisher(ABC):
    @abstractmethod
    def publish_run_requested(self, project_slug: str) -> None: ...


class EventConsumer(ABC):
    @abstractmethod
    def consume_forever(self, handler: Callable[[str], None]) -> None: ...
