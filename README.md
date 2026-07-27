# skills-hub

Packaged agent skills for Claude Code, Codex, and VS Code. Skills are markdown files — install them into your project's `.claude/skills/` directory and every tool picks them up automatically.

## Available Skills

| Skill | Purpose |
| --- | --- |
| `caveman` | Ultra-compressed communication mode, cuts token usage ~75%. |
| `context-audit` | Audit your Claude Code setup for token waste and context bloat. |
| `diagnose` | Disciplined diagnosis loop for hard bugs and performance regressions. |
| `fewer-permission-prompts` | Add allow rules to reduce repetitive permission prompts. |
| `find-skills` | Discover and install agent skills for a given task. |
| `grill-me` | Interview-style stress-test of a plan or design. |
| `grill-with-docs` | Grilling session that challenges your plan against the domain model and updates docs inline. |
| `improve-codebase-architecture` | Find refactoring and architecture improvement opportunities. |
| `init` | Initialize a CLAUDE.md for the current project. |
| `jira-helper` | Create, draft, query, and summarize Jira Cloud tickets from conversations, notes, or files. |
| `pm` | Parallelized work breakdown, effort estimates, and team-ready task list. |
| `prompt-prep` | Prepare a compact, structured Agent task prompt from a small set of inputs. |
| `review` | Review a pull request or branch changes for bugs and improvements. |
| `security-review` | Security-focused review of changed code. Checks for OWASP top 10. |
| `setup-skills` | Scaffold per-repo config (issue tracker, triage labels, domain docs) for engineering skills. |
| `simplify` | Review changed code for unnecessary complexity and fix it. |
| `tdd` | Test-driven development with red-green-refactor loop. |
| `to-issues` | Break a plan or PRD into independently-grabbable issues on the issue tracker. |
| `to-prd` | Turn the current conversation context into a PRD on the issue tracker. |
| `triage` | Move issues through a triage state machine. |
| `write-a-skill` | Create new agent skills with proper structure. |
| `zoom-out` | Step back and assess the bigger picture of a codebase or problem. |

## Install

Skills land in `.claude/skills/` in the current directory. Commit them — teammates who clone the project get the skills without needing any tooling installed.

### Option 1 — uv (recommended, no Python required)

Install `uv` once if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install skills:

```bash
uvx skills-hub install review tdd       # specific skills
uvx skills-hub install --all            # everything
uvx skills-hub==0.2.0 install review   # pin to a version
```

### Option 2 — bash (no tooling required, local clone only)

Clone the repo once, then copy skills into any project:

```bash
git clone https://github.com/priyankaiiit14/agents-skills.git
cd agents-skills

./scripts/install-local.sh /path/to/my-project   # into a specific project
./scripts/install-local.sh                        # into the current directory
```

### See what's available

```bash
uvx skills-hub list
```

### Update installed skills

After a new release, re-run with the new version to update:

```bash
uvx skills-hub update
```

### Check installed vs available

```bash
uvx skills-hub status
```

## How releases work

Merges to `main` do not auto-publish. A maintainer cuts a release by bumping the version and pushing a tag:

1. Bump `version` in `pyproject.toml` and `src/skills_hub/__init__.py`
2. Commit and push to `main`
3. Push a tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The GitHub Action builds the package and publishes it to PyPI automatically. Teams can then `uvx skills-hub==0.2.0 install` or use `uvx skills-hub update` to pick up the new version.

## Contributing a skill

You do not need to clone the repo to use skills. Clone only if you are adding or editing one.

```bash
git clone git@github.com:priyankaiiit14/agents-skills.git
cd agents-skills
git checkout -b skills/my-skill-name
uvx skills-hub create my-skill-name   # scaffolds src/skills_hub/skills/my-skill-name/SKILL.md
# edit the file, then:
git add src/skills_hub/skills/my-skill-name
git commit -m "add my-skill-name skill"
# open a PR to main
```

### Branch naming

| Branch | Purpose |
| --- | --- |
| `main` | Always stable. Protected — PRs required. |
| `skills/<name>` | New or updated skill |
| `fix/<name>` | Bug fix to an existing skill |
| `release/v<x.y.z>` | Version bump PR before tagging |

### Skill layout

```text
src/skills_hub/skills/
  <skill-name>/
    SKILL.md          ← required; keep concise
    references/       ← large or conditional reference material
    scripts/          ← executable helpers
    assets/           ← templates, binaries, examples
```

Add YAML frontmatter to `SKILL.md`:

```yaml
---
name: my-skill-name
description: One-line description shown in `skills-hub list`.
---
```

Add the skill to the table in this README and open a PR. A reviewer approves; the next release picks it up.
