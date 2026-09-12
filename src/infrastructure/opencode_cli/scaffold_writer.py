from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from domain.entities import AgentRole, Project, Team
from domain.exceptions import ScaffoldWriteError
from domain.ports import ScaffoldWriter

from . import templates


class FilesystemScaffoldWriter(ScaffoldWriter):
    def write(self, project: Project, team: Team, roles: Sequence[AgentRole]) -> None:
        root = Path(project.output_path)
        try:
            self._write(root, project, roles)
        except OSError as exc:
            raise ScaffoldWriteError(f"failed writing {root}: {exc}") from exc

    def _write(self, root: Path, project: Project, roles: Sequence[AgentRole]) -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "src" / ".gitkeep").touch()
        (root / "tests" / ".gitkeep").touch()

        (root / "opencode.json").write_text(templates.opencode_json(roles))
        (root / "AGENTS.md").write_text(templates.agents_md(project, roles))
        (root / "tracking.json").write_text(templates.tracking_json(project, roles))
        (root / "README.md").write_text(templates.readme_md(project))
        (root / ".env.example").write_text(templates.env_example())
        (root / "docker-compose.yml").write_text(templates.docker_compose_yml())

        self._write_agents(root, roles)
        self._write_skills(root, roles)

    def _write_agents(self, root: Path, roles: Sequence[AgentRole]) -> None:
        agents_dir = root / ".opencode" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        for role in roles:
            (agents_dir / f"{role.slug}.md").write_text(templates.agent_frontmatter_file(role))

    def _write_skills(self, root: Path, roles: Sequence[AgentRole]) -> None:
        skills_dir = root / ".opencode" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        for role in roles:
            for skill in role.skills:
                skill_dir = skills_dir / skill.slug
                skill_dir.mkdir(exist_ok=True)
                (skill_dir / "SKILL.md").write_text(
                    templates.skill_file(skill.slug, skill.description, skill.content_md)
                )
