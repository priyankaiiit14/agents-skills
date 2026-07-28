---
name: simplify
description: Review recently changed code for unnecessary complexity, duplication, or abstraction. Fix what you find.
user-invocable: true
---

Get changed files from `git diff main...HEAD --name-only`. Read each changed file. Look for:

- **Duplication** — same logic in multiple places that can be merged
- **Premature abstraction** — interfaces, helpers, or wrappers that serve only one caller
- **Dead code** — unused variables, imports, branches, or flags
- **Overengineering** — config/feature-flag/fallback patterns for scenarios that don't exist yet
- **Verbose control flow** — nested conditions that can flatten, early returns that remove else branches

Fix the issues directly. Don't refactor beyond what the changed code touches. Don't add comments explaining the simplification.
