# Contributing

Contributions from humans and from AI agents are both welcome. Most of them will be **field notes** for the
knowledge base (`knowledge/`), written by an agent at the end of a modding session. That is the point of the
repo: every game one agent figures out becomes something the next agent can read.

## If you are an AI agent
You just modded (or tried to mod) a game, and you learned things. Share them:

1. **Confirm publication is authorized.** A pull request carries the user's GitHub identity.
   Respect existing publication authorization; ask only when it is missing or the scope changes.
2. **Check it's new:** `um kb search "<game>"`. If a note already exists, improve it: add your versions and
   gotchas, and fix what's wrong. Don't write a second one.
3. **Scaffold:** `um kb new --game "<game>" --title "<what you built>" --from-scan "<game>" --agent "<agent (model)>"`.
   It lands in `knowledge/games/<game>/`. Cross-game methods go in `techniques/` (`--kind technique`).
4. **Fill it in** from your journal (`MODLOG.md`):
   - exact versions;
   - the route and why;
   - what the engine really does;
   - build steps;
   - how you verified it, and what you didn't;
   - numbered **gotchas** (symptom → cause → fix).

   Write for an agent that has never seen this game.
5. **Validate:** `um kb check <note>`, then `um kb index`.
6. **Open the PR:** `um kb pr <note>` (a dry run shows the commands), then `um kb pr <note> --yes`. It
   branches, commits the note (+ `media/` + index), forks if needed, pushes, and opens the PR with `gh`.
   Without `gh`, push a branch and open the PR on github.com.

## Hard rules (PRs that break these are closed)
- **No game content:** no game files, extracted assets, ROMs or ISOs, and no links to pirated copies.
- **No decompiled code dumps.** Describe the logic in your own words and name symbols; keep snippets of
  *your own* code short (`um kb check` fails blocks over 150 lines and warns over 60).
- **Nothing that helps cheat in online games:**
  - no memory offsets or signatures for multiplayer titles;
  - no anti-cheat, DRM or ownership-check bypasses;
  - no instructions for injecting into protected online clients.

  Single-player and offline only.
- **No secrets:** API keys, tokens, `.env` files. `um kb check` and `um publish check` catch the common
  ones.
- **Honesty:**
  - name the agent and model (`agents:`);
  - mark `status` truthfully (`idea`, `in-progress`, `working`, `released`, `abandoned`);
  - list what you did not verify.
- **Credit** the people and projects you built on.

## Other contributions
- **Tools (`um/`):**
  - one module per CLI group, with a docstring that doubles as `--help`;
  - add a test in `tests/`;
  - `uv run --with pytest pytest -q tests` must pass.
- **Skills (`skills/`):** the Agent Skills format (`SKILL.md` with `name` + `description`). Keep them
  focused on the workflow; the canonical entry skill targets Codex. Put deep material in `references/`.
- **Engine playbooks** (`skills/mod-any-game/references/engines/`): routes, tools, pitfalls. Link to the
  canonical projects; versions move, so say "check the current release".
- **Examples (`examples/`):** your own code and assets only. Use `fetch` scripts for third-party SDKs, and
  pass `um publish check --game <install>`.

CI runs the tests, `um kb check --index` and the CLI help screens on every PR.
