from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from config.env import DjangoSettings, KafkaSettings, PathSettings, Settings, SuperuserSettings


def _settings_with_superuser(username="admin", email="admin@example.com", password="hunter2") -> Settings:
    return Settings(
        django=DjangoSettings(secret_key="x", debug=True, allowed_hosts=["*"], port=8000),
        database=None,  # not read by this command
        kafka=KafkaSettings(bootstrap_servers="kafka:9092"),
        superuser=SuperuserSettings(username=username, email=email, password=password),
        paths=PathSettings(generated_teams_root="/tmp"),
    )


class EnsureSuperuserCommandTests(TestCase):
    def test_creates_superuser_when_password_set(self):
        with override_settings(APP_SETTINGS=_settings_with_superuser()):
            call_command("ensure_superuser", stdout=StringIO())

        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("hunter2"))

    def test_skips_when_password_blank(self):
        with override_settings(APP_SETTINGS=_settings_with_superuser(password="")):
            call_command("ensure_superuser", stdout=StringIO())

        self.assertFalse(get_user_model().objects.filter(username="admin").exists())

    def test_skips_when_user_already_exists(self):
        get_user_model().objects.create_user(username="admin", password="original")

        with override_settings(APP_SETTINGS=_settings_with_superuser(password="hunter2")):
            call_command("ensure_superuser", stdout=StringIO())

        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.check_password("original"))
        self.assertFalse(user.is_superuser)
