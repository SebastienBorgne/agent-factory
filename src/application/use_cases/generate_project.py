from __future__ import annotations

from domain.entities import Project
from domain.ports import AgentRoleRepository, ProjectRepository, ScaffoldWriter, TeamRepository


def generate_project(
    project_repo: ProjectRepository,
    team_repo: TeamRepository,
    role_repo: AgentRoleRepository,
    scaffold_writer: ScaffoldWriter,
    *,
    project_slug: str,
) -> Project:
    project = project_repo.get(project_slug)
    team = team_repo.get_for_project(project_slug)
    roles = [role_repo.get(role_slug) for role_slug in team.member_role_slugs]

    scaffold_writer.write(project, team, roles)

    return project
