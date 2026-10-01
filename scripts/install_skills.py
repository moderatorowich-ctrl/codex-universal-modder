"""Install this repository's skills without Windows symlinks or changing Codex config."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def install(destination: Path) -> list[str]:
    source = Path(__file__).resolve().parents[1] / "skills"
    destination = destination.expanduser().resolve()
    skills = sorted(p for p in source.iterdir() if (p / "SKILL.md").is_file())
    # Keep sibling names: the workflows reference each other using relative paths.
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("skill destination must be separate from source")
    conflicts = [p.name for p in skills if (destination / p.name).exists()]
    if conflicts:
        raise ValueError("existing skills would be overwritten: " + ", ".join(conflicts))
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, destination / skill.name)
    return [p.name for p in skills]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dest", type=Path, default=Path.home() / ".agents" / "skills")
    args = p.parse_args()
    try:
        print("Installed: " + ", ".join(install(args.dest)))
    except (ValueError, OSError) as exc:
        p.exit(1, str(exc) + "\n")
