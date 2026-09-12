import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from domain.entities import AgentRole
from domain.value_objects import AgentMode
from infrastructure.django_app.repositories import DjangoAgentRoleRepository


class BuilderAndDashboardFlowTests(TestCase):
    def setUp(self):
        DjangoAgentRoleRepository().upsert(
            AgentRole(
                slug="backend-dev",
                name="Backend Developer",
                description="implements the backend",
                mode=AgentMode.SUBAGENT,
                guidelines_md="do backend things",
            )
        )
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_builder_page_lists_roles(self):
        response = self.client.get(reverse("builder"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Developer")

    def test_generate_creates_project_and_redirects_to_dashboard(self):
        with override_settings(GENERATED_TEAMS_ROOT=self.tmp.name):
            response = self.client.post(
                reverse("builder"),
                {
                    "project_name": "Acme Widgets",
                    "brief": "Build a widget catalog",
                    "roles": ["backend-dev"],
                },
            )
        self.assertRedirects(response, reverse("dashboard", kwargs={"slug": "acme-widgets"}))

    def test_dashboard_renders_generated_tracking_json(self):
        with override_settings(GENERATED_TEAMS_ROOT=self.tmp.name):
            self.client.post(
                reverse("builder"),
                {
                    "project_name": "Acme Widgets",
                    "brief": "Build a widget catalog",
                    "roles": ["backend-dev"],
                },
            )
            response = self.client.get(reverse("dashboard", kwargs={"slug": "acme-widgets"}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "planning")

    def test_generate_rejects_empty_team(self):
        with override_settings(GENERATED_TEAMS_ROOT=self.tmp.name):
            response = self.client.post(
                reverse("builder"), {"project_name": "Acme", "brief": "x", "roles": []}
            )
        self.assertEqual(response.status_code, 200)  # re-renders form with errors
        self.assertContains(response, "This field is required")
