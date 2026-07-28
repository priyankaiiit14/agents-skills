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
SHARED = BUNDLED / "core"
PROJECTS = BUNDLED / "domain"
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


def available_shared() -> list[str]:
    if not SHARED.exists():
        return []
    return sorted(d.name for d in SHARED.iterdir() if d.is_dir() and not d.name.startswith("."))


def available_domain() -> dict[str, list[str]]:
    """Return {project: [skill, ...]} for all project skills."""
    if not PROJECTS.exists():
        return {}
    out = {}
    for proj in sorted(PROJECTS.iterdir()):
        if not proj.is_dir() or proj.name.startswith("."):
            continue
        skills = sorted(s.name for s in proj.iterdir() if s.is_dir() and not s.name.startswith("."))
        if skills:
            out[proj.name] = skills
    return out


def available_skills() -> list[str]:
    """Return all installable skill identifiers (shared leaf names + domain/proj/skill keys)."""
    names = list(available_shared())
    for proj, skills in available_domain().items():
        for skill in skills:
            names.append(f"domain/{proj}/{skill}")
    return names


def install_skill(name: str, dest_dir: Path) -> list[tuple[str, str, str]]:
    """Install skill(s); return [(lock_key, dest_relative, hash), ...].

    name forms:
      "review"                             shared skill → flat dest
      "domain/search/query-review" single project skill → flat dest
      "domain/search"              all skills for project → namespaced dest
    """
    parts = name.split("/")

    if len(parts) == 1:
        src = SHARED / name
        if not src.exists():
            sys.exit(f"Skill '{name}' not found. Run `agent-skills-bundle list` to see available skills.")
        dest = dest_dir / name
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        return [(name, name, sha256_dir(dest))]

    if parts[0] != "domain" or len(parts) not in (2, 3):
        sys.exit(f"Unknown skill identifier: '{name}'. Use 'review', 'domain/proj', or 'domain/proj/skill'.")

    if len(parts) == 3:
        _, proj, skill = parts
        src = PROJECTS / proj / skill
        if not src.exists():
            sys.exit(f"Skill '{name}' not found.")
        dest = dest_dir / skill  # flat
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        return [(name, skill, sha256_dir(dest))]

    # project-level install: namespaced dest
    _, proj = parts
    proj_dir = PROJECTS / proj
    if not proj_dir.exists():
        sys.exit(f"Project '{proj}' not found under domain/.")
    results = []
    for skill_src in sorted(proj_dir.iterdir()):
        if not skill_src.is_dir() or skill_src.name.startswith("."):
            continue
        dest_rel = f"{proj}/{skill_src.name}"
        dest = dest_dir / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(skill_src, dest)
        results.append((f"domain/{proj}/{skill_src.name}", dest_rel, sha256_dir(dest)))
    return results


# ── commands ──────────────────────────────────────────────────────────────────

def _skill_desc(skill_md: Path) -> str:
    if not skill_md.exists():
        return ""
    for line in skill_md.read_text().splitlines():
        line = line.strip()
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


def cmd_list(_args):
    shared = available_shared()
    projects = available_domain()
    total = len(shared) + sum(len(s) for s in projects.values())
    if not total:
        print("No skills bundled in this version.")
        return
    print(f"agent-skills-bundle v{__version__} — {total} skill(s) available:\n")
    if shared:
        print("Shared skills:")
        for name in shared:
            desc = _skill_desc(SHARED / name / "SKILL.md")
            print(f"  {name:<30} {desc}")
    if projects:
        print("\nProject skills:")
        for proj, skills in projects.items():
            print(f"  [{proj}]")
            for skill in skills:
                desc = _skill_desc(PROJECTS / proj / skill / "SKILL.md")
                print(f"    {skill:<28} {desc}")


def cmd_install(args):
    project = Path(args.project).resolve()

    if args.all:
        wanted = list(available_shared())
        for proj in available_domain():
            wanted.append(f"domain/{proj}")
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

    total = 0
    for name in wanted:
        for agent, d in dests.items():
            d.mkdir(parents=True, exist_ok=True)
            entries = install_skill(name, d)
            for lock_key, dest_rel, digest in entries:
                print(f"  installed  {lock_key}  →  {d / dest_rel}  ({agent})")
                lock["skills"][lock_key] = {
                    "dest": dest_rel,
                    "package_version": __version__,
                    "installed_at": datetime.now(timezone.utc).isoformat(),
                    "hash": digest,
                }
                total += 1

    save_lock(path, lock)
    print(f"\n{total} skill(s) installed for {args.target} ({args.scope} scope, "
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
    updated, skipped = [], []

    for name in tracked:
        parts = name.split("/")
        if len(parts) == 1:
            src = SHARED / name
        elif len(parts) == 3 and parts[0] == "domain":
            src = PROJECTS / parts[1] / parts[2]
        else:
            print(f"  warning: unrecognized skill key '{name}', skipping")
            skipped.append(name)
            continue

        if not src.exists():
            print(f"  warning: '{name}' is no longer in agent-skills-bundle v{__version__}, skipping")
            skipped.append(name)
            continue

        dest_rel = lock["skills"][name].get("dest", name)  # backwards compat: old entries have no dest
        digest = ""
        for agent, d in dests.items():
            dest = d / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(src, dest)
            digest = sha256_dir(dest)

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
    print(f"  {'SKILL':<40} {'INSTALLED':<10} {'PKG VERSION'}")
    print(f"  {'-'*40} {'-'*10} {'-'*11}")

    for name in sorted(available):
        if name in installed:
            pkg_ver = installed[name].get("package_version", "?")
            flag = "✓" if pkg_ver == __version__ else f"← was {pkg_ver}"
            print(f"  {name:<40} {'yes':<10} {flag}")
        else:
            print(f"  {name:<40} {'no':<10} available")

    for name in sorted(set(installed) - available):
        print(f"  {name:<40} {'yes':<10} ← removed from v{__version__}")


def cmd_create(args):
    name = args.name.lower().replace(" ", "-")
    repo_root = Path(os.getcwd())
    skills_src = repo_root / "src" / "agent_skills_bundle" / "skills"

    if not skills_src.exists():
        sys.exit(
            "No 'src/agent_skills_bundle/skills/' directory found in the current directory.\n"
            "Run this command from the root of the agent-skills-bundle repo."
        )

    if args.project_name:
        proj = args.project_name.lower().replace(" ", "-")
        dest = skills_src / "domain" / proj / name
        rel = f"domain/{proj}/{name}"
        install_hint = f"domain/{proj}/{name}"
    else:
        dest = skills_src / "core" / name
        rel = f"core/{name}"
        install_hint = name

    if dest.exists():
        sys.exit(f"Skill '{name}' already exists at {dest}")

    dest.mkdir(parents=True)
    skill_file = dest / "SKILL.md"
    skill_file.write_text(
        SKILL_TEMPLATE.format(name=name, title=name.replace("-", " ").title())
    )
    print(f"Created {skill_file}")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_file}")
    print(f"  2. git checkout -b skills/{name}")
    print(f"  3. git add src/agent_skills_bundle/skills/{rel} && git commit -m 'add {name} skill'")
    print(f"  4. Open a PR to main")
    print(f"\nInstall locally with: agent-skills-bundle install {install_hint}")


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
    p_create.add_argument(
        "--project-name", default=None, metavar="PROJECT",
        help="Create under domain/<PROJECT>/ instead of core/ (e.g. --project-name search)",
    )

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
