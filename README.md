# Personal Skills

Reusable agent skills for Codex, Claude Code, and other local coding agents.

## Skills

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

### Option 1 — npx (recommended)

Requires [Node.js](https://nodejs.org) 18+. Installs skills via the `skills` CLI into your project's `.claude/skills/` directory.

**Install all skills:**

```bash
npx skills@latest add priyankaiiit14/agents-skills
```

**Install specific skills only:**

```bash
npx skills@latest add priyankaiiit14/agents-skills --skills jira-helper,triage,tdd
```

### Option 2 — Python script

No dependencies beyond Python 3.8+. Pulls the skills directly from GitHub.

**Install all skills:**

```bash
python3 scripts/skills.py add
```

**Install specific skills:**

```bash
python3 scripts/skills.py add --skills jira-helper,triage,tdd
```

**Install into a specific project directory:**

```bash
python3 scripts/skills.py add --target /path/to/my-project
```

**Pull from a specific branch:**

```bash
python3 scripts/skills.py add --branch main
```

### Option 3 — Shell script (local only)

If you have cloned this repo, copy all skills into a project's `.claude/skills/`:

```bash
# into a specific project
./scripts/install-local.sh /path/to/project

# into the current directory
./scripts/install-local.sh
```

## Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/
    references/
    scripts/
    assets/
```

Each skill keeps `SKILL.md` concise. Large or conditional detail goes in `references/`, executable helpers in `scripts/`, and reusable templates or binaries in `assets/`.

## Adding A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Add YAML frontmatter with `name` and `description`.
3. Keep operational instructions in `SKILL.md`.
4. Put large or conditional detail in `references/`.
5. Add the skill path to `.claude-plugin/plugin.json`.
6. Add the skill to the table in this README.
