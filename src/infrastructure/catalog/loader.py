from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from domain.entities import AgentRole, Skill
from domain.value_objects import AgentMode


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise ValueError("expected YAML frontmatter starting with '---'")
    _, header, body = text.split("---", 2)
    meta = yaml.safe_load(header) or {}
    return meta, body.strip() + "\n"


def load_skill(path: Path) -> Skill:
    meta, body = _split_frontmatter(path.read_text())
    return Skill(
        slug=meta["name"],
        name=meta["name"].replace("-", " ").title(),
        description=meta["description"],
        content_md=body,
    )


def load_role(path: Path, skills_root: Path) -> AgentRole:
    meta, body = _split_frontmatter(path.read_text())
    category = _ROLE_TO_SKILL_CATEGORY.get(meta["slug"], "")
    skills: list[Skill] = []
    category_dir = skills_root / category
    if category_dir.is_dir():
        for skill_file in sorted(category_dir.glob("*/SKILL.md")):
            skills.append(load_skill(skill_file))
    return AgentRole(
        slug=meta["slug"],
        name=meta["name"],
        description=meta["description"],
        mode=AgentMode(meta["mode"]),
        guidelines_md=body,
        skills=tuple(skills),
    )


_ROLE_TO_SKILL_CATEGORY = {
    "project-manager": "pm",
    "scrum-master": "scrum",
    "backend-dev": "backend",
    "frontend-dev": "frontend",
    "qa": "qa",
    "devops": "devops",
}


def load_catalog(templates_root: Path) -> list[AgentRole]:
    """Parse agent_templates/roles/*.md (+ their matching skills/<category>/) into AgentRole entities."""
    roles_dir = templates_root / "roles"
    skills_root = templates_root / "skills"
    return [load_role(p, skills_root) for p in sorted(roles_dir.glob("*.md"))]
