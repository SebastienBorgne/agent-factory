# Agent Factory

[![CI](https://github.com/SebastienBorgne/agent-factory/actions/workflows/ci.yml/badge.svg)](https://github.com/SebastienBorgne/agent-factory/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

**Pick an AI agent team, describe a project, and get back a real, runnable
[OpenCode](https://opencode.ai) project — not a template, a working team.**

Agent Factory is a Django web app for assembling agentic software teams.
Pick from a catalog of predefined roles — Project Manager, Scrum Master,
Backend Dev, Frontend Dev, QA, DevOps — each with its own pre-written
guidelines and skills, describe what you want built, and generate a
self-contained project folder with real `.opencode/agents/` +
`.opencode/skills/`, an optional [Infisical](https://infisical.com) stack
for secrets, and a `tracking.json` task board the Project Manager agent
keeps current across runs.

Agent-factory itself is Django + PostgreSQL + Kafka — that stack has nothing
to do with what the *generated* agents build. `backend-dev`/`frontend-dev`
pick (or follow) whatever stack a given project's brief calls for, and
agents use whatever model(s) the `opencode` CLI is itself configured with;
agent-factory doesn't force a provider.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Run it](#run-it)
- [Develop without Docker](#develop-without-docker)
- [Linting](#linting)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)

## Features

- **A real agent catalog, not a prompt template** — 6 predefined roles with
  hand-written system prompts and 15 skills, seeded from plain markdown in
  `agent_templates/` into the database.
- **Generates a project OpenCode can actually run** — `opencode.json`,
  `.opencode/agents/*.md`, `.opencode/skills/*/SKILL.md`, all wired so the
  Project Manager delegates to the rest of the team via OpenCode's native
  Task tool.
- **`tracking.json` as the single source of truth** — the Project Manager
  reads and rewrites it every run, so state survives across sessions.
- **Stack-agnostic by design** — the generated backend/frontend/devops
  agents follow whatever tech a project's brief specifies, or pick and
  record a sensible default; agent-factory's own Django/Postgres/Kafka stack
  is not imposed on generated projects.
- **Hexagonal architecture** — the domain and use-case layers have zero
  Django/Kafka/OpenCode-CLI imports; every external system is an adapter
  behind a port.
- **Async orchestration** — starting a run publishes a Kafka event; a
  separate `worker` process picks it up and drives `opencode run`, so the
  web request never blocks on a long-running agent session.

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

```sh
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

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install --hook-type pre-commit --hook-type commit-msg   # one-time
python manage.py migrate      # falls back to sqlite when APP_RUN__DATABASE__HOST isn't set
python manage.py seed_catalog
python manage.py runserver
```

## Linting

`.pre-commit-config.yaml` runs [ruff](https://docs.astral.sh/ruff/) (lint +
format), basic file hygiene checks (trailing whitespace, valid YAML/JSON, no
merge-conflict markers, etc.), and [commitizen](https://commitizen-tools.github.io/commitizen/)
(enforces [Conventional Commits](https://www.conventionalcommits.org/) on
every commit message). Ruff's and commitizen's own config live in
`pyproject.toml`. Run the file-content hooks manually with:

```sh
pre-commit run --all-files
```

`pylint` (Django-aware, via `pylint-django`) and `mypy` (strict, scoped to
`domain/`+`application/` — see the note in `pyproject.toml`'s `[tool.mypy]`)
run in CI rather than pre-commit, since they're slower:

```sh
PYTHONPATH=src DJANGO_SETTINGS_MODULE=config.settings pylint src
mypy
```

## Tests

```sh
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

## Contributing

1. Fork and clone, then follow [Develop without Docker](#develop-without-docker)
   to get a working environment.
2. Make your change, with tests — `pytest` should stay green and
   `pre-commit run --all-files` clean.
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `refactor:`, ...) — enforced by the
   `commit-msg` hook once you've run `pre-commit install --hook-type commit-msg`.
   `cz commit` will walk you through it interactively if you'd rather not
   remember the format.
4. Open a PR — the [CI pipeline](#cicd) runs automatically.

## License

[MIT](LICENSE) © Sebastien Borgne
