# Behavioral evals (Layer B)

Proves a skill *achieves its purpose*, not just that it's well-formed. Each spec
runs the skill against a fixture task through the OpenAI API and scores the
output against acceptance criteria with an LLM-as-judge.

These are opt-in — they call the model, cost tokens, and are non-deterministic,
so they don't run in the merge gate. The deterministic checks that *do* gate
merges live one level up in `tests/test_skills_static.py` and `tests/test_cli.py`.

## Run

```bash
export OPENAI_API_KEY=...
scripts/test.sh --evals
# or directly:
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -v
```

`.env` file is loaded automatically by `scripts/test.sh` if present — put your
`OPENAI_API_KEY=...` there and it won't be needed on the command line.

### Run a single skill

Use pytest's `-k` flag with the spec filename stem (i.e. the skill name):

```bash
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -k caveman
# multiple skills:
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -k "grill-me or grill-with-docs"
```

### See failure reasons

When a test fails, pytest truncates long assert messages by default. Run with
`-s` to print the judge's reasoning and the full skill output:

```bash
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -v -s -k caveman
```

The failure output includes two sections:
- **judge reasoning** — which rubric criteria weren't met and why
- **raw output** — exactly what the skill produced for the fixture input

Models (both env-overridable, see `runner.py`):

- `EVAL_EXECUTOR_MODEL` — runs the skill under test. Default `gpt-4o`.
- `EVAL_JUDGE_MODEL` — scores the output. Default `gpt-4o-mini`.

## Add a skill to the suite

Drop a `<skill>.yaml` in `specs/` — no code change needed:

```yaml
skill: <skill-folder-name>
input: |
  The fixture task sent to the skill.
rubric: |
  - One bullet per acceptance criterion.
  - The judge passes only if every criterion is met.
```

Write rubrics as explicit, independently checkable criteria (not "output looks
good") — the judge scores each one. Seed the fixture so a *working* skill has a
clear right answer (e.g. `review.yaml` plants a specific bug the review must find).
