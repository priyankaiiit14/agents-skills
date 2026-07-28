# Behavioral evals (Layer B)

Proves a skill *achieves its purpose*, not just that it's well-formed. Each spec
runs the skill against a fixture task through the Anthropic API and scores the
output against acceptance criteria with an LLM-as-judge.

These are opt-in — they call the model, cost tokens, and are non-deterministic,
so they don't run in the merge gate. The deterministic checks that *do* gate
merges live one level up in `tests/test_skills_static.py` and `tests/test_cli.py`.

## Run

```bash
export ANTHROPIC_API_KEY=...
scripts/test.sh --evals
# or directly:
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -v
```

Models (both env-overridable, see `runner.py`):

- `EVAL_EXECUTOR_MODEL` — runs the skill under test. Default `claude-opus-5`.
- `EVAL_JUDGE_MODEL` — scores the output. Default `claude-haiku-4-5` (cheapest
  current model; raise to `claude-sonnet-5` for borderline rubrics).

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
