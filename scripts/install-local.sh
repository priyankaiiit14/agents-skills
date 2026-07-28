#!/usr/bin/env bash
# Clone-based install. Delegates to the same CLI logic as `uvx skills-hub`
# so both install paths behave identically.
#
# Usage:
#   ./scripts/install-local.sh [TARGET_DIR] [--target claude|codex|both] \
#       [--scope project|global] [--skills a,b,c]
#
# Defaults: TARGET_DIR = cwd, --target both, --scope project, all skills.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

target_dir="$(pwd)"
agent_target="both"
scope="project"
skills=""

while [ $# -gt 0 ]; do
  case "$1" in
    --target) agent_target="$2"; shift 2 ;;
    --scope) scope="$2"; shift 2 ;;
    --skills) skills="$2"; shift 2 ;;
    *) target_dir="$1"; shift ;;
  esac
done

cmd=(install --project "$target_dir" --target "$agent_target" --scope "$scope")
if [ -n "$skills" ]; then
  IFS=',' read -ra names <<< "$skills"
  cmd+=("${names[@]}")
else
  cmd+=(--all)
fi

PYTHONPATH="$repo_root/src" python3 -m skills_hub.cli "${cmd[@]}"
