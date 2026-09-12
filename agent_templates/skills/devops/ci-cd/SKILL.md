---
name: ci-cd
description: Use when adding to or modifying CI/CD pipeline configuration, including test/lint/build stages and deployment steps.
---

## What I do
I maintain CI/CD pipeline configuration so lint, test, and build stages run reliably and quickly on every change, and deployments only proceed from a green pipeline.

## How to apply
- Add a new pipeline stage when a task introduces a new test suite, linter, or build artifact — don't let new checks stay unenforced.
- Keep stages ordered fast-to-slow (lint/type-check before unit tests before integration/e2e) so failures surface early.
- Cache dependencies (package managers, Docker layers) to keep pipeline runtime reasonable.
- Fail the pipeline loudly on any lint, test, or build error — never suppress or skip a failing check to get green.
- Keep secrets used in CI sourced from Infisical/CI secret store, never inlined in pipeline YAML.
- Gate deployment steps on all prior stages passing, and make rollback straightforward if a deploy step fails.
- Keep pipeline definitions under version control alongside the code they test, and update them in the same change that needs them.
