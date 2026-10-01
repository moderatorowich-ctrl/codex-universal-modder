"""Conservative portable paths for operations that write to game directories."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath


def no_links(path: Path) -> None:
    for node in (path, *path.parents):
        if node.is_symlink() or getattr(node, "is_junction", lambda: False)():
            raise ValueError(f"symlink/junction is not allowed: {node}")
        if node.exists() and getattr(node.stat(), "st_file_attributes", 0) & 0x400:
            raise ValueError(f"reparse point is not allowed: {node}")


def root_path(value: str | Path) -> Path:
    path = Path(value).expanduser().absolute()
    no_links(path)
    return path.resolve()


def relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("paths must be nonempty, relative, and use forward slashes")
    parts = value.split("/")
    if any(p in ("", ".", "..") or p.endswith((" ", ".")) or
           re.search(r'[<>:"|?*\x00-\x1f]', p) or
           p.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)],
                                       *[f"LPT{i}" for i in range(1, 10)]} for p in parts):
        raise ValueError(f"unsafe relative path: {value!r}")
    return PurePosixPath(*parts).as_posix()


def within(root: Path, rel: str) -> Path:
    path = root.joinpath(*relative_path(rel).split("/"))
    no_links(path)
    path.resolve().relative_to(root.resolve())
    return path


def digest(path: Path) -> str | None:
    no_links(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"expected a file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path: Path, content: bytes) -> None:
    no_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".cmod-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_json(path: Path, data: dict) -> None:
    atomic_write(path, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
