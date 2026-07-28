#!/usr/bin/env python3
"""
agent-skills-bundle — install and manage agent skills for Claude Code and Codex.

Skills are SKILL.md folders — a cross-agent standard. The same folder works in
Claude Code (.claude/skills/) and Codex (.codex/skills/) unmodified.

Usage:
  agent-skills-bundle list                                 # list available skills
  agent-skills-bundle install review                       # install one skill (both agents, project)
  agent-skills-bundle install review tdd                   # install multiple
  agent-skills-bundle install --all                        # install everything
  agent-skills-bundle install review --target claude       # Claude only
  agent-skills-bundle install review --scope global        # machine-wide (~/.claude, ~/.codex)
  agent-skills-bundle update                               # re-install tracked skills (pick up new version)
  agent-skills-bundle status                               # show installed vs available
  agent-skills-bundle create my-skill                      # scaffold a new skill for contribution
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_skills_bundle import __version__

BUNDLED = Path(__file__).parent / "skills"
LOCK_FILE = "skills-lock.json"
GLOBAL_LOCK = Path.home() / ".agent-skills-bundle" / "skills-lock.json"
AGENT_DIRS = {"claude": ".claude/skills", "codex": ".codex/skills"}
SKILL_TEMPLATE = """\
---
name: {name}
description: One-line description of what this skill does and when to invoke it.
---

# {title}

## When to use

Describe the trigger condition — what the user says or what situation prompts this skill.

## Instructions

Step-by-step instructions for Claude / Codex to follow.

## Verification

