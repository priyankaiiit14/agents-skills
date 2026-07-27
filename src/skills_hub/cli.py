#!/usr/bin/env python3
"""
skills-hub — install and manage agent skills.

Usage:
  skills-hub list                        # list all available skills
  skills-hub install review              # install one skill
  skills-hub install review tdd          # install multiple
  skills-hub install --all               # install everything
  skills-hub update                      # re-install tracked skills (pick up new version)
  skills-hub status                      # show installed vs available
  skills-hub create my-skill             # scaffold a new skill for contribution
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from skills_hub import __version__

BUNDLED = Path(__file__).parent / "skills"
LOCK_FILE = "skills-lock.json"
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


# ── lockfile ──────────────────────────────────────────────────────────────────

def load_lock(project: Path) -> dict:
    p = project / LOCK_FILE
    if p.exists():
        return json.loads(p.read_text())
    return {"version": 1, "package_version": None, "skills": {}}


def save_lock(project: Path, lock: dict) -> None:
    (project / LOCK_FILE).write_text(json.dumps(lock, indent=2) + "\n")


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


def install_skill(name: str, skills_dir: Path) -> str:
    src = BUNDLED / name
    if not src.exists():
        sys.exit(f"Skill '{name}' not found. Run `skills-hub list` to see available skills.")
    dest = skills_dir / name
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)
    return sha256_dir(dest)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_list(_args):
    skills = available_skills()
    if not skills:
        print("No skills bundled in this version.")
        return
    print(f"skills-hub v{__version__} — {len(skills)} skill(s) available:\n")
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
    skills_dir = project / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        wanted = available_skills()
        if not wanted:
            sys.exit("No skills available to install.")
    else:
        if not args.names:
            sys.exit("Provide skill name(s) or use --all.")
        wanted = args.names

    lock = load_lock(project)
    lock["package_version"] = __version__

    for name in wanted:
        digest = install_skill(name, skills_dir)
        lock["skills"][name] = {
            "package_version": __version__,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "hash": digest,
        }
        print(f"  installed  {name}  →  {skills_dir / name}")

    save_lock(project, lock)
    print(f"\n{len(wanted)} skill(s) installed (skills-hub v{__version__})")


def cmd_update(args):
    project = Path(args.project).resolve()
    lock = load_lock(project)

    tracked = list(lock["skills"].keys())
    if not tracked:
        print("No skills tracked in skills-lock.json. Run `skills-hub install` first.")
        return

    skills_dir = project / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    available = available_skills()
    updated, skipped = [], []

    for name in tracked:
        if name not in available:
            print(f"  warning: '{name}' is no longer in skills-hub v{__version__}, skipping")
            skipped.append(name)
            continue
        digest = install_skill(name, skills_dir)
        lock["skills"][name].update({
            "package_version": __version__,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "hash": digest,
        })
        print(f"  updated    {name}")
        updated.append(name)

    lock["package_version"] = __version__
    save_lock(project, lock)
    print(f"\n{len(updated)} updated, {len(skipped)} skipped (skills-hub v{__version__})")


def cmd_status(args):
    project = Path(args.project).resolve()
    lock = load_lock(project)
    available = set(available_skills())
    installed = lock.get("skills", {})

    print(f"skills-hub v{__version__}  |  project: {project}\n")
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
    skills_src = Path(os.getcwd()) / "src" / "skills_hub" / "skills"

    if not skills_src.exists():
        sys.exit(
            "No 'src/skills_hub/skills/' directory found in the current directory.\n"
            "Run this command from the root of the skills-hub repo."
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
    print(f"  3. git add src/skills_hub/skills/{name} && git commit -m 'add {name} skill'")
    print(f"  4. Open a PR to main")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="skills-hub",
        description="Install and manage agent skills for Claude Code / Codex",
    )
    parser.add_argument("--version", action="version", version=f"skills-hub {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List available skills in this version")

    # install
    p_install = sub.add_parser("install", help="Install skill(s) into a project")
    p_install.add_argument("names", nargs="*", help="Skill name(s) to install")
    p_install.add_argument("--all", action="store_true", help="Install all available skills")
    p_install.add_argument("--project", default=os.getcwd(), help="Target project dir (default: cwd)")

    # update
    p_update = sub.add_parser("update", help="Update installed skills to the current package version")
    p_update.add_argument("--project", default=os.getcwd(), help="Target project dir (default: cwd)")

    # status
    p_status = sub.add_parser("status", help="Show installed vs available skills")
    p_status.add_argument("--project", default=os.getcwd(), help="Target project dir (default: cwd)")

    # create
    p_create = sub.add_parser("create", help="Scaffold a new skill (run from skills-hub repo root)")
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
