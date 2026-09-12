from datetime import UTC, datetime

from django.test import SimpleTestCase

from application.tests.fakes import (
    FakeAgentRoleRepository,
    FakeEventPublisher,
    FakeProjectRepository,
    FakeRunLogRepository,
    FakeScaffoldWriter,
    FakeTeamRepository,
)
from application.use_cases.build_team import build_team
from application.use_cases.generate_project import generate_project
from application.use_cases.handle_run_result import handle_run_result
from application.use_cases.start_run import start_run
from domain.entities import AgentRole, Project
from domain.exceptions import EmptyTeamError, ProjectAlreadyExistsError, UnknownRoleError
from domain.value_objects import AgentMode, RunStatus


def _role(slug="backend-dev", name="Backend Developer") -> AgentRole:
    return AgentRole(
        slug=slug,
        name=name,
        description="does backend things",
        mode=AgentMode.SUBAGENT,
        guidelines_md="be a good backend dev",
    )


class BuildTeamTests(SimpleTestCase):
    def test_creates_project_and_team(self):
        role_repo = FakeAgentRoleRepository([_role()])
        project_repo = FakeProjectRepository()
        team_repo = FakeTeamRepository()

        project = build_team(
            project_repo,
            team_repo,
            role_repo,
            slug="acme",
            name="Acme",
            brief="build a thing",
            output_root="/tmp/generated_teams",
            member_role_slugs=["backend-dev"],
        )

        self.assertEqual(project.output_path, "/tmp/generated_teams/acme")
        self.assertEqual(team_repo.get_for_project("acme").member_role_slugs, ("backend-dev",))

    def test_rejects_empty_team(self):
        with self.assertRaises(EmptyTeamError):
            build_team(
                FakeProjectRepository(),
                FakeTeamRepository(),
                FakeAgentRoleRepository(),
                slug="acme",
                name="Acme",
                brief="x",
                output_root="/tmp",
                member_role_slugs=[],
            )

    def test_rejects_unknown_role(self):
        with self.assertRaises(UnknownRoleError):
            build_team(
                FakeProjectRepository(),
                FakeTeamRepository(),
                FakeAgentRoleRepository([_role()]),
                slug="acme",
                name="Acme",
                brief="x",
                output_root="/tmp",
                member_role_slugs=["nonexistent"],
            )

    def test_rejects_duplicate_slug(self):
        project_repo = FakeProjectRepository()
        role_repo = FakeAgentRoleRepository([_role()])
        team_repo = FakeTeamRepository()
        build_team(
            project_repo,
            team_repo,
            role_repo,
            slug="acme",
            name="Acme",
            brief="x",
            output_root="/tmp",
            member_role_slugs=["backend-dev"],
        )
        with self.assertRaises(ProjectAlreadyExistsError):
            build_team(
                project_repo,
                team_repo,
                role_repo,
                slug="acme",
                name="Acme 2",
                brief="y",
                output_root="/tmp",
                member_role_slugs=["backend-dev"],
            )


class GenerateProjectTests(SimpleTestCase):
    def test_writes_scaffold_for_the_teams_roles(self):
        role_repo = FakeAgentRoleRepository([_role()])
        project_repo = FakeProjectRepository()
        team_repo = FakeTeamRepository()
        build_team(
            project_repo,
            team_repo,
            role_repo,
            slug="acme",
            name="Acme",
            brief="x",
            output_root="/tmp",
            member_role_slugs=["backend-dev"],
        )
        writer = FakeScaffoldWriter()

        generate_project(project_repo, team_repo, role_repo, writer, project_slug="acme")

        self.assertEqual(len(writer.calls), 1)
        project, _team, roles = writer.calls[0]
        self.assertEqual(project.slug, "acme")
        self.assertEqual([r.slug for r in roles], ["backend-dev"])


class StartRunTests(SimpleTestCase):
    def test_publishes_and_records_requested_run(self):
        project_repo = FakeProjectRepository()
        project_repo.save(
            Project(
                slug="acme",
                name="Acme",
                brief="x",
                output_path="/tmp/acme",
                created_at=datetime.now(UTC),
            )
        )
        publisher = FakeEventPublisher()
        run_log_repo = FakeRunLogRepository()

        run_log = start_run(project_repo, publisher, run_log_repo, project_slug="acme")

        self.assertEqual(publisher.published, ["acme"])
        self.assertEqual(run_log.status, RunStatus.REQUESTED)
        self.assertEqual(run_log_repo.saved, [run_log])


class HandleRunResultTests(SimpleTestCase):
    def test_saves_result_run_log(self):
        run_log_repo = FakeRunLogRepository()

        run_log = handle_run_result(
            run_log_repo, project_slug="acme", status=RunStatus.SUCCEEDED, log_tail="done"
        )

        self.assertEqual(run_log.status, RunStatus.SUCCEEDED)
        self.assertEqual(run_log_repo.saved, [run_log])
