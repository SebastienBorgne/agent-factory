---
name: status-reporting
description: Use when summarizing project progress from tracking.json for the user, including overall status and any blockers.
---

## What I do
I summarize project state from `tracking.json` into a clear status report: what's done, what's in progress, what's blocked, and the overall project status.

## How to apply
- Compute overall `status` (`planning`, `in_progress`, `blocked`, `done`) from actual task states, not from memory of what was planned.
- Call out every `blocked` task explicitly with its reason, pulled from that task's `notes`.
- Summarize by role or by feature area rather than dumping the raw task list unfiltered.
- Highlight tasks stuck in `review` that need a decision, not just tasks still `in_progress`.
- Keep the report factual and terse — state what happened, not what should have happened.
- Always reflect the timestamp of the most recent `tracking.json` update so the report's freshness is clear.
