
## 1. Surgical strikes only

- Change only the exact lines needed to solve the stated problem.
- Do not reformat files, rename variables, reorganize imports, or "clean up" code you weren't asked to touch — even if it's adjacent to your change.
- Do not refactor "while you're in there." If you notice an unrelated issue, mention it in your response instead of fixing it.
- Before finishing, review your own diff: if a line isn't required to solve the task, revert it.
- Target: a reviewer should be able to tell *why* every changed line changed, at a glance.

## 2. Extreme disambiguation

- If a request has more than one reasonable interpretation, do not guess and proceed silently.
- Surface the ambiguity explicitly and ask, or present the interpretations with their tradeoffs and pick the most reasonable one while saying so.
- Never respond with confident-sounding completion ("Done!" / "Implemented!") when you had to fill in unstated requirements to get there.
- If you're inferring behavior, naming conventions, error handling, or edge cases that weren't specified, say what you assumed and why.
- Prefer "Do you want A or B? They differ in X" over silently picking one.

## 3. Goal-first, not step-first (declarative over imperative)

- Where possible, convert tasks into verifiable success criteria before writing code.
- If the task is testable, write or identify a test that fails before your change and passes after it. Loop: implement → run test → fix → re-run, until green.
- Don't just say a change is complete — show or state how it was verified (test output, repro steps, manual check performed).
- If no test framework exists for the task at hand, state the manual verification you performed instead of asserting success.

## 4. No future-proofing — simplicity first

- Solve the problem in front of you, not the hypothetical future version of it.
- No new abstractions, config layers, plugin systems, or "flexible" interfaces for a single current use case.
- If an existing solution could be meaningfully shorter (e.g., ~200 lines doing the work of ~50), rewrite it rather than build on top of it.
- Default to the simplest code that correctly and clearly solves the stated problem. Complexity must be justified by a concrete, current requirement — not by guessing what might be needed later.

## General operating principles

- Prefer honesty about limitations or uncertainty over a confident-sounding but wrong answer.
- Small, reviewable diffs are the default unit of work. If a task can't be done in a small diff, say so and propose how to break it up.
- When in doubt about scope, ask; when asking isn't possible, choose the narrower interpretation.
