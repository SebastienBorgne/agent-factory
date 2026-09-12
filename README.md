# Agent Factory

Pick a team of pre-configured AI agents (Project Manager, Scrum Master,
Backend Dev, Frontend Dev, QA, DevOps), describe a project, and generate a
self-contained [OpenCode](https://opencode.ai) project folder: real
`.opencode/agents/` + `.opencode/skills/`, an optional Infisical stack for
secrets, and a `tracking.json` task board the Project Manager agent keeps
current across runs. Agents use whatever model(s) the `opencode` CLI is
itself configured with — agent-factory doesn't force a provider.

Agent-factory itself is Django + PostgreSQL + Kafka. That stack has nothing
to do with what the *generated* agents build — `backend-dev`/`frontend-dev`
pick (or follow) whatever stack a given project's brief calls for.

## Architecture

Hexagonal/DDD, under `src/`:

- `domain/` — entities, value objects, and ports (ABCs). Zero framework
  imports.
- `application/use_cases/` — orchestrates ports to fulfil one use case each
  (build a team, generate a project, start a run, record a run's result).
- `infrastructure/` — adapters implementing the ports: `django_app` (ORM +
  repositories), `web` (views/templates, htmx), `opencode_cli` (scaffold
  writer + `opencode run` subprocess runner), `kafka` (producer/consumer).
  `container.py` is the composition root — the one place that wires concrete
  adapters to ports.

`agent_templates/` holds the source-of-truth markdown for the 6 predefined
roles and their skills; `seed_catalog` loads it into the database.

## Configuration

All of agent-factory's own runtime config is typed and lives in one place:
`src/config/env.py`. Every key is namespaced `APP_RUN__<SECTION>__<FIELD>`
(double-underscore-delimited, e.g. `APP_RUN__DJANGO_SETTINGS__PORT=9000`),
read from `.env` (a plain `KEY=VALUE` dict — see `read_dotenv`) merged with
the process environment, which always wins. `config/settings.py` builds
every Django setting from `load_settings()` — nothing reads `os.environ`
directly outside that one module. `docker-compose.yml` interpolates the
*same* `.env` keys for the containers around Django (e.g. the exposed port,
Postgres's own credentials), so there is exactly one source of truth. See
`.env.example` for the full list of keys.

## Run it

```
cp .env.example .env      # edit APP_RUN__SUPERUSER__PASSWORD etc. as you like
docker compose up -d --build
```

An `init` container runs once on startup — migrations, `seed_catalog`, and
`ensure_superuser` (creates the admin user from `APP_RUN__SUPERUSER__*` in
`.env`, skipped if `APP_RUN__SUPERUSER__PASSWORD` is left blank) — and `web`
/`worker` wait for it to finish before starting.

Open http://localhost:8000 (or whatever `APP_RUN__DJANGO_SETTINGS__PORT` is
set to), pick a team, describe your project, and hit "Generate team". The
output lands in `generated_teams/<slug>/` — open its own `README.md` for how
to run it. `/admin/` logs in with the `APP_RUN__SUPERUSER__*` credentials
from `.env`.

Hitting "Start run" on a project's dashboard publishes a Kafka event that the
`worker` service picks up and turns into `opencode run --agent
project-manager ...` inside that project's folder — requires the `opencode`
CLI to be installed wherever `worker` runs.

## Develop without Docker

`.env` is shared with docker-compose, so if it exists with
`APP_RUN__DATABASE__HOST=db` (the default in `.env.example`), plain
`manage.py` on the host can't resolve `db` — that hostname only exists on
the compose network. Either don't create `.env` at all for host-only work
(falls back to sqlite automatically), or blank out `APP_RUN__DATABASE__HOST`
in your copy.

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install            # one-time: runs the hooks below on every commit
python manage.py migrate      # falls back to sqlite when APP_RUN__DATABASE__HOST isn't set
python manage.py seed_catalog
python manage.py runserver
```

## Linting

`.pre-commit-config.yaml` runs [ruff](https://docs.astral.sh/ruff/) (lint +
format) and basic file hygiene checks (trailing whitespace, valid
YAML/JSON, no merge-conflict markers, etc.) via `pre-commit`. Ruff's own
config lives in `pyproject.toml`. Run it manually with:

```
pre-commit run --all-files
```

## Tests

```
python manage.py test                            # host, sqlite (no .env, or blank DATABASE__HOST)
docker compose exec web python manage.py test     # against the real stack, whenever .env is docker-configured
```

Covers the typed config loader (including precedence between `.env` and the
process environment), the catalog loader against the real
`agent_templates/`, the scaffold writer (generates into a temp dir and
asserts file contents/schema), `ensure_superuser`, the Django repositories,
and the builder → generate → dashboard web flow. `pytest` also works
directly (see `[tool.pytest.ini_options]` in `pyproject.toml`) and is what
CI uses.

## CI/CD

`.github/workflows/ci.yml` runs on every push to `main` and every PR:

| Job | What |
|---|---|
| `ruff` | `ruff check` + `ruff format --check` |
| `pylint` | `pylint src` (Django-aware via `pylint-django`) |
| `mypy` | strict, scoped to `domain/`+`application/` — see the note in `pyproject.toml`'s `[tool.mypy]` for why `infrastructure/` is excluded |
| `test` | `pytest`, sqlite, no external services needed |
| `gitleaks` | secret scanning |
| `trivy-fs` | dependency + misconfig scan of the repo (Dockerfile, compose files) |
| `docker-build-scan` | builds the image, then Trivy-scans it for OS/package CVEs |
| `ci` | fans in all of the above — the one required status check to branch-protect on |

`docker-build-scan` only runs once every other job is green, so a broken
lint/test doesn't waste minutes building and scanning an image. Both Trivy
jobs use `ignore-unfixed: true` (only fail on CVEs that actually have a
patch available) and upload SARIF to the repo's Security tab. Everything
here runs the same tools you can run locally (`pre-commit run --all-files`,
`pytest`, `mypy`, `pylint src`) — CI should never surprise you.
