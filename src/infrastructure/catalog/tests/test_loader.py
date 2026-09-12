from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from domain.value_objects import AgentMode
from infrastructure.catalog.loader import load_catalog

EXPECTED_ROLE_SLUGS = {
    "project-manager",
    "scrum-master",
    "backend-dev",
    "frontend-dev",
    "qa",
    "devops",
}


class LoadCatalogTests(SimpleTestCase):
    def setUp(self):
        self.roles = load_catalog(Path(settings.AGENT_TEMPLATES_ROOT))

    def test_loads_all_six_roles(self):
        self.assertEqual({r.slug for r in self.roles}, EXPECTED_ROLE_SLUGS)

    def test_project_manager_is_primary_and_others_are_subagents(self):
        by_slug = {r.slug: r for r in self.roles}
        self.assertEqual(by_slug["project-manager"].mode, AgentMode.PRIMARY)
        for slug in EXPECTED_ROLE_SLUGS - {"project-manager"}:
            self.assertEqual(by_slug[slug].mode, AgentMode.SUBAGENT, slug)

    def test_every_role_has_description_and_guidelines(self):
        for role in self.roles:
            self.assertTrue(role.description.strip())
            self.assertTrue(role.guidelines_md.strip())

    def test_roles_load_their_matching_skills(self):
        by_slug = {r.slug: r for r in self.roles}
        self.assertGreaterEqual(len(by_slug["backend-dev"].skills), 3)
        self.assertGreaterEqual(len(by_slug["frontend-dev"].skills), 3)
        skill_slugs = {s.slug for s in by_slug["backend-dev"].skills}
        self.assertIn("django-rest", skill_slugs)

    def test_skill_slug_matches_directory_name(self):
        for role in self.roles:
            for skill in role.skills:
                self.assertTrue(skill.slug)
                self.assertTrue(skill.description.strip())
                self.assertTrue(skill.content_md.strip())
