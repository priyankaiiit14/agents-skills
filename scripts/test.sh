#!/usr/bin/env bash
# Merge gate — the same entrypoint CI runs. Run before opening a PR to main.
#
#   scripts/test.sh          # Layer A: static + CLI gate (fast, free)
#   scripts/test.sh --evals  # also run Layer B behavioral evals (needs OPENAI_API_KEY)
#
# Local .env is loaded automatically if present. Override models via env:
#   EVAL_EXECUTOR_MODEL=gpt-4o EVAL_JUDGE_MODEL=gpt-4o-mini scripts/test.sh --evals
set -euo pipefail
cd "$(dirname "$0")/.."

# Load .env if present (local dev convenience; never committed).
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

RUN_EVALS_STAGE=0
if [[ "${1:-}" == "--evals" ]]; then
    RUN_EVALS_STAGE=1
    shift
fi

echo "== Layer A: static + CLI gate =="
uv run --extra dev pytest tests/test_skills_static.py tests/test_cli.py "$@"

if [[ "$RUN_EVALS_STAGE" == "1" ]]; then
    echo "== Layer B: behavioral evals =="
    RUN_EVALS=1 uv run --extra evals pytest tests/test_evals.py
fi
