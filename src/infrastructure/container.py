"""Composition root: builds concrete adapters for the domain ports. Plain
constructor wiring on purpose — no DI framework. Callers (Django views, the
worker entrypoint, management commands) import factory functions from here
rather than constructing adapters themselves, so there is exactly one place
that knows which concrete class implements which port."""

from __future__ import annotations

from infrastructure.django_app.repositories import (
    DjangoAgentRoleRepository,
    DjangoProjectRepository,
    DjangoRunLogRepository,
    DjangoTeamRepository,
)
from infrastructure.opencode_cli.scaffold_writer import FilesystemScaffoldWriter


def agent_role_repo() -> DjangoAgentRoleRepository:
    return DjangoAgentRoleRepository()


def project_repo() -> DjangoProjectRepository:
    return DjangoProjectRepository()


def team_repo() -> DjangoTeamRepository:
    return DjangoTeamRepository()


def run_log_repo() -> DjangoRunLogRepository:
    return DjangoRunLogRepository()


def scaffold_writer() -> FilesystemScaffoldWriter:
    return FilesystemScaffoldWriter()


def event_publisher():
    from infrastructure.kafka.producer import KafkaEventPublisher

    return KafkaEventPublisher()
