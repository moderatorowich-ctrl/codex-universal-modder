"""Create a private, game-specific lab without changing the game installation."""
from __future__ import annotations

from pathlib import Path

from um import scan
from um.common import die, emit
from um.paths import root_path, write_json


def init(game: str, out: str, idea: str) -> dict:
    report = scan.scan(game)
    install = root_path(report["path"])
    dest = root_path(out)
    if dest == install or install in dest.parents or dest in install.parents:
        raise ValueError("lab must be separate from the game installation")
    if dest.exists():
        raise ValueError("lab already exists; use a new output directory")
    dest.mkdir(parents=True)
    for folder in ("src", "assets", "dist", "evidence", "private"):
        (dest / folder).mkdir()
    write_json(dest / "recon.json", report)
    write_json(dest / "mod.json", dict(schema_version=1, name=dest.name, files=[]))
    (dest / "MODLOG.md").write_text(
        f"# {report['name']} mod lab\n\nIdea: {idea}\n\nEngine signal: {report['engine']['key']}\n"
        f"\nPlaybook: {report['playbook']}\n\nStatus: research; not tested in game.\n"
        "\n## Route\nSelect from recon.json after verifying the current loader and game build.\n"
        "\n## Backups\nRecord save/config snapshots and the mod install journal before a modded launch.\n"
        "\n## Verification\nRecord exact game and loader versions, build output, logs, screenshots, and restore results.\n",
        encoding="utf-8")
    (dest / "AGENTS.md").write_text(
        "Use the codex-modder skill. Read MODLOG.md and recon.json, verify current loader documentation, "
        "and keep game files and decompiled code in private/. Engine detection is a signal, not proof of "
        "compatibility. Back up saves; stop the game before any install or restore. Start with one working slice. "
        "Publish only dist/ after checking its contents; record untested features explicitly.\n", encoding="utf-8")
    (dest / ".gitignore").write_text("private/\nevidence/\nrecon.json\ntransactions/\n.env\n.venv/\n__pycache__/\n", encoding="utf-8")
    return dict(workspace=str(dest), game=report["name"], engine=report["engine"], warnings=report["warnings"])


def main(args):
    try:
        emit(init(args.game, args.out, args.idea), True)
    except (OSError, ValueError) as exc:
        die(str(exc))


def register(sub):
    p = sub.add_parser("workspace", help="create an isolated mod lab with recon and a journal")
    cmds = p.add_subparsers(dest="cmd")
    p = cmds.add_parser("init")
    p.add_argument("game")
    p.add_argument("--out", required=True)
    p.add_argument("--idea", required=True)
    p.set_defaults(func=main)
