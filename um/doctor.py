"""Report local capabilities without installing software or revealing credentials."""
from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import sys

from um.common import emit


def report() -> dict:
    return dict(
        python=platform.python_version(), platform=sys.platform,
        required={m: importlib.util.find_spec(m) is not None for m in ("PIL", "numpy", "yaml")},
        optional_tools={name: shutil.which(name) for name in ("git", "uv", "ffmpeg", "ffprobe", "blender", "dotnet", "java", "gh")},
        optional_credentials={"FAL_KEY_configured": bool(os.environ.get("FAL_KEY"))},
        windows_game_control=(os.name == "nt" or "microsoft" in platform.release().lower()),
        note="fal is optional; imported assets and Codex image tools can be used without it. Engine tools are installed per game.",
    )


def main(args):
    result = report()
    if args.json:
        emit(result, True)
    else:
        print(f"Python {result['python']} on {result['platform']}")
        for name, found in result["required"].items():
            print(f"{'OK' if found else 'MISSING'} required Python module: {name}")
        for name, path in result["optional_tools"].items():
            print(f"{'OK' if path else 'OPTIONAL'} {name}")
        print("FAL_KEY: " + ("configured" if result["optional_credentials"]["FAL_KEY_configured"] else "optional, unset"))
        print(result["note"])
    if not all(result["required"].values()):
        raise SystemExit(1)


def register(sub):
    p = sub.add_parser("doctor", help="check Python dependencies and optional tools (no secrets)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=main)
