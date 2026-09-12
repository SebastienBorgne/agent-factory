import os
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from config.env import load_settings, read_dotenv


class ReadDotenvTests(SimpleTestCase):
    def test_parses_key_value_pairs_and_skips_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(
                "# a comment\n"
                "\n"
                "APP_RUN__DJANGO_SETTINGS__SECRET_KEY=abc123\n"
                'APP_RUN__DJANGO_SETTINGS__ALLOWED_HOSTS="example.com,other.com"\n'
            )
            values = read_dotenv(path)

        self.assertEqual(values["APP_RUN__DJANGO_SETTINGS__SECRET_KEY"], "abc123")
        self.assertEqual(values["APP_RUN__DJANGO_SETTINGS__ALLOWED_HOSTS"], "example.com,other.com")

    def test_missing_file_returns_empty_dict(self):
        self.assertEqual(read_dotenv(Path("/nonexistent/.env")), {})


class LoadSettingsTests(SimpleTestCase):
    def setUp(self):
        # These tests assert on values read from an isolated temp-dir .env.
        # Process env always wins over the .env file (by design — see
        # config/env.py), so if this test process itself is running with
        # real APP_RUN__* vars already exported (e.g. inside a container
        # started via docker-compose's `env_file: .env`), those would
        # otherwise shadow the temp file and break isolation here.
        patcher = mock.patch.dict(
            os.environ,
            {k: v for k, v in os.environ.items() if not k.startswith("APP_RUN__")},
            clear=True,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _write_env(self, tmp: str, content: str) -> Path:
        base_dir = Path(tmp)
        (base_dir / ".env").write_text(content)
        return base_dir

    def test_reads_typed_nested_settings_from_dotenv(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = self._write_env(
                tmp,
                "APP_RUN__DJANGO_SETTINGS__SECRET_KEY=s3cr3t\n"
                "APP_RUN__DJANGO_SETTINGS__DEBUG=false\n"
                "APP_RUN__DJANGO_SETTINGS__ALLOWED_HOSTS=a.com, b.com\n"
                "APP_RUN__DJANGO_SETTINGS__PORT=9000\n"
                "APP_RUN__DATABASE__HOST=db\n"
                "APP_RUN__DATABASE__PORT=5433\n"
                "APP_RUN__KAFKA__BOOTSTRAP_SERVERS=kafka:29092\n"
                "APP_RUN__SUPERUSER__USERNAME=root\n"
                "APP_RUN__SUPERUSER__PASSWORD=hunter2\n",
            )
            settings = load_settings(base_dir)

        self.assertEqual(settings.django.secret_key, "s3cr3t")
        self.assertFalse(settings.django.debug)
        self.assertEqual(settings.django.allowed_hosts, ["a.com", "b.com"])
        self.assertEqual(settings.django.port, 9000)
        self.assertEqual(settings.database.host, "db")
        self.assertEqual(settings.database.port, 5433)
        self.assertEqual(settings.kafka.bootstrap_servers, "kafka:29092")
        self.assertEqual(settings.superuser.username, "root")
        self.assertEqual(settings.superuser.password, "hunter2")

    def test_missing_dotenv_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = load_settings(Path(tmp))

        self.assertEqual(settings.django.port, 8000)
        self.assertEqual(settings.database.host, "")  # -> sqlite fallback in settings.py
        self.assertEqual(settings.superuser.password, "")  # -> ensure_superuser skips

    def test_blank_value_in_dotenv_falls_back_to_default_not_empty_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = self._write_env(tmp, "APP_RUN__PATHS__GENERATED_TEAMS_ROOT=\n")
            settings = load_settings(base_dir)

        self.assertEqual(settings.paths.generated_teams_root, str(base_dir / "generated_teams"))

    def test_process_environment_overrides_dotenv_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = self._write_env(tmp, "APP_RUN__DJANGO_SETTINGS__PORT=8000\n")
            with mock.patch.dict(os.environ, {"APP_RUN__DJANGO_SETTINGS__PORT": "9999"}):
                settings = load_settings(base_dir)

        self.assertEqual(settings.django.port, 9999)
