---
name: pytest-django
description: Use when writing or running backend tests for a Django project with pytest and pytest-django, including fixtures, the test database, and factories.
---

## What I do
I write backend tests using `pytest` and `pytest-django`: database-backed tests via fixtures, request/response testing via the Django test client, and isolated, fast test runs.

## How to apply
- Use the `db` (or `django_db` marker) fixture only on tests that actually need database access; keep pure-logic tests DB-free for speed.
- Build test data with factories (e.g. `factory_boy`) or minimal fixtures rather than large hardcoded JSON blobs.
- Use `pytest.mark.parametrize` for testing multiple input variations instead of copy-pasted near-identical test functions.
- Use Django's `client`/`APIClient` fixture for endpoint tests, asserting both status code and response body shape.
- Isolate external calls (Kafka producers, third-party APIs) with mocks/fakes so tests don't depend on live infrastructure.
- Run the suite with `pytest -x` locally before reporting a task as done; investigate any flaky test rather than re-running until green.
- Keep fixtures scoped as narrowly as possible (`function` over `module`/`session`) unless shared setup is genuinely expensive and safe to reuse.
