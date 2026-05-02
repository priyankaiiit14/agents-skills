# Personal Skills

Reusable agent skills for Codex, Claude Code, and other local coding agents.

## Skills

| Skill | Purpose |
| --- | --- |
| `jira-helper` | Create, draft, query, and summarize Jira Cloud tickets from conversations, notes, or files. |

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

Each skill should keep `SKILL.md` concise and move detailed docs into `references/`, executable helpers into `scripts/`, and reusable templates or binaries into `assets/`.

## Local Install

Install the skills into a local `.claude/skills` directory:

```bash
./scripts/install-local.sh /path/to/project
```

Install into the current directory:

```bash
./scripts/install-local.sh
```

## Adding A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Add YAML frontmatter with `name` and `description`.
3. Keep operational instructions in `SKILL.md`.
4. Put large or conditional detail in `references/`.
5. Add or update `agents/agent.yaml` when the skill needs UI metadata.
6. Add the skill to the table in this README.
