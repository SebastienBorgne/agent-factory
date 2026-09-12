---
name: test-strategy
description: Use when deciding what to test and at what level for a task — unit, integration, or end-to-end — before writing any test code.
---

## What I do
I decide the right mix of unit, integration, and end-to-end tests for a given task based on its acceptance criteria and risk, so coverage is deliberate rather than accidental.

## How to apply
- Map each acceptance criterion in the task to at least one test before writing implementation-level tests.
- Favor unit tests for pure logic, integration tests for component/API boundaries, and end-to-end tests sparingly for critical user flows only.
- Prioritize tests around failure modes most likely to break in production: bad input, empty/None states, permission boundaries, concurrent writes.
- Avoid duplicating the same assertion at multiple test levels — push logic checks down to unit tests, keep integration/e2e focused on wiring.
- Flag acceptance criteria that are untestable as written back to whoever authored the task rather than guessing at intent.
- Keep tests deterministic — no reliance on real time, network, or ordering unless explicitly under test.
- Record which acceptance criteria are covered (and which are deliberately out of scope) in the task's notes.
