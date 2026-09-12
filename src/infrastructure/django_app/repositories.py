from __future__ import annotations

from collections.abc import Sequence

from django.db import transaction

from domain.entities import AgentRole, Project, RunLog, Skill, Team
from domain.exceptions import UnknownProjectError, UnknownRoleError
from domain.ports import (
    AgentRoleRepository,
    ProjectRepository,
    RunLogRepository,
    TeamRepository,
)
from domain.value_objects import AgentMode, RunStatus

from .models import (
    AgentRoleModel,
    ProjectModel,
    RunLogModel,
    SkillModel,
    TeamMemberModel,
)


def _role_to_domain(row: AgentRoleModel) -> AgentRole:
    return AgentRole(
        slug=row.slug,
        name=row.name,
        description=row.description,
        mode=AgentMode(row.mode),
        guidelines_md=row.guidelines_md,
        skills=tuple(
            Skill(slug=s.slug, name=s.name, description=s.description, content_md=s.content_md)
            for s in row.skills.all()
        ),
    )


class DjangoAgentRoleRepository(AgentRoleRepository):
    def list_all(self) -> Sequence[AgentRole]:
        return [_role_to_domain(row) for row in AgentRoleModel.objects.prefetch_related("skills")]

    def get(self, slug: str) -> AgentRole:
        try:
            row = AgentRoleModel.objects.prefetch_related("skills").get(slug=slug)
        except AgentRoleModel.DoesNotExist as exc:
            raise UnknownRoleError(slug) from exc
        return _role_to_domain(row)

    @transaction.atomic
    def upsert(self, role: AgentRole) -> None:
        row, _ = AgentRoleModel.objects.update_or_create(
            slug=role.slug,
            defaults={
                "name": role.name,
                "description": role.description,
                "mode": role.mode.value,
                "guidelines_md": role.guidelines_md,
            },
        )
        row.skills.all().delete()
        SkillModel.objects.bulk_create(
            SkillModel(
                role=row,
                slug=skill.slug,
                name=skill.name,
                description=skill.description,
                content_md=skill.content_md,
            )
            for skill in role.skills
        )


class DjangoProjectRepository(ProjectRepository):
    def save(self, project: Project) -> None:
        ProjectModel.objects.update_or_create(
            slug=project.slug,
            defaults={
                "name": project.name,
                "brief": project.brief,
                "output_path": project.output_path,
            },
        )

    def get(self, slug: str) -> Project:
        try:
            row = ProjectModel.objects.get(slug=slug)
        except ProjectModel.DoesNotExist as exc:
            raise UnknownProjectError(slug) from exc
        return Project(
            slug=row.slug,
            name=row.name,
            brief=row.brief,
            output_path=row.output_path,
            created_at=row.created_at,
        )

    def list_all(self) -> Sequence[Project]:
        return [
            Project(
                slug=row.slug,
                name=row.name,
                brief=row.brief,
                output_path=row.output_path,
                created_at=row.created_at,
            )
            for row in ProjectModel.objects.all()
        ]

    def exists(self, slug: str) -> bool:
        return ProjectModel.objects.filter(slug=slug).exists()


class DjangoTeamRepository(TeamRepository):
    @transaction.atomic
    def save(self, team: Team) -> None:
        project = ProjectModel.objects.get(slug=team.project_slug)
        TeamMemberModel.objects.filter(project=project).delete()
        TeamMemberModel.objects.bulk_create(
            TeamMemberModel(project=project, role_id=role_slug) for role_slug in team.member_role_slugs
        )

    def get_for_project(self, project_slug: str) -> Team:
        role_slugs = tuple(
            TeamMemberModel.objects.filter(project_id=project_slug).values_list("role_id", flat=True)
        )
        return Team(project_slug=project_slug, member_role_slugs=role_slugs)


class DjangoRunLogRepository(RunLogRepository):
    def save(self, run_log: RunLog) -> None:
        RunLogModel.objects.create(
            project_id=run_log.project_slug,
            status=run_log.status.value,
            started_at=run_log.started_at,
            finished_at=run_log.finished_at,
            log_tail=run_log.log_tail,
        )

    def latest_for_project(self, project_slug: str) -> RunLog | None:
        row = RunLogModel.objects.filter(project_id=project_slug).order_by("-created_at").first()
        if row is None:
            return None
        return RunLog(
            project_slug=project_slug,
            status=RunStatus(row.status),
            started_at=row.started_at,
            finished_at=row.finished_at,
            log_tail=row.log_tail,
        )
