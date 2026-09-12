from __future__ import annotations

from collections.abc import Sequence

from domain.entities import AgentRole
from domain.ports import AgentRoleRepository


def seed_catalog(role_repo: AgentRoleRepository, roles: Sequence[AgentRole]) -> int:
    """Upsert the predefined role catalog. Returns the number of roles written."""
    count = 0
    for role in roles:
        role_repo.upsert(role)
        count += 1
    return count
