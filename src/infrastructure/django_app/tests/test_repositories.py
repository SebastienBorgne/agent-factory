from datetime import UTC, datetime

from django.test import TestCase

from domain.entities import AgentRole, Project, RunLog, Skill, Team
from domain.exceptions import UnknownProjectError, UnknownRoleError
from domain.value_objects import AgentMode, RunStatus
from infrastructure.django_app.repositories import (
    DjangoAgentRoleRepository,
    DjangoProjectRepository,
    DjangoRunLogRepository,
    DjangoTeamRepository,
)


class DjangoAgentRoleRepositoryTests(TestCase):
    def test_upsert_then_get_round_trips_with_skills(self):
        repo = DjangoAgentRoleRepository()
        role = AgentRole(
            slug="backend-dev",
            name="Backend Developer",
            description="implements the backend",
            mode=AgentMode.SUBAGENT,
            guidelines_md="do backend things",
            skills=(Skill(slug="django-rest", name="Django Rest", description="d", content_md="c"),),
        )
        repo.upsert(role)

        fetched = repo.get("backend-dev")
        self.assertEqual(fetched.name, "Backend Developer")
        self.assertEqual(fetched.mode, AgentMode.SUBAGENT)
        self.assertEqual([s.slug for s in fetched.skills], ["django-rest"])

    def test_upsert_replaces_skills_on_second_call(self):
        repo = DjangoAgentRoleRepository()
        base = {
            "slug": "qa",
            "name": "QA",
            "description": "d",
            "mode": AgentMode.SUBAGENT,
            "guidelines_md": "g",
        }
        repo.upsert(AgentRole(**base, skills=(Skill("a", "A", "d", "c"),)))
        repo.upsert(AgentRole(**base, skills=(Skill("b", "B", "d", "c"),)))

        self.assertEqual([s.slug for s in repo.get("qa").skills], ["b"])

    def test_get_unknown_role_raises(self):
        with self.assertRaises(UnknownRoleError):
            DjangoAgentRoleRepository().get("nope")


class DjangoProjectRepositoryTests(TestCase):
    def test_save_then_get(self):
        repo = DjangoProjectRepository()
        repo.save(
            Project(
                slug="acme",
                name="Acme",
                brief="b",
                output_path="/tmp/acme",
                created_at=datetime.now(UTC),
            )
        )
        fetched = repo.get("acme")
        self.assertEqual(fetched.name, "Acme")
        self.assertTrue(repo.exists("acme"))
        self.assertFalse(repo.exists("nope"))

    def test_get_unknown_project_raises(self):
        with self.assertRaises(UnknownProjectError):
            DjangoProjectRepository().get("nope")


class DjangoTeamRepositoryTests(TestCase):
    def test_save_then_get_for_project(self):
        DjangoAgentRoleRepository().upsert(
            AgentRole(slug="qa", name="QA", description="d", mode=AgentMode.SUBAGENT, guidelines_md="g")
        )
        DjangoProjectRepository().save(
            Project(
                slug="acme",
                name="Acme",
                brief="b",
                output_path="/tmp/acme",
                created_at=datetime.now(UTC),
            )
        )
        team_repo = DjangoTeamRepository()
        team_repo.save(Team(project_slug="acme", member_role_slugs=("qa",)))

        self.assertEqual(team_repo.get_for_project("acme").member_role_slugs, ("qa",))


class DjangoRunLogRepositoryTests(TestCase):
    def test_latest_for_project_returns_most_recent(self):
        DjangoProjectRepository().save(
            Project(
                slug="acme",
                name="Acme",
                brief="b",
                output_path="/tmp/acme",
                created_at=datetime.now(UTC),
            )
        )
        repo = DjangoRunLogRepository()
        repo.save(RunLog(project_slug="acme", status=RunStatus.REQUESTED))
        repo.save(RunLog(project_slug="acme", status=RunStatus.SUCCEEDED))

        self.assertEqual(repo.latest_for_project("acme").status, RunStatus.SUCCEEDED)

    def test_latest_for_project_returns_none_when_no_runs(self):
        self.assertIsNone(DjangoRunLogRepository().latest_for_project("nope"))
