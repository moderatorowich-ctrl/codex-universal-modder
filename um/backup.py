"""Snapshot folders before touching them (saves, profiles, config, the game's data folder).

    um backup create "C:\\Users\\me\\Documents\\My Games\\Terraria" --name terraria-saves
    um backup list [name]
    um backup diff terraria-saves "C:\\Users\\me\\Documents\\My Games\\Terraria"     # what changed since the last snapshot
    um backup restore terraria-saves [--to DIR] [--snapshot FILE] [--yes]

Snapshots are zip files + a manifest (size + sha1 per file) in ~/.universal-modder/backups/<name>/.
restore first snapshots the current state (so a restore can itself be undone), then puts every file
back and removes files that weren't in the snapshot only with --clean.
Habit that saved the Terraria showcase: keep a pristine copy of any world/scenario a scripted take
destroys, and restore it before each take.
"""
from __future__ import annotations

import hashlib
import json
import time
import zipfile
import re
from pathlib import Path

from um.common import data_dir, die, to_posix
from um.paths import root_path, within, relative_path, atomic_write


def _root(name: str) -> Path:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", name):
        die("backup name must contain 1-100 letters, numbers, underscores or hyphens")
    d = data_dir() / "backups" / name
    root_path(d)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _scan(src: Path) -> dict:
    files = {}
    for p in sorted(src.rglob("*")):
        root_path(p)
        if p.is_file():
            relative_path(p.relative_to(src).as_posix())
            if p.relative_to(src).as_posix() == "_um_manifest.json":
                die("_um_manifest.json is reserved for snapshot metadata")
            h = hashlib.sha1()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            files[p.relative_to(src).as_posix()] = dict(size=p.stat().st_size, sha1=h.hexdigest())
    return files


def create(src: str, name: str | None = None, note: str = "") -> Path:
    s = root_path(to_posix(src))
    if not s.is_dir():
        die(f"not a folder: {s}")
    name = name or s.name.replace(" ", "-").lower()
    storage = _root(name).resolve()
    if s == storage or s in storage.parents or storage in s.parents:
        die("backup storage must be separate from source")
    files = _scan(s)
    total = sum(f["size"] for f in files.values())
    if total > 20 << 30:
        die(f"{total / 2**30:.1f} GB - too big to snapshot casually; back up the specific subfolder you'll change")
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"-{time.time_ns() % 1_000_000_000:09d}"
    out = _root(name) / f"{stamp}.zip"
    with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel in files:
            z.write(s / rel, rel)
        z.writestr("_um_manifest.json", json.dumps(dict(source=str(s), created=stamp, note=note, files=files), indent=1))
    _manifest(out)  # Detect source changes during snapshot creation before reporting success.
    print(f"{out}  ({len(files)} files, {total / 2**20:.1f} MB)")
    return out


def snapshots(name: str) -> list[Path]:
    return sorted(_root(name).glob("*.zip"))


