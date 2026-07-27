---
name: init
description: Initialize a CLAUDE.md for the current project by reading its structure, stack, and conventions.
user-invocable: true
---

If CLAUDE.md already exists, stop and say so.

Otherwise:
1. Read: `README.md`, `pyproject.toml`/`package.json`/`Cargo.toml`, key config files, directory structure (top 2 levels)
2. Identify: language/stack, how to run/test/build, any non-obvious conventions

Write `CLAUDE.md` with only:
- **What this is** — one sentence
- **Key commands** — run, test, build (exact commands only)
- **Conventions** — only things Claude wouldn't infer from the code (unusual patterns, constraints, project-specific rules)

Hard limits: under 60 lines, no generic advice ("write clean code"), no section that restates what the stack already implies.
