# File installation and recovery

Keep the lab outside the game. mod.json has schema_version 1 and explicit relative source/
target pairs. Use forward slashes. Absolute paths, traversal, backslashes, reserved device
names and alternate data streams are refused. Targets cannot duplicate, overlap, or differ
only by case. Symlinks, junctions and reparse points are refused.

Plan writes only its output outside the game, recording SHA-256 hashes and the actual root.
Inspect targets against the loader documentation. The installer cannot determine payload
compatibility or whether a game's offline mode is active. Stop the game and other mod managers.
--offline --yes states operator intent; it does not detect running processes.

Apply requires a fresh journal outside the game. It stages and validates payloads and
originals before writing. Per-file replacement is atomic; the entire multi-file install is
not. An ordinary write failure attempts rollback. Power loss/termination can leave a partial
install. The recovery journal is written before changes. Keep it private: originals may be
game files. Recover with `cmod mod restore transactions/install-001 --yes`.

Restore checks original hashes and every destination before its first game write. A destination
matching neither payload nor original is a conflict. Preserve and investigate newer changes,
then retry when it is in a recognized state. Never change hashes to bypass checks. Repeated
restores can recover interrupted transactions. Failure during preparation does not modify the game.

Restore removes new files and restores original contents. Empty directories may remain.
Permissions, ownership, ACLs, extended attributes and timestamps are not restored. Individual
files are read into memory; use mod payloads rather than whole game archives. Concurrent
writers are unsupported; no OS-level transaction lock is provided. Native runtime hooks,
registry changes, loader setup, save migration and mod-manager state need separate handling.

Use backup separately for saves/config. Archives validate paths, duplicate entries, sizes
and hashes before restore, and snapshot the current state first. --clean optionally removes
new files. Stop writers before snapshot/restore. Folder restoration is not a multi-file atomic
operation; snapshots provide recovery after interruption. Storage must be outside the source.
