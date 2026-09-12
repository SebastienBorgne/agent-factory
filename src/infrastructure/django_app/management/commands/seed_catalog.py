from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from application.use_cases.seed_catalog import seed_catalog
from infrastructure.catalog.loader import load_catalog
from infrastructure.django_app.repositories import DjangoAgentRoleRepository


class Command(BaseCommand):
    help = "Load agent_templates/ (roles + skills) into the database."

    def handle(self, *args, **options):
        templates_root = Path(settings.AGENT_TEMPLATES_ROOT)
        roles = load_catalog(templates_root)
        count = seed_catalog(DjangoAgentRoleRepository(), roles)
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} agent roles from {templates_root}"))
