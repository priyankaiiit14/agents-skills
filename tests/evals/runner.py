"""Layer B — behavioral eval harness: run a skill, then judge the result.

A skill's SKILL.md body is an instruction prompt. To test that it *achieves* its
purpose we run it against a fixture task through the Anthropic API, then score
the output against per-spec acceptance criteria with an LLM-as-judge.

Two knobs, both env-overridable:
  EVAL_EXECUTOR_MODEL  runs the skill under test   (default: claude-opus-5)
  EVAL_JUDGE_MODEL     scores the output           (default: claude-haiku-4-5)

The judge defaults to Haiku 4.5 — the cheapest current model ($1/$5 per MTok)
and adequate for rubric grading. Raise it to claude-sonnet-5 for borderline
rubrics where judge reliability matters.

`anthropic` is imported lazily so the Layer A gate never needs it installed.
"""

from __future__ import annotations

import json
import os
import re

EXECUTOR_MODEL = os.environ.get("EVAL_EXECUTOR_MODEL", "claude-opus-5")
JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", "claude-haiku-4-5")

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def _client():
    import anthropic

    return anthropic.Anthropic()


def run_skill(skill_body: str, user_input: str, model: str | None = None) -> str:
    """Run the skill's instructions (as system prompt) against a fixture task."""
    resp = _client().messages.create(
        model=model or EXECUTOR_MODEL,
        max_tokens=4096,
        system=skill_body,
        messages=[{"role": "user", "content": user_input}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def judge(task: str, output: str, rubric: str, model: str | None = None) -> dict:
    """Score `output` against `rubric`. Returns {"passed": bool, "reasoning": str}."""
    prompt = (
        "You are grading the output of an AI skill against acceptance criteria.\n\n"
        f"TASK GIVEN TO THE SKILL:\n{task}\n\n"
        f"SKILL OUTPUT:\n{output}\n\n"
        f"ACCEPTANCE CRITERIA:\n{rubric}\n\n"
        'Reply with ONLY a JSON object: {"passed": <true|false>, "reasoning": "<one sentence>"}. '
        "Pass only if every criterion is met."
    )
    resp = _client().messages.create(
        model=model or JUDGE_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    match = _JSON_OBJECT.search(text)
    if not match:
        raise ValueError(f"judge did not return JSON: {text!r}")
    verdict = json.loads(match.group(0))
    return {"passed": bool(verdict.get("passed")), "reasoning": verdict.get("reasoning", "")}
