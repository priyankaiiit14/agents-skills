---
name: prompt-prep
description: Use when the user wants to prepare a compact, structured Agent task prompt from a small set of inputs. Ask only for the missing fields needed to fill the prompt template, then return the final prompt in copy-ready form. Do not use for solving the task itself.
---

# Prompt Prep

Your job is to turn partial user intent into a compact, structured task prompt.

## When to use

Use this skill when the user wants to:
- draft a low-token Agent prompt
- fill a task template
- prepare a scoped implementation, investigation, review, or explanation prompt
- answer a small intake questionnaire and get a final prompt

Do not use this skill when the user already wants the task executed directly.

## Workflow

1. Determine which of these fields are missing:
- `Task`
- `Scope`
- `Do not inspect`
- `Goal`
- `Constraints`
- `Inputs`
- `Expected output`

2. Ask only for the missing fields.
- Keep questions concise.
- Combine related missing fields into the fewest questions possible.
- Prefer one short message with a numbered list.
- Do not ask for fields the user already provided.

3. If the user gave very little context, ask in this order:
1. What kind of task is this: `investigate`, `implement`, `review`, or `explain`?
2. Which files, folders, PR, commit, or subsystem should be in scope?
3. What is the one concrete outcome?
4. What constraints should be enforced?
5. What exact inputs already exist: failing command, error, reference, branch, ticket, or diff?
6. What output format do they want: diagnosis only, patch plus validation, findings only, or explanation?

4. After you have enough information, produce exactly one final prompt in this format:

```text
Task: <investigate | implement | review | explain>

Scope:
- Files/area: <exact paths or subsystem>
- Do not inspect: <areas to skip>

Goal:
- <one concrete outcome>

Constraints:
- Smallest reasonable change
- No new deps
- No unrelated edits
- <additional constraints from user>

Inputs:
- Failing command: <command or n/a>
- Error/output: <exact error or n/a>
- Reference: <PR / commit / Jira / workflow id / n/a>

Expected output:
- <diagnosis only | patch + targeted validation | findings only | explanation>
- Keep response concise
```

## Rules

- Keep the prompt compact.
- Prefer exact paths over broad repo areas.
- Preserve user wording for errors and constraints.
- If the user says not to inspect an area, keep it out of scope.
- Do not add generic advice after the final prompt unless the user asks.
- Do not execute the task. This skill only prepares the prompt.
