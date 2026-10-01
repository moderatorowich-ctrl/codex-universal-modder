"""Plan, install, and restore a file-based mod using SHA-256 and a recovery journal.

    cmod mod plan mod.json --game GAME --out plan.json
    cmod mod apply plan.json --journal TRANSACTION_DIR --offline --yes
    cmod mod restore TRANSACTION_DIR --yes

Only explicitly listed files are installed. Plans do not modify games. Stop the game
and other mod managers before apply/restore; no process-wide lock is implied.
"""
from __future__ import annotations

import json
from pathlib import Path

from um.common import die, emit
from um.paths import atomic_write, digest, relative_path, root_path, within, write_json


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("expected an object with schema_version: 1")
    return data


def _overlap(a: Path, b: Path) -> bool:
    return a == b or a in b.parents or b in a.parents


def _entries(entries: list) -> list:
    if not isinstance(entries, list) or not entries:
        raise ValueError("files must be a nonempty list")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each file entry must be an object")
        key = relative_path(entry["target"]).casefold()
        if key in seen or any(key.startswith(k + "/") or k.startswith(key + "/") for k in seen):
            raise ValueError("duplicate or overlapping destinations")
        seen.add(key)
    return entries


def _hash(value, optional=False):
    import re
    if optional and value is None:
        return
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid SHA-256 in plan/journal")


def plan(manifest: str, game: str, out: str) -> dict:
    source = root_path(manifest)
    data = _load(source)
    root = root_path(game)
    if not root.is_dir():
        raise ValueError("game folder must exist")
    if _overlap(source.parent, root):
        raise ValueError("keep mod source outside the game folder")
    output = root_path(out)
    if output == root or root in output.parents:
        raise ValueError("plan must be outside the game folder")
    if output.exists():
        raise ValueError("plan output already exists")
    files = []
    for entry in _entries(data.get("files")):
        src = within(source.parent, entry["source"])
        dst = within(root, entry["target"])
        sha = digest(src)
        if sha is None:
            raise ValueError(f"missing source: {src}")
        if src == output:
            raise ValueError("plan cannot overwrite a mod source")
        files.append(dict(source=str(src), target=entry["target"], sha256=sha, before_sha256=digest(dst)))
    result = dict(schema_version=1, name=data.get("name", source.parent.name), game_root=str(root), files=files)
    write_json(output, result)
    return result


def apply(plan_file: str, journal_dir: str, *, offline=False, yes=False) -> dict:
    if not (offline and yes):
        raise ValueError("apply requires --offline --yes; stop the game first")
    data = _load(root_path(plan_file))
    root = root_path(data["game_root"])
    journal = root_path(journal_dir)
    if not root.is_dir() or _overlap(root, journal):
        raise ValueError("journal must be outside an existing game folder")
    if journal.exists():
        raise ValueError("use a new journal directory for each transaction")
    files = _entries(data.get("files"))
    # Validate everything before creating a journal or touching any game file.
    for entry in files:
        _hash(entry["sha256"])
        _hash(entry["before_sha256"], optional=True)
        src = root_path(entry["source"])
        dst = within(root, entry["target"])
        if root == src or root in src.parents or journal == src or journal in src.parents:
            raise ValueError("source must be outside game and journal")
        if digest(src) != entry["sha256"]:
            raise ValueError(f"source changed since plan: {src}")
        if digest(dst) != entry["before_sha256"]:
            raise ValueError(f"destination changed since plan: {dst}")
    journal.mkdir(parents=True)
    state = dict(schema_version=1, game_root=str(root), status="preparing", files=files)
    write_json(journal / "journal.json", state)
    for i, entry in enumerate(files):
        src = root_path(entry["source"])
        dst = within(root, entry["target"])
        # Freeze both sides; later writes never depend on a changing source.
        atomic_write(journal / "staged" / str(i), src.read_bytes())
        if digest(journal / "staged" / str(i)) != entry["sha256"]:
            raise ValueError("source changed during staging; game untouched")
        if entry["before_sha256"] is not None:
            atomic_write(journal / "original" / str(i), dst.read_bytes())
            if digest(journal / "original" / str(i)) != entry["before_sha256"]:
                raise ValueError("destination changed during backup; game untouched")
    state["status"] = "applying"
    write_json(journal / "journal.json", state)
    try:
        for i, entry in enumerate(files):
            dst = within(root, entry["target"])
            if digest(dst) != entry["before_sha256"]:
                raise ValueError(f"destination changed during apply: {dst}")
            staged = journal / "staged" / str(i)
            if digest(staged) != entry["sha256"]:
                raise ValueError("staged payload corrupted")
            atomic_write(dst, staged.read_bytes())
            if digest(dst) != entry["sha256"]:
                raise ValueError("installed payload hash mismatch")
        state["status"] = "applied"
        write_json(journal / "journal.json", state)
    except (OSError, ValueError):
        # Persist the recovery route even when automatic rollback hits a conflict.
        restore(str(journal), yes=True)
        raise
    return dict(status="applied", files=len(files), journal=str(journal))


