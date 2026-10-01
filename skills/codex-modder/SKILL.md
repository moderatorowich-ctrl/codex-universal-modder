---
name: codex-modder
description: Build and test mods for owned single-player PC games with Codex, including engine recon, loader selection, isolated labs, assets, reversible installation, and packaging. Use for game modding requests or compatibility assessment.
---

# Codex game modder

Use this toolkit to take a concrete mod idea through research, implementation, and real-game verification.
It provides a method across engines; it cannot promise support for every game or every requested feature.

## Locate the tools

Run `cmod doctor --json` (or `um doctor --json`). In a clone, use `uv run python -m um` on
Windows, macOS, or Linux. Install the Python CLI separately from installing this skill/plugin:
`uv tool install git+https://github.com/moderatorowich-ctrl/codex-universal-modder`.
Plugin installation does not automatically put the CLI on PATH.

Read [the engine workflow](../mod-any-game/SKILL.md) and only the playbook selected by recon.
All companion skills are siblings under the same skill collection. Knowledge-base searches work
offline after CLI installation; bundled field notes are upstream evidence, not tests of this fork.

## Start a mod

- Establish the game install, exact build, platform/store, desired feature, and single-player/offline mode.
  Read-only recon can start immediately. If the install is unavailable, prepare source and mark runtime
  verification pending. Do not report a mod as working from a successful compile alone.
- Run `cmod scan "<game or install>" --json`, then `cmod kb search "<game>"`. Detection scores are
  heuristic signals. "No anti-cheat found" is not proof that a title has none. Research the current
  official loader/game documentation before installation. Unknown engines need investigation.
- Create a separate lab with `cmod workspace init "<game>" --out "<lab>" --idea "<idea>"`.
  Keep `MODLOG.md` current and record versions, chosen route, and explicit acceptance criteria.
- Back up confirmed save and config folders with `cmod backup create`. Save hints may be incomplete;
  confirm cloud saves, redirected folders, and loader-specific profiles. Record the snapshot paths.
- Prefer the game's supported mod interface, data packs, or an established loader. Build one visible
  slice first. Use exact APIs from the installed version, not guessed method names.

## Assets and installation

Use existing user-provided assets, code/vector assets, available Codex image tools, or the optional fal
tools according to the asset type. fal is not required; paid asset calls require the user's cost scope.
Use the asset-pipeline skill for engine dimensions, alpha, frame ordering, and texture conversion.

For file installs, create `mod.json` in the lab with `schema_version: 1`, a `name`, and a nonempty
`files` list of `{ "source": "dist/example.ext", "target": "Mods/example.ext" }` entries.
Choose destinations from the actual loader documentation. Paths use forward slashes and are relative.
Create a plan with `cmod mod plan mod.json --game "<install>" --out plan.json` and inspect it.
With installation in the user's authorized scope, stop the game and mod managers, then run
`cmod mod apply plan.json --journal transactions/install-001 --offline --yes`.
Restore with `cmod mod restore transactions/install-001 --yes`. A conflict needs investigation;
never edit hashes to make a plan or restore accept a changed game. Keep journals private.
Directory links/junctions, external destinations, and overlapping paths are rejected by this installer.
Executable injection, registry changes, loader setup, and saves need their own scoped handling.

## Verify and deliver

Run relevant build checks, launch the actual offline game, read logs, inspect screenshots, exercise the
feature and a baseline scenario, and verify uninstall. Use the game-automation skill if local tools
are available and taking over input is authorized. A recording is optional unless requested.

Package only original code/assets and installation instructions. Run `cmod publish check dist --game
"<install>"`; review its warnings. It is a heuristic, not proof that every secret or game file is caught.
Record exact versions and status: research, build-tested, runtime-tested, or released. Publish to the
destination already authorized by the user; request missing authorization only for additional actions.
Never claim universal compatibility or verification that did not happen.

Work on owned games in single-player/offline. Do not bypass DRM, ownership checks, or anti-cheat.
Use official offline launch routes. Keep extracted game assets, decompiles, saves, credentials,
install journals, and private paths out of public repositories.
