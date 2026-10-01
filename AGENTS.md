# Codex Universal Modder

For game modding read skills/codex-modder/SKILL.md first. It routes to the inherited engine
workflow and only the references needed. Use cmod / um or uv run python -m um. Plugin
installation does not install the CLI. Search the knowledge base before choosing a route.

Confirm exact game versions and current official loader documentation. Engine signals and
upstream field notes do not prove runtime compatibility. Work on owned single-player/offline
games; do not bypass anti-cheat, DRM or ownership checks. Back up confirmed saves/config.
Keep game files, decompiles, extracted assets, saves, credentials and journals private.
Stop the game and mod managers before file transactions. Kill processes by exact PID.

Respect existing user authorization. Loader installs, input control, registry changes and
publication must be within scope; do not repeat approval for already authorized actions.

Toolkit code is Python 3.10+ in um/. Run uv run --with pytest pytest -q tests, knowledge
validation, publish lint, uv build and scripts/check_wheel.py. Text IO uses explicit UTF-8.
PowerShell scripts embed C# 5 for Windows PowerShell 5.1. Retain license notices and distinguish
original contributions from upstream work.
