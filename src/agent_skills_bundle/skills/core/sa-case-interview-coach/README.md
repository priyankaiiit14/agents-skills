# SA Case Interview Coach — install guide

`SKILL.md` uses the open, cross-agent skill format, so the same file works
in Claude and Codex CLI unmodified. Only the folder it goes in differs.

## Claude Code / Claude apps

Personal (all your projects):
```
mkdir -p ~/.claude/skills/sa-case-interview-coach
cp SKILL.md ~/.claude/skills/sa-case-interview-coach/
```

Project-only (checked into a repo, shared with teammates):
```
mkdir -p .claude/skills/sa-case-interview-coach
cp SKILL.md .claude/skills/sa-case-interview-coach/
```

Restart the session (or start a new one) and it will be picked up
automatically when your request matches the description — e.g. "mock
interview me for a Solutions Architect case study."

## Codex CLI

Personal:
```
mkdir -p ~/.codex/skills/sa-case-interview-coach
cp SKILL.md ~/.codex/skills/sa-case-interview-coach/
```

Project-only (checked into a repo):
```
mkdir -p .agents/skills/sa-case-interview-coach
cp SKILL.md .agents/skills/sa-case-interview-coach/
```

Codex scans skill directories on startup; restart the session if it doesn't
show up right away. Codex also supports an optional, Codex-only
`openai.yaml` sidecar file for UI hints — not needed here, since this skill
is plain conversation/coaching with no scripts or MCP dependencies.

## Using it

Just talk to the assistant naturally, e.g.:

- "Roleplay the interviewer — client scenario is global data ingestion,
  I want to spike on Data Engineering."
- "Here's how I talked through my last mock interview, give me feedback."
- "Give me a discovery-question checklist for a data warehousing spike."

The skill will pick Roleplay / Coach / Prep mode based on what you ask for.
