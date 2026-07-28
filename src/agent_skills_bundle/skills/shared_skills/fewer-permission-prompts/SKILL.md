---
name: fewer-permission-prompts
description: Scan recent tool calls and add allow rules to .claude/settings.json to reduce repetitive permission prompts.
user-invocable: true
---

1. Read `.claude/settings.json` (project) and `~/.claude/settings.json` (global)
2. Check existing `permissions.allow` rules
3. Look at recent bash commands in this session that were prompted — identify patterns that are clearly safe (read-only, non-destructive)
4. Add allow rules for those patterns to `.claude/settings.json` (project-level by default, global only if the command is universal)

Rule format: `"Bash(command *)"` — use the minimal prefix that covers the pattern without being too broad.

Don't allow: `rm`, `git push`, `git reset`, anything that writes outside the project, or anything destructive.
Show the diff before writing. Ask which file (project vs global) if unclear.
