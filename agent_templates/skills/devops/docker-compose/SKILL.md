---
name: docker-compose
description: Use when defining or modifying docker-compose services for this project's actual stack (backend, database, message broker, frontend, cache, etc.), including dependencies and health checks.
---

## What I do
I define and maintain `docker-compose` services so the project's stack — whatever it actually is — starts reliably in the right order with correct networking and volumes.

## How to apply
- Declare `depends_on` with `condition: service_healthy` for services that must wait on another (e.g. backend waiting on its database/broker), not just startup order.
- Add a real `healthcheck` for each service that a `depends_on` condition relies on.
- Use named volumes for any service with persistent data (databases, message brokers) so `docker compose down` doesn't silently destroy state.
- Keep service configuration in environment variables (`environment`/`env_file`), sourced from Infisical-managed `.env` files that are never committed.
- Pin image versions/tags explicitly rather than floating on `latest`.
- Expose only the ports actually needed for local development; keep internal-only services on the compose network.
- Verify `docker compose up` brings up the full stack cleanly from a fresh state before marking a related task done.
