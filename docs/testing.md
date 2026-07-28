# Testing skills before merge

The DS/MLE team needs confidence that each skill does what it's supposed to
before it reaches `main`. Testing a skill means two different things, and we
check both — in two layers.

## Two kinds of tests at a glance

| | Layer A — static + CLI gate | Layer B — behavioral evals |
| --- | --- | --- |
| **Question it answers** | Is the skill *well-formed*? | Does the skill *actually work*? |
| **How** | Parse & lint every `SKILL.md`; smoke-test the CLI | Run the skill on a fixture through the API, grade with an LLM-as-judge |
| **Speed / cost** | ~1s, free, deterministic | Minutes, costs tokens, non-deterministic |
| **Runs in CI?** | Yes — **blocks merge** on every PR to `main` | No — opt-in, run locally / on demand |
| **Needs an API key?** | No | Yes (`ANTHROPIC_API_KEY`) |
| **Files** | `tests/test_skills_static.py`, `tests/test_cli.py` | `tests/test_evals.py`, `tests/evals/` |

## Layer A — static + CLI gate (the merge gate)

Deterministic, fast, free. Runs on every PR to `main` via
`.github/workflows/test.yml` and blocks merge on failure. Proves each skill is
**well-formed**:

- `SKILL.md` present; frontmatter parses; `name` matches the folder.
- `description` present and within length; only known frontmatter keys (a typo
  like `user-invocabl` fails here); boolean fields are actually booleans.
- Every `subdir/file.ext` a `SKILL.md` references (progressive-disclosure
  resources like `references/jira.md`) resolves.
- Every skill appears in the README "Available Skills" table.
- `skills-lock.json` has no entries for removed skills.
- The `agent-skills-bundle` CLI still discovers, lists, and installs every skill.

## Layer B — behavioral evals (opt-in)

Proves a skill **achieves its purpose**. Each spec in `tests/evals/specs/*.yaml`
runs the skill against a fixture task through the Anthropic API and scores the
output against acceptance criteria with an LLM-as-judge. These call the model,
cost tokens, and are non-deterministic, so they do **not** gate merges — run them
locally / on demand. Seeded with two exemplars (`review`, `jira-helper`); extend
by adding a YAML spec. See `tests/evals/README.md`.

## Run it

Same entrypoint locally and in CI:

```bash
scripts/test.sh            # Layer A (what CI enforces)
scripts/test.sh --evals    # Layer A + Layer B (needs ANTHROPIC_API_KEY)
```

Or directly:

```bash
uv run --extra dev pytest tests/test_skills_static.py tests/test_cli.py
RUN_EVALS=1 ANTHROPIC_API_KEY=... uv run --extra evals pytest tests/test_evals.py
```

## What's expected of you (contributors)

- **Every PR:** run `scripts/test.sh` before opening it. The Layer A gate must
  be green — CI enforces it on `main`, so a red gate can't merge. Most failures
  are self-explanatory (a missing README row, an unclosed frontmatter block, a
  broken `references/…` path, a `name` that doesn't match the folder).

- **Adding a new skill:** the gate already holds you to the contract
  (frontmatter, README table, resource references, CLI install). On top of that,
  **add a Layer B eval spec** if the skill has a checkable right answer —
  anything prompt-shaped like `review`, `jira-helper`, `simplify`,
  `security-review`. Drop a `tests/evals/specs/<skill>.yaml` (see
  `tests/evals/README.md`); no code change needed. Skills that are open-ended or
  conversational (e.g. `caveman`, `zoom-out`) may not have a meaningful rubric —
  a static-only skill is acceptable, but say so in the PR.

- **Changing an existing skill's behavior:** if a Layer B spec covers it, run
  `scripts/test.sh --evals` and confirm it still passes; if your change alters
  what "correct" means, update the spec's rubric in the same PR. If the skill
  had no eval and your change is behavioral, consider adding one.

- **Adding a bundled resource** (`references/`, `scripts/`, `assets/`): reference
  it from `SKILL.md` with a `subdir/file.ext` path — the gate verifies it
  resolves, which is how we catch dangling references.

- **Writing a good eval:** seed the fixture so a *working* skill has a clear
  right answer (e.g. `review.yaml` plants a specific bug the review must find),
  and write the rubric as explicit, independently checkable bullets — not "output
  looks good." The judge scores each bullet and passes only if all are met.

- **In the PR description:** state what you verified — that the gate is green,
  and either the eval result or a note that the skill is static-only and why.
