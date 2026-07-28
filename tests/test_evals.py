"""Layer B — behavioral evals (opt-in).

Each spec in tests/evals/specs/*.yaml runs its skill against a fixture task and
scores the output with an LLM-as-judge. These call the model, cost tokens, and
are non-deterministic, so they do NOT run in the merge gate. Enable them with:

    RUN_EVALS=1 OPENAI_API_KEY=... uv run --extra evals pytest tests/test_evals.py

Add a skill to the behavioral suite by dropping a `<skill>.yaml` here — no code
change needed. See tests/evals/README.md.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import yaml

from conftest import load_skill

EVALS_DIR = Path(__file__).parent / "evals"
sys.path.insert(0, str(EVALS_DIR))

pytestmark = pytest.mark.skipif(
    not (os.environ.get("RUN_EVALS") and os.environ.get("OPENAI_API_KEY")),
    reason="behavioral eval; set RUN_EVALS=1 and OPENAI_API_KEY to run",
)

SPECS = sorted((EVALS_DIR / "specs").glob("*.yaml"))


@pytest.mark.eval
@pytest.mark.parametrize("spec_path", SPECS, ids=lambda p: p.stem)
def test_skill_behavior(spec_path):
    import runner

    spec = yaml.safe_load(spec_path.read_text())
    _, body, _ = load_skill(spec["skill"])

    output = runner.run_skill(body, spec["input"])
    verdict = runner.judge(spec["input"], output, spec["rubric"])

    assert verdict["passed"], (
        f"{spec['skill']} eval failed — {verdict['reasoning']}\n\n--- output ---\n{output}"
    )
