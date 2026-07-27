---
name: review
description: Review a pull request or the current branch changes for bugs, logic issues, and improvements.
user-invocable: true
---

Run `git diff main...HEAD` (or the provided PR diff). Then:

1. **Bugs** — logic errors, off-by-ones, unhandled edge cases, broken error paths
2. **Correctness** — does the code do what it claims? check naming vs behavior
3. **Simplicity** — unnecessary complexity, dead code, over-abstraction
4. **Risk** — anything that could break callers, change behavior silently, or cause data loss

Output: grouped findings by severity (blocking / suggestion). One line each. No praise, no summary fluff.

If given a PR number, use `gh pr diff <number>` to get the diff.
