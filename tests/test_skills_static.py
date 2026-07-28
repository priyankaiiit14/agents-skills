"""Layer A — deterministic static gate for every bundled skill.

These checks are fast, free, and non-flaky, so they run on every PR and block
merge. They prove each skill is *well-formed* (valid frontmatter, sound internal
references, in sync with the README and lockfile) — not that it *works*; that is
Layer B (tests/test_evals.py).
"""

from __future__ import annotations

import json
import re

import pytest

from conftest import (
    ALLOWED_FRONTMATTER_KEYS,
    BOOLEAN_FRONTMATTER_KEYS,
    REPO_ROOT,
    RESOURCE_EXTS,
    load_skill,
    skill_dir,
    skill_names,
)

SKILLS = skill_names()

# Backtick-quoted subpath references like `references/jira.md` or
# `scripts/hitl-loop.template.sh` — the progressive-disclosure files a skill
# points its agent at. Requires a "/" so we don't match prose or bare filenames.
RESOURCE_REF = re.compile(r"`([\w./-]+/[\w./-]+\.(?:%s))`" % "|".join(e[1:] for e in RESOURCE_EXTS))


def test_at_least_one_skill():
    assert SKILLS, "no skills found under src/agent_skills_bundle/skills/"


@pytest.mark.parametrize("name", SKILLS)
def test_skill_md_exists(name):
    assert (skill_dir(name) / "SKILL.md").is_file()


@pytest.mark.parametrize("name", SKILLS)
def test_frontmatter_is_valid(name):
    frontmatter, body, _ = load_skill(name)

    assert isinstance(frontmatter, dict), "frontmatter must parse to a mapping"

    unknown = set(frontmatter) - ALLOWED_FRONTMATTER_KEYS
    assert not unknown, f"unknown frontmatter key(s): {sorted(unknown)}"

    assert isinstance(frontmatter.get("name"), str) and frontmatter["name"].strip(), "name missing"
    leaf = name.split("/")[-1]
    assert frontmatter["name"] == leaf, f"name '{frontmatter['name']}' != folder '{leaf}'"

    desc = frontmatter.get("description")
    assert isinstance(desc, str) and desc.strip(), "description missing/empty"
    assert len(desc) <= 1024, f"description too long ({len(desc)} chars, max 1024)"

    for key in BOOLEAN_FRONTMATTER_KEYS & set(frontmatter):
        assert isinstance(frontmatter[key], bool), f"'{key}' must be a boolean"

    assert body.strip(), "SKILL.md body (after frontmatter) is empty"


@pytest.mark.parametrize("name", SKILLS)
def test_resource_references_resolve(name):
    """Bundled resources a SKILL.md points at must exist.

    A reference counts as a *bundled* resource only when its first path segment
    is a real subdirectory of the skill (e.g. `references/`, `scripts/`). That
    excludes paths that live in the user's target project (`.claude/settings.json`,
    `docs/agents/domain.md`), which the skill legitimately references but doesn't ship.
    """
    _, body, skill_dir = load_skill(name)
    for ref in sorted(set(RESOURCE_REF.findall(body))):
        top = ref.split("/", 1)[0]
        if not (skill_dir / top).is_dir():
            continue
        assert (skill_dir / ref).exists(), f"referenced resource missing: {ref}"


def test_readme_lists_every_skill():
    readme = (REPO_ROOT / "README.md").read_text()
    # Check by leaf name so both shared and project skills match README entries.
    missing = [n for n in SKILLS if f"`{n.split('/')[-1]}`" not in readme]
    assert not missing, f"skills absent from README 'Available Skills' table: {missing}"


def test_lockfile_has_no_dangling_entries():
    """Provenance lockfile may cover a subset, but every locked skill must exist."""
    lock = json.loads((REPO_ROOT / "skills-lock.json").read_text())
    dangling = [n for n in lock.get("skills", {}) if n not in SKILLS]
    assert not dangling, f"skills-lock.json references removed skills: {dangling}"


def test_every_skill_has_an_eval_spec():
    """Every bundled skill must have a behavioral eval spec in tests/evals/specs/.

    Shared skills: specs/<skill>.yaml
    Project skills: specs/<project>/<skill>.yaml
    """
    specs_dir = REPO_ROOT / "tests" / "evals" / "specs"

    def spec_path(name: str):
        parts = name.split("/")
        if len(parts) == 1:
            return specs_dir / f"{name}.yaml"
        _, proj, skill = parts
        return specs_dir / proj / f"{skill}.yaml"

    missing = [n for n in SKILLS if not spec_path(n).is_file()]
    assert not missing, (
        f"skills missing a behavioral eval spec in tests/evals/specs/: {missing}\n"
        "Shared skills: add tests/evals/specs/<skill>.yaml\n"
        "Project skills: add tests/evals/specs/<project>/<skill>.yaml\n"
        "See tests/evals/README.md."
    )
