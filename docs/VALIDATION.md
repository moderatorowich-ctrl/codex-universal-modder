# Validation

Results are recorded after local tests and package checks, before publication. Tests use
synthetic fixtures rather than installed game binaries. No real game mod was launched.
CI covers Windows, Ubuntu, macOS and Python 3.10. Ubuntu installs ffmpeg for video tests.
Platform-dependent skips are explicit. Passing CI does not certify a game's mod support.

Local validation on 2026-10-01: Windows, Python 3.13.5, ffmpeg 8.1.2.

- 57 tests passed; one symlink test skipped because creation was unavailable. The Windows
  junction rejection test ran successfully. ffmpeg video compilation ran successfully.
- All seven inherited knowledge notes and their index passed validation.
- Publish lint reported zero failures and zero warnings.
- Wheel and source distribution built; the wheel installed in a separate environment.
  CLI commands, offline knowledge, Windows/Blender scripts and font/license assets passed checks.
- Both Codex entry skills passed the bundled skill validator.
- The actual installed Codex CLI registered and listed the local marketplace, resolving the
  plugin identity, version, source and policy. The temporary registration was removed afterward.

Runtime loader installation, live game input/capture, Blender rendering, and paid fal generation
were not exercised. CI results are visible in the repository Actions tab after publication.
