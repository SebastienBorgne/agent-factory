from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from domain.entities import Project, Team
from domain.exceptions import EmptyTeamError, ProjectAlreadyExistsError
from domain.ports import AgentRoleRepository, ProjectRepository, TeamRepository


def build_team(
    project_repo: ProjectRepository,
    team_repo: TeamRepository,
    role_repo: AgentRoleRepository,
    *,
    slug: str,
    name: str,
    brief: str,
    output_root: str,
    member_role_slugs: Sequence[str],
) -> Project:
    if not member_role_slugs:
        raise EmptyTeamError()
    if project_repo.exists(slug):
        raise ProjectAlreadyExistsError(slug)

    for role_slug in member_role_slugs:
        role_repo.get(role_slug)  # raises UnknownRoleError if missing

    project = Project(
        slug=slug,
        name=name,
        brief=brief,
        output_path=str(Path(output_root) / slug),
        created_at=datetime.now(UTC),
    )
    project_repo.save(project)
    team_repo.save(Team(project_slug=slug, member_role_slugs=tuple(member_role_slugs)))
    return project
