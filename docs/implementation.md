# Implementation guide

For contributors and anyone who wants to understand how the repo is structured internally.

## Repo layout

```
agents-skills/
├── src/agent_skills_bundle/
│   ├── __init__.py          ← version string (single source of truth)
│   ├── cli.py               ← all CLI logic (~300 lines, no external deps)
│   └── skills/              ← bundled skill folders
│       ├── review/
│       │   └── SKILL.md
│       └── ...
├── scripts/skills.py        ← standalone installer (no pip needed, fetches from GitHub zip)
├── pyproject.toml           ← package metadata and build config
└── .github/workflows/
    └── publish.yml          ← CD: auto-publishes to PyPI on merge to main
```

## What a skill is

A skill is a folder containing at minimum a `SKILL.md` with YAML frontmatter:

```yaml
---
name: review
description: Review a pull request or branch changes for bugs and improvements.
---

# Instructions for the agent...
```

Claude Code and Codex scan `.claude/skills/` and `.codex/skills/` at startup. They use the `description` field to decide when to auto-invoke a skill, and the body as instructions when they do. The folder format is agent-agnostic — the same folder works in both tools unmodified.

## How the CLI works

`cli.py` implements five subcommands:

**`install`** — copies skill folders from `src/agent_skills_bundle/skills/` into the target project's `.claude/skills/` and/or `.codex/skills/`. Uses `shutil.copytree`. Writes a `skills-lock.json` recording the SHA-256 hash and package version for each installed skill.

**`update`** — reads the lockfile to find previously installed skills, then re-copies each one at the current package version.

**`status`** — diffs the lockfile against the bundled skills to show what is installed, what version it was installed from, and what is newly available.

**`list`** — reads the `description` frontmatter from each bundled `SKILL.md` and prints a table.

**`create`** — scaffolds a new `SKILL.md` folder for contributors (run from the repo root).

The CLI entry point is registered in `pyproject.toml`:

```toml
[project.scripts]
agent-skills-bundle = "agent_skills_bundle.cli:main"
```

When pip installs the package it writes a thin wrapper script to the system `bin/` that calls `main()`. That is how `agent-skills-bundle list` works from any terminal.

### How the CLI finds bundled skills

```python
BUNDLED = Path(__file__).parent / "skills"
```

`__file__` resolves to wherever pip installed the package (inside a virtualenv, a `uvx` temp env, or the system site-packages). The `skills/` subfolder is always right next to `cli.py`, so this works regardless of install location.

## Package build

- **Build backend**: `hatchling`, configured in `pyproject.toml`.
- **`uv build`** produces a wheel (`dist/agent_skills_bundle-<ver>-py3-none-any.whl`) and a source tarball.
- **Wheel contents**: `[tool.hatch.build.targets.wheel]` tells hatchling to include `src/agent_skills_bundle/` — which includes all `skills/` subfolders and their `SKILL.md` files. The skills ship inside the wheel.

## CD pipeline

`publish.yml` triggers on every push to `main`. Logic:

1. Fetch `https://pypi.org/pypi/agent-skills-bundle/<version>/json`.
2. HTTP 200 → version already published → skip (handles docs-only merges without bumping version).
3. HTTP 404 → new version → `uv build` → publish via OIDC.

**OIDC (Trusted Publishing)**: no API token is stored. PyPI trusts a specific GitHub Actions workflow in a specific repo. The workflow requests a short-lived token from GitHub's OIDC provider and presents it to PyPI, which verifies it matches the registered publisher configuration.

**To trigger a release**: bump `version` in `pyproject.toml` and `src/agent_skills_bundle/__init__.py` (keep them in sync), then open a PR and merge to `main`.

## Two install paths for users

| | `uvx agent-skills-bundle install` | `python scripts/skills.py add` |
|---|---|---|
| Requires | `uv` | Nothing (stdlib only) |
| Source | PyPI | GitHub zip download |
| Versioning | lockfile + PyPI versions | latest `main` always |
| Use case | normal teams | no-tooling or air-gapped environments |

## End-to-end flow for `uvx agent-skills-bundle install review`

1. `uvx` downloads `agent-skills-bundle` from PyPI into a temporary virtualenv.
2. Runs `agent_skills_bundle.cli:main` with args `install review`.
3. `cli.py` resolves `BUNDLED = Path(__file__).parent / "skills"` — points inside the temp venv.
4. Copies `BUNDLED/review/` → `<cwd>/.claude/skills/review/` and `<cwd>/.codex/skills/review/`.
5. Writes `skills-lock.json` with the content hash and package version.
6. The temp venv is discarded — nothing persists except the copied skill folder and the lockfile.

## Local development

```bash
# Editable install — source changes take effect immediately
pip install -e .
agent-skills-bundle list

# Build and test the wheel (closest to what PyPI ships)
uv build
pip install dist/agent_skills_bundle-*.whl
agent-skills-bundle list

# Quick smoke-test without installing
uvx --from . agent-skills-bundle list
```
