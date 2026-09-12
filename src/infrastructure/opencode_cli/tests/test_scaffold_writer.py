import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from django.test import SimpleTestCase

from domain.entities import AgentRole, Project, Skill, Team
from domain.value_objects import AgentMode
from infrastructure.opencode_cli.scaffold_writer import FilesystemScaffoldWriter


class FilesystemScaffoldWriterTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output_path = str(Path(self.tmp.name) / "acme")

        self.roles = [
            AgentRole(
                slug="project-manager",
                name="Project Manager",
                description="orchestrates",
                mode=AgentMode.PRIMARY,
                guidelines_md="Read tracking.json first.\n",
            ),
            AgentRole(
                slug="backend-dev",
                name="Backend Developer",
                description="implements the backend",
                mode=AgentMode.SUBAGENT,
                guidelines_md="Implement the backend.\n",
                skills=(
                    Skill(
                        slug="django-rest",
                        name="Django Rest",
                        description="apply when the project uses Django",
                        content_md="Use DRF serializers.\n",
                    ),
                ),
            ),
        ]
        self.project = Project(
            slug="acme",
            name="Acme",
            brief="Build a widget catalog",
            output_path=self.output_path,
            created_at=datetime.now(UTC),
        )
        self.team = Team(project_slug="acme", member_role_slugs=("project-manager", "backend-dev"))
        FilesystemScaffoldWriter().write(self.project, self.team, self.roles)
        self.root = Path(self.output_path)

    def test_top_level_files_exist(self):
        for name in (
            "opencode.json",
            "AGENTS.md",
            "tracking.json",
            "README.md",
            ".env.example",
            "docker-compose.yml",
        ):
            self.assertTrue((self.root / name).is_file(), name)

    def test_src_and_tests_dirs_created(self):
        self.assertTrue((self.root / "src").is_dir())
        self.assertTrue((self.root / "tests").is_dir())

    def test_tracking_json_matches_schema(self):
        data = json.loads((self.root / "tracking.json").read_text())
        self.assertEqual(data["project"], "acme")
        self.assertEqual(data["status"], "planning")
        self.assertEqual(data["team"], ["project-manager", "backend-dev"])
        self.assertEqual(data["tasks"], [])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_opencode_json_is_valid_and_has_no_forced_provider(self):
        data = json.loads((self.root / "opencode.json").read_text())
        self.assertEqual(data["default_agent"], "project-manager")
        self.assertNotIn("provider", data)

    def test_opencode_json_grants_all_permissions_for_unattended_runs(self):
        data = json.loads((self.root / "opencode.json").read_text())
        for key in ("read", "edit", "bash", "task", "external_directory"):
            self.assertEqual(data["permission"][key], "allow", key)

    def test_opencode_json_lets_project_manager_delegate_but_not_subagents(self):
        data = json.loads((self.root / "opencode.json").read_text())
        self.assertEqual(data["agent"]["project-manager"]["permission"]["task"], "allow")
        self.assertEqual(data["agent"]["backend-dev"]["permission"]["task"], "deny")

    def test_agent_files_written_with_correct_frontmatter(self):
        pm_file = (self.root / ".opencode" / "agents" / "project-manager.md").read_text()
        self.assertIn("mode: primary", pm_file)
        self.assertIn("Read tracking.json first.", pm_file)
        self.assertNotIn("model:", pm_file)  # no forced provider/model

        backend_file = (self.root / ".opencode" / "agents" / "backend-dev.md").read_text()
        self.assertIn("mode: subagent", backend_file)

    def test_skill_files_written_for_selected_roles_only(self):
        skill_file = self.root / ".opencode" / "skills" / "django-rest" / "SKILL.md"
        self.assertTrue(skill_file.is_file())
        content = skill_file.read_text()
        self.assertTrue(content.startswith("---\nname: django-rest\n"))

    def test_no_router_or_secret_push_scaffolding(self):
        self.assertFalse((self.root / "router").exists())
        self.assertFalse((self.root / "scripts").exists())
