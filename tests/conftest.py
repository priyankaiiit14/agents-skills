"""Shared helpers for the skill test suite.

A "skill" is a `SKILL.md` folder under `src/agent_skills_bundle/skills/`. These
helpers load and parse those folders so both the static gate (Layer A) and the
behavioral evals (Layer B) work from the same view of the bundle.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "src" / "agent_skills_bundle" / "skills"

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
    """Every skill folder name, sorted. Mirrors cli.available_skills()."""
    return sorted(
        d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


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
    skill_dir = SKILLS_DIR / name
    fm_text, body = split_frontmatter((skill_dir / "SKILL.md").read_text())
    frontmatter = yaml.safe_load(fm_text)
    return frontmatter, body, skill_dir