How to confirm the skill completed successfully.
"""


# ── destinations & lockfile ─────────────────────────────────────────────────────

def dest_dirs(target: str, scope: str, project: Path) -> dict[str, Path]:
    """Map each selected agent to its skills directory for the given scope."""
    root = Path.home() if scope == "global" else project
    agents = ["claude", "codex"] if target == "both" else [target]
    return {a: root / AGENT_DIRS[a] for a in agents}


def lock_path(scope: str, project: Path) -> Path:
    return GLOBAL_LOCK if scope == "global" else project / LOCK_FILE


def load_lock(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"version": 1, "package_version": None, "target": "both",
            "scope": "project", "skills": {}}


def save_lock(path: Path, lock: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lock, indent=2) + "\n")


# ── helpers ───────────────────────────────────────────────────────────────────

def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h.update(str(f.relative_to(path)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def available_skills() -> list[str]:
    if not BUNDLED.exists():
        return []
    return sorted(d.name for d in BUNDLED.iterdir() if d.is_dir() and not d.name.startswith("."))


def copy_skill(name: str, dest_dir: Path) -> str:
    """Copy one bundled skill folder into dest_dir/<name>; return its content hash."""
    src = BUNDLED / name
    if not src.exists():
        sys.exit(f"Skill '{name}' not found. Run `agent-skills-bundle list` to see available skills.")
    dest = dest_dir / name
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)
    return sha256_dir(dest)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_list(_args):
    skills = available_skills()
    if not skills:
        print("No skills bundled in this version.")
        return
    print(f"agent-skills-bundle v{__version__} — {len(skills)} skill(s) available:\n")
    for name in skills:
        skill_md = BUNDLED / name / "SKILL.md"
        desc = ""
        if skill_md.exists():
            for line in skill_md.read_text().splitlines():
                line = line.strip()
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    break
        print(f"  {name:<30} {desc}")


def cmd_install(args):
    project = Path(args.project).resolve()

    if args.all:
        wanted = available_skills()
        if not wanted:
            sys.exit("No skills available to install.")
    elif not args.names:
        sys.exit("Provide skill name(s) or use --all.")
    else:
        wanted = args.names

    dests = dest_dirs(args.target, args.scope, project)
    path = lock_path(args.scope, project)
    lock = load_lock(path)
    lock.update({"package_version": __version__, "target": args.target, "scope": args.scope})

    for name in wanted:
        for agent, d in dests.items():
            d.mkdir(parents=True, exist_ok=True)
            digest = copy_skill(name, d)
            print(f"  installed  {name}  →  {d / name}  ({agent})")
        lock["skills"][name] = {
            "package_version": __version__,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "hash": digest,
        }

    save_lock(path, lock)
    print(f"\n{len(wanted)} skill(s) installed for {args.target} ({args.scope} scope, "
          f"agent-skills-bundle v{__version__})")


def cmd_update(args):
    project = Path(args.project).resolve()
    path = lock_path(args.scope, project)
    lock = load_lock(path)

    tracked = list(lock["skills"].keys())
    if not tracked:
        print(f"No skills tracked in {path}. Run `agent-skills-bundle install` first.")
        return

    target = lock.get("target", "both")
    dests = dest_dirs(target, args.scope, project)
    available = available_skills()
    updated, skipped = [], []

    for name in tracked:
        if name not in available:
            print(f"  warning: '{name}' is no longer in agent-skills-bundle v{__version__}, skipping")
            skipped.append(name)
            continue
        for agent, d in dests.items():
            d.mkdir(parents=True, exist_ok=True)
            digest = copy_skill(name, d)
        lock["skills"][name].update({
            "package_version": __version__,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "hash": digest,
        })
        print(f"  updated    {name}")
        updated.append(name)

    lock["package_version"] = __version__
    save_lock(path, lock)
    print(f"\n{len(updated)} updated, {len(skipped)} skipped ({args.scope} scope, "
          f"agent-skills-bundle v{__version__})")


def cmd_status(args):
    project = Path(args.project).resolve()
    path = lock_path(args.scope, project)
    lock = load_lock(path)
    available = set(available_skills())
    installed = lock.get("skills", {})

    print(f"agent-skills-bundle v{__version__}  |  scope: {args.scope}  |  "
          f"target: {lock.get('target', '?')}  |  lock: {path}\n")
    print(f"  {'SKILL':<30} {'INSTALLED':<10} {'PKG VERSION'}")
    print(f"  {'-'*30} {'-'*10} {'-'*11}")

    for name in sorted(available):
        if name in installed:
            pkg_ver = installed[name].get("package_version", "?")
            flag = "✓" if pkg_ver == __version__ else f"← was {pkg_ver}"
            print(f"  {name:<30} {'yes':<10} {flag}")
        else:
            print(f"  {name:<30} {'no':<10} available")

    for name in sorted(set(installed) - available):
        print(f"  {name:<30} {'yes':<10} ← removed from v{__version__}")


def cmd_create(args):
    name = args.name.lower().replace(" ", "-")
    skills_src = Path(os.getcwd()) / "src" / "agent_skills_bundle" / "skills"

    if not skills_src.exists():
        sys.exit(
            "No 'src/agent_skills_bundle/skills/' directory found in the current directory.\n"
            "Run this command from the root of the agent-skills-bundle repo."
        )

    dest = skills_src / name
    if dest.exists():
        sys.exit(f"Skill '{name}' already exists at {dest}")

    dest.mkdir()
    skill_file = dest / "SKILL.md"
    skill_file.write_text(
        SKILL_TEMPLATE.format(name=name, title=name.replace("-", " ").title())
    )
    print(f"Created {skill_file}")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_file}")
    print(f"  2. git checkout -b skills/{name}")
    print(f"  3. git add src/agent_skills_bundle/skills/{name} && git commit -m 'add {name} skill'")
    print(f"  4. Open a PR to main")


# ── CLI ───────────────────────────────────────────────────────────────────────

def add_scope(p):
    p.add_argument("--project", default=os.getcwd(), help="Target project dir (default: cwd)")
    p.add_argument(
        "--scope", choices=["project", "global"], default="project",
        help="project: <project>/.claude|.codex/skills (committed, team-shared). "
             "global: ~/.claude|.codex/skills (personal, all projects).",
    )


def main():
    parser = argparse.ArgumentParser(
        prog="agent-skills-bundle",
        description="Install and manage agent skills for Claude Code / Codex",
    )
    parser.add_argument("--version", action="version", version=f"agent-skills-bundle {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List available skills in this version")

    p_install = sub.add_parser("install", help="Install skill(s)")
    p_install.add_argument("names", nargs="*", help="Skill name(s) to install")
    p_install.add_argument("--all", action="store_true", help="Install all available skills")
    p_install.add_argument(
        "--target", choices=["claude", "codex", "both"], default="both",
        help="Which agent(s) to install for (default: both)",
    )
    add_scope(p_install)

    p_update = sub.add_parser("update", help="Update installed skills to the current package version")
    add_scope(p_update)

    p_status = sub.add_parser("status", help="Show installed vs available skills")
    add_scope(p_status)

    p_create = sub.add_parser("create", help="Scaffold a new skill (run from agent-skills-bundle repo root)")
    p_create.add_argument("name", help="Skill name (e.g. data-pipeline-review)")

    args = parser.parse_args()
    {
        "list": cmd_list,
        "install": cmd_install,
        "update": cmd_update,
        "status": cmd_status,
        "create": cmd_create,
    }[args.command](args)


if __name__ == "__main__":
    main()
