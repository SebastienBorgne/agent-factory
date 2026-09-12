---
name: sprint-planning
description: Use when organizing a set of tasks in tracking.json into a sprint-sized, sequenced plan of work.
---

## What I do
I organize backlog tasks into a sprint-sized plan: right-sized tasks, correctly sequenced by dependency, with a clear owner role for each.

## How to apply
- Split any task that can't realistically be finished in one focused agent pass into smaller tasks with their own acceptance criteria.
- Set `dependencies` on each task explicitly so downstream work never gets delegated before its prerequisites are `done`.
- Assign each task's `assigned_to` to the role best suited to it (`backend-dev`, `frontend-dev`, `qa`, `devops`) based on the work described, not availability.
- Balance the sprint so no single role is overloaded with sequential dependent tasks while others sit idle.
- Write acceptance criteria into each task description up front — don't leave "done" undefined.
- Leave a small buffer for review/rework tasks (QA findings) rather than planning every task as flowing straight to done.
