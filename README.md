# Codex Universal Modder

Build, test, and package mods for **owned single-player PC games with Codex**.
An independent MIT-licensed adaptation of [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder).
It retains the engine playbooks, asset tools, Windows game controls, examples and field notes,
and adds a Codex workflow, Windows launchers, diagnostics, isolated labs and reversible file installation.

**No toolkit can guarantee every game or mod idea.** Games need compatible APIs, loaders,
data formats or game-specific engineering. Engine recognition and passing toolkit tests do
not prove a mod works in a particular game. Read [support boundaries](docs/SUPPORT.md) and
[provenance](UPSTREAM.md).

## Quick start

Python 3.10+ and [uv](https://docs.astral.sh/uv/) are recommended. CLI tools work on Windows,
Linux and macOS; the bundled game driver requires Windows/WSL.

```powershell
git clone https://github.com/moderatorowich-ctrl/codex-universal-modder.git
cd codex-universal-modder
uv run python -m um doctor
uv run python -m um scan "C:\Games\MyGame" --json
uv run python -m um workspace init "C:\Games\MyGame" --out "../my-mod-lab" --idea "Add a new item"
```

Open this checkout in Codex and ask:

> Use $codex-modder to add a new item to my owned single-player game at C:\Games\MyGame.
> Inspect its modding route, back up saves, build one working slice, and verify it in game.

A physical `.agents/skills/codex-modder/SKILL.md` entry supports Windows clones without
symlink privileges. Full workflows live in `skills/`.

Install commands for use anywhere:

```powershell
uv tool install git+https://github.com/moderatorowich-ctrl/codex-universal-modder
cmod doctor
cmod scan --list
cmod kb search "Terraria"
```

`um` remains an alias. A clone also includes `bin/cmod.ps1` and `bin/cmod.cmd`.
Without uv, install the clone with `py -3 -m pip install .` on Windows or
`python3 -m pip install .` elsewhere, using an appropriate Python environment.

## Codex plugin or skills

```text
codex plugin marketplace add moderatorowich-ctrl/codex-universal-modder
codex plugin add codex-universal-modder@codex-universal-modder
```

The repository includes a portable plugin manifest, Codex compatibility manifest and
marketplace catalog. **Install the CLI separately:** installing a plugin does not put
`cmod` on PATH. If your host lacks marketplace support, install skills from a clone:

```powershell
py -3 scripts/install_skills.py
```

It copies the collection into `~/.agents/skills`, refusing to overwrite existing skills.
`--dest <directory>` selects another location. See [installation](docs/INSTALL.md).

## Toolkit

| Command | Purpose |
| --- | --- |
| `doctor` | Required Python modules and optional tools; never prints API keys |
| `workspace init` | Separate lab, recon, journal and private folders |
| `scan` | Game discovery, engine/anti-cheat signals, loaders and save hints |
| `mod plan/apply/restore` | Explicit manifest, SHA-256 checks, originals and recovery journal |
| `backup` | Save/config snapshots with path and archive validation |
| `kb` | Offline field notes, note validation and contribution helpers |
| `sprite` / `render3d` | Sprite processing and Blender rendering |
| `win` | Windows/WSL launch, screenshots, input, capture and exact-PID control |
| `video` | ffmpeg showcase editing and contact sheets |
| `fal` | Optional paid art, 3D and audio generation with a separately configured FAL_KEY |
| `publish check` | Heuristic lint for credentials, copied game files and decompiled code |

Twelve reference playbooks cover Unity, Unreal, Godot, Source, .NET/XNA, Bethesda,
Minecraft, Genie/AoE2, established game frameworks, native engines, smaller engines,
and retro workflows. These are guides, not automatically installed adapters. Codex
implements the route for the specific game. Upstream examples retain their provenance.

## Reversible installation

List only your own mod files in `mod.json`, using the actual loader's destination:

```json
{
  "schema_version": 1,
  "name": "my-mod",
  "files": [
    { "source": "dist/MyMod.dll", "target": "BepInEx/plugins/MyMod/MyMod.dll" }
  ]
}
```

That destination is an example for an already configured compatible BepInEx game.
Stop the game and other mod managers before writing. Keep the lab outside the game.

```powershell
cmod mod plan mod.json --game "C:\Games\MyGame" --out plan.json
cmod mod apply plan.json --journal transactions/install-001 --offline --yes
cmod mod restore transactions/install-001 --yes
```

Inspect the plan first. Apply freezes payloads and backs up originals; stale hashes,
duplicate/overlapping destinations, traversal, symlinks and junctions are rejected.
Restore refuses to overwrite newer changes. Journals can contain original game files;
keep them private. See [transactions and recovery](docs/TRANSACTIONS.md).

## Assets, tests and limits

Use imported original assets, code/vector assets, available Codex image tools or optional
fal. No fal account is required for core workflows. ffmpeg is needed for video, Blender
for 3D renders, and game-specific tools for the chosen loader. `doctor` reports availability.

Verify each mod in the actual offline game with logs, inspected screenshots, behavior
checks and uninstall. If the game is unavailable, mark runtime verification pending.
No real game mod was runtime-tested while creating this fork.

```powershell
uv run --with pytest pytest -q tests
uv run python -m um kb check --index
uv run python -m um publish check .
uv build
uv run python scripts/check_wheel.py
```

CI covers Windows, Linux, macOS and Python 3.10. See [validation](docs/VALIDATION.md) for
actual results. Work on owned games in single-player/offline; do not bypass DRM,
ownership checks or anti-cheat. Use official offline launch options. Publish original
mod code/assets, keeping extracted assets, decompiles, saves and credentials private.
The publish checker is a heuristic; review its warnings and the release contents.

Original toolkit, examples, media and field notes: Rehan and universal-modder contributors.
Adaptation and new tools: moderatorowich-ctrl, built with Codex. MIT; retained fonts have
bundled OFL notices. This is an independent project, not an official OpenAI product.
