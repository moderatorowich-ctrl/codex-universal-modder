"""Behavioral tests for isolated labs, conflict-safe installs, and snapshot integrity."""
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from um import backup, doctor, mod, workspace
from um.paths import relative_path, within


@pytest.fixture
def fixture(tmp_path):
    game = tmp_path / "game"
    lab = tmp_path / "lab"
    game.mkdir()
    lab.mkdir()
    (game / "config.ini").write_bytes(b"original")
    (lab / "replacement.ini").write_bytes(b"modified")
    (lab / "new.txt").write_bytes(b"new file")
    manifest = lab / "mod.json"
    manifest.write_text(json.dumps(dict(schema_version=1, files=[
        dict(source="replacement.ini", target="config.ini"),
        dict(source="new.txt", target="Mods/new.txt"),
    ])), encoding="utf-8")
    plan = lab / "plan.json"
    return game, lab, manifest, plan, tmp_path / "transaction"


def prepared(fixture):
    game, lab, manifest, plan, journal = fixture
    mod.plan(str(manifest), str(game), str(plan))
    return game, lab, manifest, plan, journal


def applied(fixture):
    game, lab, manifest, plan, journal = prepared(fixture)
    mod.apply(str(plan), str(journal), offline=True, yes=True)
    return game, lab, manifest, plan, journal


def test_plan_is_read_only_and_install_restores(fixture):
    game, lab, manifest, plan, journal = prepared(fixture)
    assert (game / "config.ini").read_bytes() == b"original"
    assert not (game / "Mods").exists()
    mod.apply(str(plan), str(journal), offline=True, yes=True)
    assert (game / "config.ini").read_bytes() == b"modified"
    assert (game / "Mods/new.txt").read_bytes() == b"new file"
    mod.restore(str(journal), yes=True)
    assert (game / "config.ini").read_bytes() == b"original"
    assert not (game / "Mods/new.txt").exists()
    mod.restore(str(journal), yes=True)  # retry is safe


@pytest.mark.parametrize("changed", ["source", "destination"])
def test_stale_plan_rejected_before_writes(fixture, changed):
    game, lab, _, plan, journal = prepared(fixture)
    (lab / "replacement.ini" if changed == "source" else game / "config.ini").write_bytes(b"updated")
    with pytest.raises(ValueError, match="changed since plan"):
        mod.apply(str(plan), str(journal), offline=True, yes=True)
    assert not journal.exists()
    assert not (game / "Mods/new.txt").exists()


def test_restore_conflict_does_not_overwrite_other_files(fixture):
    game, _, _, _, journal = applied(fixture)
    (game / "Mods/new.txt").write_bytes(b"newer mod")
    with pytest.raises(ValueError, match="restore conflict"):
        mod.restore(str(journal), yes=True)
    assert (game / "config.ini").read_bytes() == b"modified"
    assert (game / "Mods/new.txt").read_bytes() == b"newer mod"


def test_corrupt_backup_refuses_restore(fixture):
    game, _, _, _, journal = applied(fixture)
    (journal / "original/0").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="backup missing or corrupt"):
        mod.restore(str(journal), yes=True)
    assert (game / "config.ini").read_bytes() == b"modified"


def test_partial_install_recovers(fixture):
    game, _, _, _, journal = applied(fixture)
    state = json.loads((journal / "journal.json").read_text(encoding="utf-8"))
    state["status"] = "applying"
    (journal / "journal.json").write_text(json.dumps(state), encoding="utf-8")
    (game / "Mods/new.txt").unlink()  # simulate interruption before this file was installed
    mod.restore(str(journal), yes=True)
    assert (game / "config.ini").read_bytes() == b"original"


def test_write_failure_rolls_back(fixture, monkeypatch):
    game, _, _, plan, journal = prepared(fixture)
    write = mod.atomic_write
    failed = False

    def failing(path, payload):
        nonlocal failed
        if path == game / "Mods/new.txt" and not failed:
            failed = True
            raise OSError("simulated disk failure")
        write(path, payload)

    monkeypatch.setattr(mod, "atomic_write", failing)
    with pytest.raises(OSError, match="disk failure"):
        mod.apply(str(plan), str(journal), offline=True, yes=True)
    assert (game / "config.ini").read_bytes() == b"original"
    assert not (game / "Mods/new.txt").exists()
    assert json.loads((journal / "journal.json").read_text(encoding="utf-8"))["status"] == "restored"


@pytest.mark.parametrize("path", ["../outside", "/absolute", "C:/absolute", "folder\\file", "a//b", "a/./b", "CON.txt", "com1", "foo.", "foo ", "x:ads", "x\x00y"])
def test_portable_path_rejects_escape_and_aliases(path):
    with pytest.raises(ValueError):
        relative_path(path)


@pytest.mark.parametrize("targets", [["config.ini", "CONFIG.INI"], ["Mods", "Mods/new.txt"]])
def test_overlapping_destinations_rejected(fixture, targets):
    game, _, manifest, plan, _ = fixture
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for entry, target in zip(data["files"], targets):
        entry["target"] = target
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="overlapping"):
        mod.plan(str(manifest), str(game), str(plan))
    assert not plan.exists()


