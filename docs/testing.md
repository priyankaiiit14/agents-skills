# Testing skills before merge

## Two kinds of tests at a glance

| | Layer A — static + CLI gate | Layer B — behavioral evals |
| --- | --- | --- |
| **Question it answers** | Is the skill *well-formed*? | Does the skill *actually work*? |
| **How** | Parse & lint every `SKILL.md`; smoke-test the CLI | Run the skill on a fixture through the OpenAI API, grade with an LLM-as-judge |
| **Speed / cost** | ~1s, free, deterministic | Minutes, costs tokens, non-deterministic |
| **Runs in CI?** | Yes — **blocks merge** on every PR to `main` | On demand via `workflow_dispatch` only |
| **Needs an API key?** | No | Yes (`OPENAI_API_KEY`) |
| **Files** | `tests/test_skills_static.py`, `tests/test_cli.py` | `tests/test_evals.py`, `tests/evals/` |

---

## Layer A — static + CLI gate (the merge gate)

Deterministic, fast, free. Runs on every PR and push to `main` via
`.github/workflows/test.yml` and blocks merge on failure. Proves each skill is
**well-formed**:

- `SKILL.md` present; frontmatter parses; `name` matches the folder.
- `description` present and within length; only known frontmatter keys (a typo
  like `user-invocabl` fails here); boolean fields are actually booleans.
- Every `subdir/file.ext` a `SKILL.md` references (progressive-disclosure
  resources like `references/jira.md`) resolves.
- Every skill appears in the README "Available Skills" table.
- Every skill has a corresponding eval spec in `tests/evals/specs/<skill>.yaml`.
- `skills-lock.json` has no entries for removed skills.
- The `agent-skills-bundle` CLI still discovers, lists, and installs every skill.

---

## Layer B — behavioral evals (opt-in)

Proves a skill **achieves its purpose**. Each spec in `tests/evals/specs/*.yaml`
runs the skill's `SKILL.md` body as a system prompt against a fixture task
through the OpenAI API, then scores the output against acceptance criteria with
an LLM-as-judge. These call the model, cost tokens, and are non-deterministic,
so they do **not** gate merges.

### When you see the judge result

**Locally** — the result appears inline in the pytest output as the test runs:

```
PASSED  tests/test_evals.py::test_skill_behavior[review]
FAILED  tests/test_evals.py::test_skill_behavior[simplify]
  AssertionError: simplify eval failed — the response did not merge the duplicated functions
  --- output ---
  <full model output shown here>
```

**In CI** — go to **Actions → test → the `behavioral-evals` run** (triggered
manually via `workflow_dispatch`). Click the `behavioral-evals` job, then the
`Layer B — behavioral evals` step. Each spec is a parametrised pytest case; pass
or fail is visible per skill, with the judge's reasoning in the failure message.

---

## Running tests

### Local — Layer A only (what CI enforces, no API key needed)

```bash
scripts/test.sh
```

### Local — Layer A + Layer B

```bash
# put your key in .env (gitignored) — loaded automatically by scripts/test.sh
echo "OPENAI_API_KEY=sk-..." >> .env

scripts/test.sh --evals
```

Override models if needed:

```bash
EVAL_EXECUTOR_MODEL=gpt-4o-mini scripts/test.sh --evals   # cheaper executor
EVAL_JUDGE_MODEL=gpt-4o scripts/test.sh --evals           # stronger judge
```

Run a single skill's eval:

```bash
RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py -k simplify -v
```

### CI — Layer B via `workflow_dispatch`

1. Go to **Actions → test → Run workflow** (top-right button).
2. Optionally set **executor model** and **judge model** (defaults: `gpt-4o` /
   `gpt-4o-mini`).
3. Click **Run workflow**.
4. The `behavioral-evals` job runs all specs in `tests/evals/specs/` and reports
   pass/fail per skill.

The `OPENAI_API_KEY` secret must be set in **Settings → Secrets → Actions**.

---

## What's expected of contributors

- **Every PR:** run `scripts/test.sh` before opening. Layer A must be green —
  CI enforces it and a red gate cannot merge. Most failures are self-explanatory
  (a missing README row, unclosed frontmatter, broken resource reference, `name`
  not matching the folder).

- **Adding a new skill:** the Layer A gate now requires a
  `tests/evals/specs/<skill>.yaml`. Add one in the same PR. See
  `tests/evals/README.md` for the format. Seed the fixture so a working skill
  has a clear right answer; write rubric bullets as explicit, independently
  checkable criteria — not "output looks good."

- **Changing an existing skill's behavior:** if a Layer B spec covers it, run
  `scripts/test.sh --evals` locally and confirm it still passes. If your change
  alters what "correct" means, update the rubric in the same PR.

- **In the PR description:** state what you verified — that Layer A is green, and
  either the Layer B eval result (pass/fail + judge reasoning) or a note
  explaining why the skill is not behaviorally testable.
