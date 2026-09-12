---
name: task-breakdown
description: Use when turning a project brief or epic into concrete, independently assignable tasks in tracking.json.
---

## What I do
I turn a project brief or epic into a set of concrete tasks in `tracking.json`, each small enough to assign to one subagent role with clear acceptance criteria.

## How to apply
- Extract every distinct piece of required functionality from the brief as its own task rather than one monolithic task.
- Write each task with a title, a description containing explicit acceptance criteria, and the correct `assigned_to` role slug.
- Identify and record `dependencies` between tasks (e.g. a frontend task depending on a backend endpoint task) before delegating.
- Size tasks so one subagent can complete one in a single focused pass — split anything larger.
- Avoid overlapping scope between two tasks; if two tasks would touch the same files/behavior, merge or clearly separate their boundaries.
- Leave ambiguous or underspecified requirements as a `scrum-master` task to clarify rather than guessing and assigning straight to an implementer.
