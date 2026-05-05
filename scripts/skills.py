#!/usr/bin/env python3
"""
skills.py — install agent skills locally or from GitHub.

Usage:
  # Install all skills from this local repo into a target project
  python skills.py install [TARGET_DIR]

  # Add skills from GitHub (defaults to priyankaiiit14/agents-skills)
  python skills.py add [REPO] [--skills foo,bar] [--target TARGET_DIR] [--branch BRANCH]

Examples:
  python skills.py install
  python skills.py install /path/to/my-project
  python skills.py add
  python skills.py add priyankaiiit14/agents-skills --skills jira-helper,triage
  python skills.py add --target /path/to/my-project
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_REPO = "priyankaiiit14/agents-skills"
DEFAULT_BRANCH = "main"
SKILLS_SUBDIR = "skills"
LOCK_FILE = "skills-lock.json"


def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h.update(str(f.relative_to(path)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def load_lock(target: Path) -> dict:
    lock_path = target / LOCK_FILE
    if lock_path.exists():
        return json.loads(lock_path.read_text())
    return {"version": 1, "skills": {}}


def save_lock(target: Path, lock: dict) -> None:
    (target / LOCK_FILE).write_text(json.dumps(lock, indent=2) + "\n")


# ── local install ────────────────────────────────────────────────────────────

def cmd_install(args):
    repo_root = Path(__file__).resolve().parent.parent
    skills_src = repo_root / SKILLS_SUBDIR
    target_dir = Path(args.target).resolve() / ".claude" / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)

    lock = load_lock(Path(args.target).resolve())
    installed = []

    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        dest = target_dir / name
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(skill_dir, dest)
        lock["skills"][name] = {
            "source": "local",
            "sourceType": "local",
            "skillPath": str(skill_dir.relative_to(repo_root)),
            "computedHash": sha256_dir(dest),
        }
        print(f"  installed  {name}  →  {dest}")
        installed.append(name)

    save_lock(Path(args.target).resolve(), lock)
    print(f"\n{len(installed)} skill(s) installed into {target_dir}")


# ── github add ───────────────────────────────────────────────────────────────

def fetch_zip(repo: str, branch: str) -> zipfile.ZipFile:
    url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    print(f"Fetching {url} ...")
    with urllib.request.urlopen(url) as resp:  # noqa: S310
        return zipfile.ZipFile(io.BytesIO(resp.read()))


def list_skills_in_zip(zf: zipfile.ZipFile, zip_prefix: str) -> list[str]:
    skills_root = f"{zip_prefix}{SKILLS_SUBDIR}/"
    names = set()
    for name in zf.namelist():
        if name.startswith(skills_root) and name != skills_root:
            rest = name[len(skills_root):]
            skill_name = rest.split("/")[0]
            if skill_name:
                names.add(skill_name)
    return sorted(names)


def extract_skill(zf: zipfile.ZipFile, zip_prefix: str, skill_name: str, dest: Path) -> None:
    prefix = f"{zip_prefix}{SKILLS_SUBDIR}/{skill_name}/"
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    for entry in zf.namelist():
        if not entry.startswith(prefix) or entry == prefix:
            continue
        rel = entry[len(prefix):]
        if not rel:
            continue
        out = dest / rel
        if entry.endswith("/"):
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(entry))


def cmd_add(args):
    repo = args.repo or DEFAULT_REPO
    branch = args.branch or DEFAULT_BRANCH
    target_root = Path(args.target).resolve()
    target_dir = target_root / ".claude" / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)

    zf = fetch_zip(repo, branch)
    repo_name = repo.split("/")[-1]
    zip_prefix = f"{repo_name}-{branch}/"

    available = list_skills_in_zip(zf, zip_prefix)
    if not available:
        sys.exit(f"No skills found in {repo} under '{SKILLS_SUBDIR}/'")

    if args.skills:
        wanted = [s.strip() for s in args.skills.split(",")]
        missing = [s for s in wanted if s not in available]
        if missing:
            sys.exit(f"Skill(s) not found in {repo}: {', '.join(missing)}\nAvailable: {', '.join(available)}")
    else:
        wanted = available

    lock = load_lock(target_root)
    installed = []

    for skill_name in wanted:
        dest = target_dir / skill_name
        extract_skill(zf, zip_prefix, skill_name, dest)
        lock["skills"][skill_name] = {
            "source": repo,
            "sourceType": "github",
            "skillPath": f"{SKILLS_SUBDIR}/{skill_name}",
            "computedHash": sha256_dir(dest),
        }
        print(f"  installed  {skill_name}  →  {dest}")
        installed.append(skill_name)

    save_lock(target_root, lock)
    print(f"\n{len(installed)} skill(s) installed into {target_dir}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agent skills installer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="Install skills from this local repo")
    p_install.add_argument("target", nargs="?", default=os.getcwd(), help="Target project dir (default: cwd)")

    p_add = sub.add_parser("add", help="Install skills from GitHub")
    p_add.add_argument("repo", nargs="?", default=None, help=f"GitHub repo (default: {DEFAULT_REPO})")
    p_add.add_argument("--skills", default=None, help="Comma-separated skill names to install (default: all)")
    p_add.add_argument("--target", default=os.getcwd(), help="Target project dir (default: cwd)")
    p_add.add_argument("--branch", default=DEFAULT_BRANCH, help=f"Branch to pull from (default: {DEFAULT_BRANCH})")

    args = parser.parse_args()
    {"install": cmd_install, "add": cmd_add}[args.command](args)


if __name__ == "__main__":
    main()
