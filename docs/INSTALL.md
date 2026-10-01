# Installation

Use a clone for development and in-project skill discovery. For CLI use anywhere:
`uv tool install git+https://github.com/moderatorowich-ctrl/codex-universal-modder`.
Python 3.10+ is required; Pillow, numpy and PyYAML install with the package. Without uv,
install the clone into an appropriate Python environment with `python -m pip install .`.
Windows can use `py -3 -m pip install .`.

```text
codex plugin marketplace add moderatorowich-ctrl/codex-universal-modder
codex plugin add codex-universal-modder@codex-universal-modder
```

Portable resources live at the root. .codex-plugin/plugin.json is the compatibility
manifest; .agents/plugins/marketplace.json is the catalog. CLI installation is separate.
Hosts vary in plugin support; clone/skill-copy routes do not need a marketplace.
Packaging follows [official OpenAI documentation](https://developers.openai.com/plugins/build/plugins).

Run `py -3 scripts/install_skills.py` (Windows) or `python3 scripts/install_skills.py`.
Default destination: ~/.agents/skills. The full sibling collection preserves relative
references. Existing skill directories are refused. Use --dest for a separate project's
.agents/skills folder. Use the plugin or copy route to avoid duplicate skills.

Run cmod doctor. Install ffmpeg for video and Blender for 3D; select game compilers and
loaders after verifying exact versions. fal is optional, disabled by default. Set FAL_KEY
securely in the process environment for cmod fal. To enable fal MCP in a trusted clone,
uncomment its .codex/config.toml section after configuring the host environment.
Never commit credentials. Paid generation must fit the user's requested cost scope.

The wheel includes Windows/Blender scripts, fonts and licenses, engine skills and offline
knowledge. cmod kb search needs no first-run sync. Explicit kb sync fetches this fork;
UM_KB_REPO and UM_KB_BRANCH select another source. UM_HOME selects private cache/backup
storage. No OpenAI API key is required; Codex uses its own configured account.
