---
name: django-rest
description: REST API conventions for Django projects — apply when the project's backend is Django, covering Django REST Framework serializers, viewsets, routing, and permissions. Not applicable if the project uses a different backend stack.
---

## What I do
I build REST endpoints using Django REST Framework: serializers for validation and representation, viewsets or generic views for behavior, routers for URL wiring, and permission/authentication classes for access control.

## How to apply
- Use `ModelSerializer` for straightforward CRUD; drop to plain `Serializer` when the payload doesn't map 1:1 to a model.
- Prefer `ViewSet`/`ModelViewSet` with a `DefaultRouter` over hand-wired function views for standard CRUD resources.
- Set explicit `permission_classes` on every view — never rely on framework defaults for anything touching user data.
- Validate in the serializer (`validate_<field>`, `validate()`), not in the view.
- Use `select_related`/`prefetch_related` in the queryset to avoid N+1 queries triggered by nested serializers.
- Version or namespace URLs deliberately; don't let endpoints leak internal model field names verbatim without review.
- Return DRF's standard error shape (`{"detail": ...}` or field-keyed errors) so frontend error handling stays consistent.