def _manifest(zp: Path) -> dict:
    root_path(zp)
    with zipfile.ZipFile(zp) as z:
        m = json.loads(z.read("_um_manifest.json"))
        if not isinstance(m, dict) or not isinstance(m.get("source"), str) or not isinstance(m.get("files"), dict):
            raise ValueError("invalid snapshot manifest")
        expected = {"_um_manifest.json", *m["files"]}
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("snapshot contains duplicate or unlisted entries")
        if sum(i.file_size for i in z.infolist()) > 20 << 30:
            raise ValueError("snapshot exceeds 20 GB limit")
        seen = set()
        for rel, info in m["files"].items():
            relative_path(rel)
            key = rel.casefold()
            if key in seen or any(key.startswith(k + "/") or k.startswith(key + "/") for k in seen):
                raise ValueError("snapshot paths collide")
            seen.add(key)
            if not isinstance(info, dict) or not isinstance(info.get("size"), int) or info["size"] < 0 or not re.fullmatch(r"[0-9a-f]{40}", str(info.get("sha1", ""))):
                raise ValueError("invalid snapshot file metadata")
            if z.getinfo(rel).file_size != info["size"]:
                raise ValueError("snapshot size mismatch")
            h = hashlib.sha1()
            with z.open(rel) as stream:
                for chunk in iter(lambda: stream.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != info["sha1"]:
                raise ValueError("snapshot hash mismatch")
        return m


def diff(name: str, target: str | None = None, snapshot: str | None = None) -> dict:
    zp = Path(snapshot) if snapshot else (snapshots(name) or [None])[-1]
    if not zp:
        die(f"no snapshots for {name}")
    m = _manifest(zp)
    t = Path(to_posix(target or m["source"]))
    now = _scan(t) if t.is_dir() else {}
    old = m["files"]
    res = dict(snapshot=str(zp), target=str(t),
               added=sorted(set(now) - set(old)), removed=sorted(set(old) - set(now)),
               changed=sorted(k for k in set(now) & set(old) if now[k]["sha1"] != old[k]["sha1"]))
    return res


def restore(name: str, to: str | None = None, snapshot: str | None = None, clean: bool = False, yes: bool = False):
    zp = Path(snapshot) if snapshot else (snapshots(name) or [None])[-1]
    if not zp:
        die(f"no snapshots for {name}")
    m = _manifest(zp)
    t = root_path(to_posix(to or m["source"]))
    for rel in m["files"]:
        within(t, rel)
    if t == zp.resolve() or t in zp.resolve().parents:
        die("restore target cannot contain its snapshot archive")
    d = diff(name, str(t), str(zp))
    print(f"restore {zp.name} -> {t}: {len(d['changed'])} changed, {len(d['removed'])} missing, {len(d['added'])} new since"
          + (" (new files will be deleted: --clean)" if clean else " (new files kept)"))
    if not yes:
        die("re-run with --yes to do it")
    if t.is_dir():
        create(str(t), name + "-pre-restore", note=f"automatic, before restoring {zp.name}")
    t.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zp) as z:
        for rel in m["files"]:
            dst = within(t, rel)
            with z.open(rel) as src:
                atomic_write(dst, src.read())
    if clean:
        for rel in d["added"]:
            within(t, rel).unlink(missing_ok=True)
    print("restored", len(m["files"]), "files")


def _main(a):
    if a.cmd == "create":
        create(a.src, a.name, a.note or "")
    elif a.cmd == "list":
        root = data_dir() / "backups"
        names = [a.name] if a.name else sorted(p.name for p in root.glob("*") if p.is_dir()) if root.exists() else []
        for n in names:
            for zp in snapshots(n):
                m = _manifest(zp)
                print(f"{n:28} {zp.name}  {len(m['files']):5} files  {m['source']}  {m.get('note', '')}")
    elif a.cmd == "diff":
        print(json.dumps(diff(a.name, a.target, a.snapshot), indent=1))
    elif a.cmd == "restore":
        restore(a.name, a.to, a.snapshot, a.clean, a.yes)


def main(a):
    try:
        _main(a)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        die(str(exc))


def register(sub):
    import argparse
    p = sub.add_parser("backup", help="snapshot / diff / restore save folders before you touch them",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("create", help="snapshot a folder")
    q.add_argument("src")
    q.add_argument("--name")
    q.add_argument("--note")
    q.set_defaults(func=main)
    q = cs.add_parser("list", help="list snapshots")
    q.add_argument("name", nargs="?")
    q.set_defaults(func=main)
    q = cs.add_parser("diff", help="what changed since the latest snapshot")
    q.add_argument("name")
    q.add_argument("target", nargs="?")
    q.add_argument("--snapshot")
    q.set_defaults(func=main)
    q = cs.add_parser("restore", help="restore the latest (or --snapshot) snapshot")
    q.add_argument("name")
    q.add_argument("--to")
    q.add_argument("--snapshot")
    q.add_argument("--clean", action="store_true", help="also delete files created after the snapshot")
    q.add_argument("--yes", action="store_true")
    q.set_defaults(func=main)
