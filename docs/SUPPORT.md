# Support and evidence

This toolkit helps Codex investigate and implement a mod. It is not an automatic adapter
for every game. Engine detection, a successful build and real-game verification are different
evidence levels. Updates can change APIs, signatures, data formats or loaders.

| Area | Included | Evidence needed for a particular game |
| --- | --- | --- |
| Unity | Mono/IL2CPP recon and playbook | Compatible loader/runtime and in-game tests |
| Unreal | Engine/version, pak/IoStore and loader guidance | Exact build, tools and load order |
| .NET/XNA | Terraria, Stardew, Celeste guidance | Loader/game versions and behavior |
| Godot / Source | Recon and engine references | Exposed data/scripts or community route |
| Bethesda / Minecraft / Genie | Specialized data/loader references | Edition, tools and formats |
| Established frameworks | RE Engine, FromSoft, GTA, Cyberpunk, BG3 guidance | Current title-specific compatibility |
| Smaller/native/retro | Research and fallback playbooks | Game-specific engineering; may be infeasible |
| File transactions | Hashes, originals and recovery journal | Correct targets, closed game, writable folder |
| Game driving | Windows/WSL tools | Local game access and authorized input/capture |

No game is certified by this fork. Upstream field notes describe their own versions and
observations. Scanner fixture tests establish fingerprint behavior, not mod compatibility.
Scores are heuristics, not calibrated probabilities. Scans are bounded and may truncate.
Anti-cheat and save discovery are incomplete; absence of a signal is not proof of absence.

macOS/Linux users can use recon, assets, knowledge and transactions. The bundled win driver
cannot drive native macOS/Linux games. Console firmware, online cheats, anti-cheat bypasses
and DRM circumvention are outside scope.

Record research, build-tested, runtime-tested or released status for each mod. Runtime tests
need exact versions, logs, inspected screenshots, acceptance checks and uninstall verification.
Do not substitute a recording or a successful compile for behavior checks.
