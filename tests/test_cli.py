"""Layer A — smoke tests for the `agent-skills-bundle` CLI.

The CLI is the one piece of real executable code in the bundle; these assert its
core paths (discover, list, install) still work before merge.
"""

from __future__ import annotations

import json
from argparse import Namespace

from agent_skills_bundle import cli

from conftest import skill_names


def test_available_skills_matches_filesystem():
    assert cli.available_skills() == skill_names()


def test_list_runs_and_names_every_skill(capsys):
    cli.cmd_list(Namespace())
    out = capsys.readouterr().out
    for name in skill_names():
        assert name in out, f"'{name}' missing from `list` output"


def test_install_all_copies_skills_and_writes_lock(tmp_path):
    args = Namespace(
        names=[], all=True, target="both", scope="project", project=str(tmp_path)
    )
    cli.cmd_install(args)

    names = skill_names()
    for agent_dir in (".claude/skills", ".codex/skills"):
        for name in names:
            parts = name.split("/")
            # shared → flat dest; project → namespaced dest (drop "project_skills/" prefix)
            dest = "/".join(parts[1:]) if len(parts) == 3 else name
            assert (tmp_path / agent_dir / dest / "SKILL.md").is_file(), \
                f"{agent_dir}/{dest}/SKILL.md missing for skill '{name}'"

    lock = json.loads((tmp_path / "skills-lock.json").read_text())
    assert set(lock["skills"]) == set(names)
    assert lock["package_version"] == cli.__version__
