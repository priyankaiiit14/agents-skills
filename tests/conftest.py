"""Shared helpers for the skill test suite.

A "skill" is a `SKILL.md` folder under `src/agent_skills_bundle/skills/`.
Shared skills live under `shared_skills/`; project skills live under
`project_skills/<project>/<skill>/`. These helpers load and parse those folders
so both the static gate (Layer A) and the behavioral evals (Layer B) work from
the same view of the bundle.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "src" / "agent_skills_bundle" / "skills"
SHARED_DIR = SKILLS_DIR / "core"
PROJECTS_DIR = SKILLS_DIR / "domain"

# The only frontmatter keys any bundled skill uses today. New keys must be added
# here deliberately so a typo (e.g. `user-invocabl`) fails the gate instead of
# silently doing nothing.
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "user-invocable",
    "disable-model-invocation",
}
BOOLEAN_FRONTMATTER_KEYS = {"user-invocable", "disable-model-invocation"}

# Extensions a bundled resource reference (progressive disclosure) can point at.
RESOURCE_EXTS = (".md", ".sh", ".yml", ".yaml", ".py", ".txt", ".json")


def skill_names() -> list[str]:
    """All installable skill identifiers, sorted.

    Shared skills return their leaf name (e.g. "review").
    Project skills return their full key (e.g. "project_skills/search/query-review").
    Mirrors cli.available_skills().
    """
    shared = sorted(
        d.name for d in SHARED_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    ) if SHARED_DIR.exists() else []

    project = []
    if PROJECTS_DIR.exists():
        for proj in sorted(PROJECTS_DIR.iterdir()):
            if not proj.is_dir() or proj.name.startswith("."):
                continue
            for skill in sorted(proj.iterdir()):
                if skill.is_dir() and not skill.name.startswith("."):
                    project.append(f"project_skills/{proj.name}/{skill.name}")

    return shared + project


def skill_dir(name: str) -> Path:
    """Return the directory for a skill given its identifier."""
    if "/" in name:
        _, proj, skill = name.split("/")
        return PROJECTS_DIR / proj / skill
    return SHARED_DIR / name


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_yaml, body). Raises if no leading `---` block."""
    if not text.startswith("---"):
        raise ValueError("no frontmatter block (file does not start with '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter block is not closed with a second '---'")
    return parts[1], parts[2]


def load_skill(name: str) -> tuple[dict, str, Path]:
    """Return (frontmatter_dict, body, skill_dir) for one skill."""
    d = skill_dir(name)
    fm_text, body = split_frontmatter((d / "SKILL.md").read_text())
    frontmatter = yaml.safe_load(fm_text)
    return frontmatter, body, d
