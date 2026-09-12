"""In-memory fakes for the domain ports, used to unit test application use
cases without touching Django/Kafka/the filesystem."""

from __future__ import annotations

from domain.entities import AgentRole, Project, RunLog, Team
from domain.exceptions import UnknownProjectError, UnknownRoleError
from domain.ports import (
    AgentRoleRepository,
    EventPublisher,
    ProjectRepository,
    RunLogRepository,
    ScaffoldWriter,
    TeamRepository,
)


class FakeAgentRoleRepository(AgentRoleRepository):
    def __init__(self, roles=()):
        self._roles = {role.slug: role for role in roles}

    def list_all(self):
        return list(self._roles.values())

    def get(self, slug: str) -> AgentRole:
        try:
            return self._roles[slug]
        except KeyError:
            raise UnknownRoleError(slug) from None

    def upsert(self, role: AgentRole) -> None:
        self._roles[role.slug] = role


class FakeProjectRepository(ProjectRepository):
    def __init__(self):
        self._projects: dict[str, Project] = {}

    def save(self, project: Project) -> None:
        self._projects[project.slug] = project

    def get(self, slug: str) -> Project:
        try:
            return self._projects[slug]
        except KeyError:
            raise UnknownProjectError(slug) from None

    def list_all(self):
        return list(self._projects.values())

    def exists(self, slug: str) -> bool:
        return slug in self._projects


class FakeTeamRepository(TeamRepository):
    def __init__(self):
        self._teams: dict[str, Team] = {}

    def save(self, team: Team) -> None:
        self._teams[team.project_slug] = team

    def get_for_project(self, project_slug: str) -> Team:
        return self._teams.get(project_slug, Team(project_slug=project_slug))


class FakeRunLogRepository(RunLogRepository):
    def __init__(self):
        self.saved: list[RunLog] = []

    def save(self, run_log: RunLog) -> None:
        self.saved.append(run_log)

    def latest_for_project(self, project_slug: str):
        matches = [r for r in self.saved if r.project_slug == project_slug]
        return matches[-1] if matches else None


class FakeScaffoldWriter(ScaffoldWriter):
    def __init__(self):
        self.calls = []

    def write(self, project: Project, team: Team, roles) -> None:
        self.calls.append((project, team, list(roles)))


class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.published: list[str] = []

    def publish_run_requested(self, project_slug: str) -> None:
        self.published.append(project_slug)
