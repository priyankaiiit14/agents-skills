# Genie Code prompt partner

Help the candidate visibly use Genie Code as an engineering partner while retaining ownership of requirements, code, execution, and validation.

This mode is for **Genie Code**, Databricks' coding assistant. It is different from configuring an AI/BI Genie Agent for business-user data questions. Clarify if the user's wording could mean the latter.

## What advanced usage looks like on two shared screens

1. On the scratchpad/Codex screen, the candidate states: “I’m converting the requirements into explicit context, constraints, and checks so I can audit the generated code.”
2. Draft a focused prompt using the SCOPE structure below. Do not invent missing business rules; either ask the interviewer or mark a narrow assumption.
3. On the Databricks screen, attach only relevant context with `@table`, `@cell`, or Add context. Verify that the intended resources are attached.
4. Paste the prompt and make the action boundary explicit: plan only, generate code, edit, or run. Default to **do not run yet** for a first implementation so the candidate can review it aloud.
5. Review the response for semantics, hidden assumptions, platform/API validity, distributed behavior, and falsifying checks.
6. Approve or run the smallest useful unit. Observe actual output.
7. Iterate with a short evidence-based follow-up in the same chat rather than rewriting the full prompt.

This sequence demonstrates prompt engineering through context management and verification, not decorative wording.

## The SCOPE prompt structure

Use only sections that materially constrain the result.

- **Situation:** customer outcome, data grain, and current notebook state.
- **Context:** attached tables/cells, known schema, business rules, and observed errors. Prefer direct `@` references over copying large content.
- **Objective:** the single next deliverable, such as a plan, one data-generation cell, one transformation, or one diagnosis.
- **Proof:** checks that could disprove correctness, including expected row counts, invariants, edge cases, or reconciliation.
- **Execution boundary:** whether Genie Code may only explain, may propose a diff, or may edit/run code; also specify language and important scale constraints.

Do not ask for hidden chain-of-thought. Ask for a concise plan, explicit assumptions, tradeoffs, and observable checks.

## Meta-prompt to use on the scratchpad/Codex screen

The candidate can paste this into Codex while the interviewer watches:

```text
Use $dbx-dsa-coding-interview-coach in Genie Code prompt-partner mode.

Interview task:
<paste the task>

Clarified requirements and assumptions:
- <business outcome>
- <row/event grain and keys>
- <volume, latency, and correctness constraints>
- <known edge cases>

Available Databricks context:
- <notebook language>
- <tables/cells I can reference with @>
- <current result or exact error, if any>

Time remaining: <minutes>

Return only:
1. one sentence I can say to explain my prompting strategy;
2. one paste-ready Genie Code prompt using SCOPE;
3. five checks I should perform before accepting or running the output;
4. at most two short follow-up prompts based on likely outcomes.

Do not solve the entire task invisibly, invent missing schema, or claim execution.
```

## Paste-ready initial Genie Code template

Replace brackets and remove irrelevant lines before pasting.

```text
# Situation
We need to [customer outcome]. One row/event represents [grain], keyed by [key].

# Context
Use [@table / @cell references].
Confirmed rules:
- [business rule]
- [edge case and required behavior]
Assumption: [only a narrow assumption already stated to the interviewer].

# Objective
[Produce a concise plan / generate one PySpark or SQL cell] that [single next outcome].

# Proof
Include checks for:
- [key invariant or reconciliation]
- [null/duplicate/boundary case]
- [expected schema, count, or known example]

# Execution boundary
- Use [PySpark / Databricks SQL] available in this notebook.
- Prefer Spark-native transformations; do not use pandas, collect large data to the driver, or add architecture not required here.
- Briefly state assumptions and likely shuffle or driver risks.
- Do not edit or run code yet. Return the proposed code and a concise explanation for my review.
- If a missing fact blocks correctness, ask at most three targeted questions; otherwise state the assumption and proceed.
```

## Specialized prompt: synthetic interview dataset

```text
Create one PySpark notebook cell that generates a reproducible synthetic dataset for [scenario].

Data contract:
- Grain: [one row per ...]
- Columns and types: [schema]
- Size: [small interview size], controlled by one row-count variable
- Seed: fixed and explicit
- Required edge cases: [duplicates/nulls/late records/skew/etc. with approximate rates or exact fixture rows]

Use Spark-native construction so the pattern can scale; do not build a large local Python list or use pandas. Keep a few deterministic rows if needed to guarantee critical edge cases. Do not write tables unless asked.

After the generation code, provide small validation expressions for schema, count, key expectations, and each required edge case. State any assumption. Do not run or edit the notebook yet.
```

## Specialized prompt: build one pipeline stage

```text
Using [@input cell/table] and the agreed rules below, implement only [stage and output].

Rules:
- [rule 1]
- [rule 2]

Acceptance checks:
- [invariant]
- [known input → expected output]

Use [PySpark/SQL]. Keep the transformation readable and minimal. Call out any shuffle, ordering, or driver-side behavior. Return code plus checks, but do not run or modify other cells.
```

## Evidence-based follow-up prompts

Use chat history and actual results instead of restating the task.

### Review before execution

```text
Audit your proposed code against the stated grain, edge cases, and acceptance checks. Return only: hidden assumptions, correctness risks, scale risks, and the minimal patch. Do not run code.
```

### Diagnose a failure

```text
The exact result/error is: [paste result]. Inspect [@cell] and [@relevant output]. State the leading hypothesis, one diagnostic that distinguishes it from the next hypothesis, and the expected observation. Do not rewrite the full pipeline yet.
```

### Explain distributed execution

```text
For [@cell], explain only the operations that affect distributed execution: actions, shuffle boundaries, join strategy, partition/skew risk, state, caching, or driver collection. Tie each risk to evidence I could inspect. Be concise.
```

### Apply a verified correction

```text
The diagnostic showed [evidence], confirming [root cause]. Propose the smallest correction to [@cell] and add one regression check for this case plus one normal case. Do not change unrelated code or run it yet.
```

### Prepare the customer explanation

```text
Using the solution in [@cells], give me a 30-second customer explanation in this order: goal, data flow, key choice, correctness check, and first scale risk. Do not describe every line.
```

## Five-point review before accepting output

1. **Requirement:** Does the code implement the agreed grain and business rule, not a plausible substitute?
2. **Data:** Are schema, null, duplicate, time, and ordering assumptions visible and correct?
3. **Runtime:** Are the APIs supported in the current environment, with no fabricated cells, tables, or results?
4. **Scale:** Are driver collection, shuffles, skew, joins, state, and unnecessary caching acceptable for the stated workload?
5. **Proof:** Do the checks exercise both a normal case and the highest-risk edge case?

## Prompting mistakes that weaken the interview signal

- Asking “build the whole pipeline” before clarifying grain and success criteria.
- Adding persona language, excessive Markdown, or generic “be an expert” instructions that do not constrain the result.
- Requesting a giant final answer instead of one reviewable vertical slice.
- Allowing edits or execution before reviewing assumptions and code.
- Asking for optimization without data size, plan, skew, or measured evidence.
- Repeating the entire prompt after every result instead of using conversation history and observed evidence.
- Accepting generated checks that merely rerun the same logic rather than independently testing an invariant.

## Source of current product behavior

When UI behavior or available actions matter, verify against current official documentation:

- [Tips to improve Genie Code responses](https://docs.databricks.com/aws/en/genie-code/tips)
- [Use Genie Code](https://docs.databricks.com/aws/en/genie-code/use-genie-code)
- [Get coding help from Genie Code](https://docs.databricks.com/aws/en/notebooks/code-assistant)
