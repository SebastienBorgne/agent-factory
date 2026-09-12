---
name: infisical-secrets
description: Use when wiring secrets or credentials into any service, ensuring nothing is hardcoded and everything is sourced from Infisical.
---

## What I do
I wire secrets into services exclusively through Infisical, so no credential, API key, or token is ever committed to the repository or hardcoded in code or config.

## How to apply
- Never commit a `.env` file with real values; keep `.env` in `.gitignore` and commit only a `.env.example` with placeholder keys.
- Authenticate non-interactive contexts (CI, containers) to Infisical using `INFISICAL_TOKEN` or a configured machine identity — never a personal login.
- Reference secrets in config using the project's `{env:VAR}` convention so the actual value is resolved from Infisical at runtime, not stored in the file.
- Scope secrets to the correct Infisical environment (dev/staging/prod) and never reuse a production secret value in a local `.env`.
- When a task needs a new secret, add the `{env:VAR}` reference and state in the task's notes what needs to be created in Infisical — don't invent a placeholder and leave it live.
- Rotate and revoke via Infisical directly; never patch a leaked secret by editing it in application code.
