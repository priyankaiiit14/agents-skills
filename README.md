# skills-hub

Packaged agent skills for Claude Code and Codex. Skills are `SKILL.md` folders — a cross-agent standard, so the same skill works in both tools unmodified. `install` copies them into the directories each agent auto-discovers (`.claude/skills/` and `.codex/skills/`), and every tool picks them up automatically.

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

Two ways to install — identical result. Pick whichever fits your team.

**uv (recommended — no Python required)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # once, if you don't have uv
uvx skills-hub install review tdd                  # named skills
uvx skills-hub install --all                       # everything
uvx skills-hub==0.2.0 install review               # pin a version
```

**bash (local clone — no tooling required)**

```bash
git clone https://github.com/priyankaiiit14/agents-skills.git
cd agents-skills
./scripts/install-local.sh /path/to/project        # omit the path to use the current dir
```

Both accept the `--target` and `--scope` flags described next.

## Targets and scopes

`--target` chooses the agent(s); `--scope` chooses project vs machine-wide. Skills are copied to the matching directory, which each agent auto-discovers at startup:

| | `--target claude` | `--target codex` |
| --- | --- | --- |
| `--scope project` (default) | `<project>/.claude/skills/` | `<project>/.codex/skills/` |
| `--scope global` | `~/.claude/skills/` | `~/.codex/skills/` |

Defaults are `--target both --scope project`. Use **project** scope to commit skills to a repo so teammates get them on `git pull`; use **global** scope to make them available in every project on your machine.

```bash
uvx skills-hub install review                    # both agents, project (default)
uvx skills-hub install review --target codex     # Codex only
uvx skills-hub install --all --scope global      # every skill, machine-wide
```

A lockfile records what's installed and the target/scope used — `skills-lock.json` (project) or `~/.skills-hub/skills-lock.json` (global).

## Commands

| Command | What it does |
| --- | --- |
| `skills-hub list` | List every skill in the installed version, with descriptions |
| `skills-hub install <names…>` | Install named skills (`--all` for everything) |
| `skills-hub update` | Re-install tracked skills at the current version |
| `skills-hub status` | Show which skills are installed vs available, and their versions |
| `skills-hub create <name>` | Scaffold a new skill folder (run from a repo clone) |

`install`, `update`, and `status` accept `--target` and `--scope`; `update` reuses the target/scope saved in the lockfile. Run any command with `--help` for details.

## Publishing to PyPI

### One-time setup

Done once, before the first release. Publishing uses PyPI [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — no API tokens are stored anywhere.

1. Create a [PyPI account](https://pypi.org/account/register/).
2. Confirm the project name `skills-hub` is free on PyPI (rename it in `pyproject.toml` if taken).
3. On PyPI, add a **Trusted Publisher** (Account settings → Publishing) with:
   - Repository: `priyankaiiit14/agents-skills`
   - Workflow: `publish.yml`
   - Environment: `pypi`
4. In the GitHub repo, create an environment named `pypi` (Settings → Environments).

### Cutting a release

Merges to `main` do **not** auto-publish. A maintainer cuts a release by bumping the version and pushing a tag:

1. Bump `version` in `pyproject.toml` and `src/skills_hub/__init__.py` (keep them in sync).
2. Commit and push to `main`.
3. Push a matching tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The GitHub Action (`.github/workflows/publish.yml`) verifies the tag matches the package version, builds the package, and publishes it to PyPI. Teams then pin with `uvx skills-hub==0.2.0 install` or run `uvx skills-hub update` to pick up the new version.

## Contributing a skill

You do **not** need to clone the repo to *use* skills. Clone only to *add* or *edit* one. All skills live in `src/skills_hub/skills/` — that's the single source of truth, and both agents' copies are generated from it.

```bash
git clone git@github.com:priyankaiiit14/agents-skills.git
cd agents-skills
```

### Add a new skill

```bash
git checkout -b skills/my-skill-name
uvx skills-hub create my-skill-name   # scaffolds src/skills_hub/skills/my-skill-name/SKILL.md
# edit SKILL.md, then:
git add src/skills_hub/skills/my-skill-name
git commit -m "add my-skill-name skill"
# open a PR to main
```

`create` writes the folder with the required frontmatter already filled in. Then add the skill to the table at the top of this README.

### Update an existing skill

```bash
git checkout -b skills/my-skill-name        # or fix/my-skill-name for a bug fix
# edit src/skills_hub/skills/my-skill-name/SKILL.md (or its references/, scripts/, assets/)
git add src/skills_hub/skills/my-skill-name
git commit -m "update my-skill-name: <what changed>"
# open a PR to main
```

The change ships to users in the next release (see [How releases work](#how-releases-work)). Users pull it with `uvx skills-hub update`.

### Branch naming

| Branch | Purpose |
| --- | --- |
| `main` | Always stable. Protected — PRs required. |
| `skills/<name>` | New skill or feature change to an existing one |
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

Every `SKILL.md` needs YAML frontmatter — `name` and `description` are required (the description is what shows in `skills-hub list` and what each agent uses to decide when to trigger the skill):

```yaml
---
name: my-skill-name
description: One-line description of what this skill does and when to invoke it.
---
```