def restore(journal_dir: str, *, yes=False) -> dict:
    if not yes:
        raise ValueError("restore requires --yes; stop the game first")
    journal = root_path(journal_dir)
    state = _load(journal / "journal.json")
    root = root_path(state["game_root"])
    if not root.is_dir() or _overlap(root, journal):
        raise ValueError("invalid game/journal paths")
    if state.get("status") not in ("applying", "applied", "restoring", "restored"):
        raise ValueError("preparation did not finish; game was not modified")
    files = _entries(state.get("files"))
    # A newer mod or game update is a conflict. Refuse all writes before resolving it.
    for i, entry in enumerate(files):
        _hash(entry["sha256"])
        _hash(entry["before_sha256"], optional=True)
        dst = within(root, entry["target"])
        if digest(dst) not in (entry["sha256"], entry["before_sha256"]):
            raise ValueError(f"restore conflict: {dst}; preserve this change before retrying")
        if entry["before_sha256"] is not None and digest(journal / "original" / str(i)) != entry["before_sha256"]:
            raise ValueError("original backup missing or corrupt")
    state["status"] = "restoring"
    write_json(journal / "journal.json", state)
    for i, entry in reversed(list(enumerate(files))):
        dst = within(root, entry["target"])
        if digest(dst) not in (entry["sha256"], entry["before_sha256"]):
            raise ValueError(f"restore conflict: {dst}")
        if entry["before_sha256"] is None:
            dst.unlink(missing_ok=True)
        else:
            original = journal / "original" / str(i)
            if digest(original) != entry["before_sha256"]:
                raise ValueError("original backup changed during restore")
            atomic_write(dst, original.read_bytes())
        if digest(dst) != entry["before_sha256"]:
            raise ValueError("restored file hash mismatch")
    state["status"] = "restored"
    write_json(journal / "journal.json", state)
    return dict(status="restored", files=len(files), journal=str(journal))


def main(args):
    try:
        if args.cmd == "plan":
            result = plan(args.manifest, args.game, args.out)
        elif args.cmd == "apply":
            result = apply(args.plan, args.journal, offline=args.offline, yes=args.yes)
        else:
            result = restore(args.journal, yes=args.yes)
        emit(result, True)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        die(str(exc))


def register(sub):
    parser = sub.add_parser("mod", help="plan / install / restore file mods with conflict detection", description=__doc__)
    cmds = parser.add_subparsers(dest="cmd")
    p = cmds.add_parser("plan")
    p.add_argument("manifest")
    p.add_argument("--game", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=main)
    p = cmds.add_parser("apply")
    p.add_argument("plan")
    p.add_argument("--journal", required=True)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=main)
    p = cmds.add_parser("restore")
    p.add_argument("journal")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=main)
