# Evidence-based debrief rubric

Score only behavior supported by the transcript, code, results, or the candidate's concrete recollection. Use `Not observed` instead of assuming competence or failure.

## 1. Computational thinking

- **1 — Fragile:** Starts coding without defining the problem; transformations do not connect to stated requirements.
- **2 — Developing:** Finds a plausible path but leaves important grain, edge cases, or checks implicit.
- **3 — Strong:** Decomposes the problem, states assumptions, builds incrementally, and validates important boundaries.
- **4 — Exceptional:** Continuously links business rules to transformations, chooses discriminating tests, and adapts the design as evidence changes.

## 2. Code stewardship

- **1 — Fragile:** Cannot explain generated code or verify its result; uses obviously unsafe scale patterns.
- **2 — Developing:** Produces mostly plausible code but explanations or checks are incomplete.
- **3 — Strong:** Audits AI output, explains semantics and Spark execution, and demonstrates correctness with targeted checks.
- **4 — Exceptional:** Identifies subtle assumptions or inefficiencies, corrects them minimally, and explains tradeoffs clearly to both technical and customer audiences.

## 3. Resilience

- **1 — Fragile:** Guesses repeatedly, changes many things at once, or stalls without seeking evidence.
- **2 — Developing:** Recovers with substantial prompting but does not isolate the root cause cleanly.
- **3 — Strong:** States hypotheses, runs focused diagnostics, uses documentation or AI deliberately, and verifies the fix.
- **4 — Exceptional:** Turns ambiguity or failure into a clear learning loop, communicates uncertainty calmly, and preserves progress while adapting.

## Feedback format

For each criterion provide:

- score or `Not observed`;
- one or two pieces of direct evidence;
- the interviewer signal that evidence creates;
- one specific next drill.

End with the strongest signal, the highest-risk gap, and a focused practice plan containing no more than three drills. Avoid false precision such as an overall hiring probability.
