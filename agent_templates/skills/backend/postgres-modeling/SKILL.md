---
name: postgres-modeling
description: Schema-design conventions for Django models backed by PostgreSQL — apply when the project's data layer is Django + PostgreSQL, covering indexing, constraints, and migrations. Not applicable to other database or ORM choices.
---

## What I do
I design Django models that map to sound PostgreSQL schemas: correct field types, indexes for the queries that will actually run, database-level constraints, and safe, reversible migrations.

## How to apply
- Add `db_index=True` or a `Meta.indexes` entry for any field used in frequent filters, ordering, or joins.
- Use `UniqueConstraint`/`CheckConstraint` at the database level for invariants, not just serializer validation.
- Prefer `ForeignKey(..., on_delete=...)` chosen deliberately (`PROTECT`, `CASCADE`, `SET_NULL`) rather than defaulting to `CASCADE` everywhere.
- Use `JSONField` sparingly — only for genuinely unstructured data, not to avoid modeling a relation.
- Write migrations that are reversible and, for large tables, split schema changes from data backfills to avoid long locks.
- Use `Meta.ordering` and `select_related`/`prefetch_related` together to keep default querysets both correct and efficient.
- Run `makemigrations` review-by-eye before committing — check for accidental field drops or type changes on existing columns.
