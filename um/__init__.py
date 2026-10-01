"""Codex Universal Modder: tools and playbooks for owned single-player game mods.

Subcommands (see `um --help`):
  doctor    required dependencies and optional tools, without exposing credentials
  workspace create a separate game-specific mod lab with recon and a journal
  mod       plan, install and restore file mods with hashes and recovery journals
  scan      find installed games and fingerprint one: engine, runtime, anti-cheat, mod loaders, routes
  fal       generate game assets with fal (sprites, textures, PBR, 3D, rigs, SFX, music, voice, video)
  sprite    cut out, fit, pixelate, recolor and pack 2D sprites
  render3d  render a GLB into sprite frames from a game's camera (Blender)
  video     compile styled showcase videos, trim, mux
  win       Windows (and WSL): screenshots, recording with game-only audio, input, processes
  backup    snapshot and restore save folders before you touch them
  publish   lint a mod folder before sharing: game files, decompiled code, secrets, credits
  kb        the knowledge base: search prior field notes, write your own, check it, open a PR
"""

__version__ = "1.0.0"
