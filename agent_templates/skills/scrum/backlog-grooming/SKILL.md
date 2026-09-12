---
name: backlog-grooming
description: Use when reviewing existing tasks in tracking.json to keep descriptions, dependencies, and statuses accurate as scope evolves.
---

## What I do
I keep the task backlog in `tracking.json` accurate over time: descriptions match current scope, dependencies reflect reality, and stale or duplicate tasks get cleaned up.

## How to apply
- Re-read task descriptions against the current state of the code/brief and correct any that no longer match reality.
- Merge or close duplicate tasks rather than letting two tasks track the same work.
- Flag any task stuck in the same status for an unusually long time as stale, with a note on why, back to the project-manager.
- Verify `dependencies` still point to tasks that exist and actually block the work — remove stale dependency links.
- Break down any task that has grown beyond its original scope into smaller, current tasks.
- Never delete a task's history silently — record scope changes in `notes` so the audit trail stays intact.
