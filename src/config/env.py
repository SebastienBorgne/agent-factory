"""Typed application configuration, read from a `.env` file (KEY=VALUE dict)
merged with the process environment (process env wins, so a docker-compose
`environment:` override still takes priority over `.env`).

Naming convention: every key is namespaced `APP_RUN__<SECTION>__<FIELD>`,
double-underscore-delimited, e.g. `APP_RUN__DJANGO_SETTINGS__PORT=9000`
becomes `Settings.django.port`. This is the single source of truth for all
of agent-factory's own runtime configuration — `config/settings.py` derives
every Django setting from `load_settings()` rather than reading `os.environ`
directly, and `docker-compose.yml` reads the same `.env` file for its own
`${APP_RUN__...}` interpolation (e.g. the exposed port, the Postgres image's
credentials), so there is exactly one place these values are set.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_PREFIX = "APP_RUN__"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def read_dotenv(path: Path) -> dict[str, str]:
    """Minimal `.env` parser: `KEY=VALUE` per line, `#` comments and blank
    lines skipped, optional surrounding quotes stripped. No interpolation,
    no multi-line values — deliberately simple, this only needs to read what
    our own `.env.example` produces."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class _EnvReader:
    """Looks up `APP_RUN__...` keys: process env first, then the parsed
    `.env` file, then a caller-supplied default."""

    def __init__(self, dotenv_values: dict[str, str]):
        self._dotenv_values = dotenv_values

    def get(self, key: str, default: str = "") -> str:
        """An empty value counts as "not set" (falls through to default) —
        this lets `.env.example` document a key with a blank value (e.g. to
        opt out of superuser creation, or fall back to a computed default)
        without that blank overriding the default."""
        full_key = _PREFIX + key
        env_value = os.environ.get(full_key, "")
        if env_value:
            return env_value
        return self._dotenv_values.get(full_key, "") or default

    def get_bool(self, key: str, default: bool) -> bool:
        return self.get(key, "1" if default else "0").strip().lower() in _TRUE_VALUES

    def get_int(self, key: str, default: int) -> int:
        return int(self.get(key, str(default)))

    def get_list(self, key: str, default: str = "") -> list[str]:
        raw = self.get(key, default)
        return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class DjangoSettings:
    secret_key: str
    debug: bool
    allowed_hosts: list[str]
    port: int


@dataclass(frozen=True)
class DatabaseSettings:
    host: str  # empty means "no Postgres configured" -> settings.py falls back to sqlite
    port: int
    name: str
    user: str
    password: str


@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str


@dataclass(frozen=True)
class SuperuserSettings:
    username: str
    email: str
    password: str  # empty means "don't create one" -> ensure_superuser skips


@dataclass(frozen=True)
class PathSettings:
    generated_teams_root: str


@dataclass(frozen=True)
class Settings:
    django: DjangoSettings
    database: DatabaseSettings
    kafka: KafkaSettings
    superuser: SuperuserSettings
    paths: PathSettings


def load_settings(base_dir: Path | None = None) -> Settings:
    base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
    reader = _EnvReader(read_dotenv(base_dir / ".env"))

    return Settings(
        django=DjangoSettings(
            secret_key=reader.get("DJANGO_SETTINGS__SECRET_KEY", "dev-insecure-secret-key-change-me"),
            debug=reader.get_bool("DJANGO_SETTINGS__DEBUG", True),
            allowed_hosts=reader.get_list("DJANGO_SETTINGS__ALLOWED_HOSTS", "*"),
            port=reader.get_int("DJANGO_SETTINGS__PORT", 8000),
        ),
        database=DatabaseSettings(
            host=reader.get("DATABASE__HOST", ""),
            port=reader.get_int("DATABASE__PORT", 5432),
            name=reader.get("DATABASE__NAME", "agent_factory"),
            user=reader.get("DATABASE__USER", "agent_factory"),
            password=reader.get("DATABASE__PASSWORD", "agent_factory"),
        ),
        kafka=KafkaSettings(
            bootstrap_servers=reader.get("KAFKA__BOOTSTRAP_SERVERS", "kafka:9092"),
        ),
        superuser=SuperuserSettings(
            username=reader.get("SUPERUSER__USERNAME", "admin"),
            email=reader.get("SUPERUSER__EMAIL", "admin@example.com"),
            password=reader.get("SUPERUSER__PASSWORD", ""),
        ),
        paths=PathSettings(
            generated_teams_root=reader.get("PATHS__GENERATED_TEAMS_ROOT", str(base_dir / "generated_teams")),
        ),
    )