def test_linked_destinations_rejected(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation not permitted on this host")
    with pytest.raises(ValueError, match="symlink"):
        within(root, "link/file.txt")


def test_windows_junction_rejected(tmp_path):
    import os
    import subprocess
    if os.name != "nt":
        pytest.skip("Windows junction test")
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / "link"), str(outside)], capture_output=True)
    if result.returncode:
        pytest.skip("junction creation not permitted")
    try:
        with pytest.raises(ValueError, match="junction|reparse"):
            within(root, "link/file.txt")
    finally:
        (root / "link").rmdir()


@pytest.mark.parametrize("offline,yes", [(False, True), (True, False), (False, False)])
def test_install_requires_intent(fixture, offline, yes):
    _, _, _, plan, journal = prepared(fixture)
    with pytest.raises(ValueError, match="--offline --yes"):
        mod.apply(str(plan), str(journal), offline=offline, yes=yes)
    assert not journal.exists()


def test_journal_cannot_be_inside_game(fixture):
    game, _, _, plan, _ = prepared(fixture)
    with pytest.raises(ValueError, match="outside"):
        mod.apply(str(plan), str(game / "journal"), offline=True, yes=True)


def test_doctor_never_echoes_credential(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "private-value-do-not-echo")
    report = doctor.report()
    assert report["optional_credentials"]["FAL_KEY_configured"]
    assert "private-value-do-not-echo" not in json.dumps(report)


def test_workspace_isolated_and_no_game_writes(tmp_path, monkeypatch):
    game = tmp_path / "game"
    game.mkdir()
    report = dict(name="Fixture", path=str(game), engine=dict(key="native"),
                  playbook="skills/mod-any-game/references/engines/native.md", warnings=[])
    monkeypatch.setattr(workspace.scan, "scan", lambda _: report)
    lab = tmp_path / "lab"
    workspace.init(str(game), str(lab), "new item")
    assert not list(game.iterdir())
    assert (lab / "MODLOG.md").is_file()
    assert json.loads((lab / "recon.json").read_text(encoding="utf-8"))["name"] == "Fixture"
    with pytest.raises(ValueError, match="already exists"):
        workspace.init(str(game), str(lab), "new item")
    with pytest.raises(ValueError, match="separate"):
        workspace.init(str(game), str(game / "lab"), "new item")


def test_backup_unique_and_restore(tmp_path, monkeypatch):
    monkeypatch.setenv("UM_HOME", str(tmp_path / "state"))
    saves = tmp_path / "saves"
    saves.mkdir()
    (saves / "world.sav").write_bytes(b"world")
    one = backup.create(str(saves), "fixture")
    two = backup.create(str(saves), "fixture")
    assert one != two and one.is_file() and two.is_file()
    (saves / "world.sav").write_bytes(b"changed")
    backup.restore("fixture", snapshot=str(one), yes=True)
    assert (saves / "world.sav").read_bytes() == b"world"


@pytest.mark.parametrize("rel", ["../escape.txt", "C:/escape.txt", "folder\\escape.txt"])
def test_malicious_snapshot_rejected_before_restore(tmp_path, monkeypatch, rel):
    monkeypatch.setenv("UM_HOME", str(tmp_path / "state"))
    snapshot = tmp_path / "malicious.zip"
    saves = tmp_path / "saves"
    saves.mkdir()
    (saves / "world.sav").write_bytes(b"world")
    payload = b"attack"
    manifest = dict(source=str(saves), files={rel: dict(size=len(payload), sha1=hashlib.sha1(payload).hexdigest())})
    with zipfile.ZipFile(snapshot, "w") as z:
        z.writestr(rel, payload)
        z.writestr("_um_manifest.json", json.dumps(manifest))
    with pytest.raises(ValueError):
        backup.restore("fixture", snapshot=str(snapshot), yes=True)
    assert (saves / "world.sav").read_bytes() == b"world"
    assert not (tmp_path / "escape.txt").exists()


def test_corrupt_snapshot_rejected(tmp_path):
    snapshot = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(snapshot, "w") as z:
        z.writestr("world.sav", b"changed")
        z.writestr("_um_manifest.json", json.dumps(dict(source=str(tmp_path), files={
            "world.sav": dict(size=7, sha1=hashlib.sha1(b"original").hexdigest())})))
    with pytest.raises(ValueError, match="hash mismatch"):
        backup._manifest(snapshot)


def test_backup_name_traversal_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("UM_HOME", str(tmp_path))
    with pytest.raises(SystemExit):
        backup._root("../outside")


def test_cli_legacy_console_unicode():
    import os
    import subprocess
    import sys
    env = dict(os.environ, PYTHONIOENCODING="cp1252:strict")
    result = subprocess.run([sys.executable, "-m", "um", "kb", "search", "terraria"],
                            env=env, capture_output=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "Terraria" in result.stdout
