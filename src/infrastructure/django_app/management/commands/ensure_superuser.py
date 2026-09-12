from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create the Django admin superuser from APP_RUN__SUPERUSER__* config "
        "(see config/env.py), if one doesn't already exist. Safe to run on "
        "every container start."
    )

    def handle(self, *args, **options):
        superuser = settings.APP_SETTINGS.superuser
        if not superuser.password:
            self.stdout.write(
                self.style.WARNING("APP_RUN__SUPERUSER__PASSWORD is not set -- skipping superuser creation.")
            )
            return

        User = get_user_model()
        if User.objects.filter(username=superuser.username).exists():
            self.stdout.write(f"Superuser {superuser.username!r} already exists -- skipping.")
            return

        User.objects.create_superuser(
            username=superuser.username, email=superuser.email, password=superuser.password
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser {superuser.username!r}."))
