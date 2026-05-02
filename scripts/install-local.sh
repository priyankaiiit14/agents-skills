#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_root="${1:-$(pwd)}"
target_dir="$target_root/.claude/skills"

mkdir -p "$target_dir"

for skill_dir in "$repo_root"/skills/*; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"
  rm -rf "$target_dir/$skill_name"
  cp -R "$skill_dir" "$target_dir/$skill_name"
  echo "Installed $skill_name to $target_dir/$skill_name"
done
