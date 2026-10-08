from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.watch import FileEvent


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "data").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_file_event_step_uses_watch_helper_and_sets_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForFileEvent",
                        "directory": "data",
                        "event": "deleted",
                        "pattern": "*.txt",
                        "recursive": True,
                        "exclude": ["*.tmp", "${skip_glob}"],
                        "timeout_ms": 100,
                        "poll_ms": 0,
                        "max_attempts": 1,
                        "quiet_ms": 40,
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    seen = {}

    def fake_wait(directory, **kwargs):
        seen["directory"] = directory
        seen.update(kwargs)
        return (
            FileEvent(
                kind="deleted",
                path=proj / "data" / "gone.txt",
                name="gone.txt",
                directory=str(proj / "data"),
                exists=False,
                mtime_ns=123,
                size=9,
                helper="inotifywait",
                raw_event="DELETE",
                batch_count=2,
                batch_paths=[str(proj / "data" / "gone.txt"), str(proj / "data" / "later.txt")],
                batch_names=["gone.txt", "later.txt"],
                batch_kinds=["deleted", "deleted"],
            ),
            {},
        )

    monkeypatch.setattr(runner_mod.watch_mod, "wait_for_file_event", fake_wait)

    res = Runner(load_project(proj)).run("m", initial_vars={"skip_glob": "*.bak"})
    assert res.ok
    assert Path(seen["directory"]).resolve() == (proj / "data").resolve()
    assert seen["event"] == "deleted"
    assert seen["pattern"] == "*.txt"
    assert seen["recursive"] is True
    assert seen["exclude"] == ["*.tmp", "*.bak"]
    assert seen["quiet_ms"] == 40
    assert res.vars["file_event"] == "deleted"
    assert Path(res.vars["file_path"]).name == "gone.txt"
    assert res.vars["file_name"] == "gone.txt"
    assert res.vars["file_dir"] == str(proj / "data")
    assert res.vars["file_exists"] is False
    assert res.vars["file_mtime_ns"] == 123
    assert res.vars["file_size"] == 9
    assert res.vars["file_event_helper"] == "inotifywait"
    assert res.vars["file_event_raw"] == "DELETE"
    assert res.vars["file_batch_count"] == 2
    assert [Path(x).name for x in res.vars["file_batch_paths"]] == ["gone.txt", "later.txt"]
    assert res.vars["file_batch_names"] == ["gone.txt", "later.txt"]
    assert res.vars["file_batch_kinds"] == ["deleted", "deleted"]


def test_wait_for_file_event_step_end_to_end_polling(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForFileEvent",
                        "directory": "data",
                        "event": "changed",
                        "pattern": "*.txt",
                        "timeout_ms": 1500,
                        "poll_ms": 10,
                        "max_poll_ms": 20,
                        "jitter_ms": 0,
                        "min_size": 3,
                        "stable_ms": 30,
                    },
                    {"type": "AppendFile", "path": "data/hits.txt", "text": "${file_event}|${file_name}|${file_exists}\n"},
                ],
            }
        },
    )

    target = proj / "data" / "report.txt"
    target.write_text("one")

    import vhk.system.watch as watch_mod

    monkeypatch.setattr(watch_mod, "_which", lambda name: None)

    def mutate():
        time.sleep(0.03)
        target.write_text("three")

    t = threading.Thread(target=mutate, daemon=True)
    t.start()
    res = Runner(load_project(proj)).run("m")
    t.join(timeout=1)

    assert res.ok
    assert res.vars["file_event"] == "changed"
    assert Path(res.vars["file_path"]).name == "report.txt"
    assert res.vars["file_name"] == "report.txt"
    assert res.vars["file_exists"] is True
    assert res.vars["file_size"] == 5
    assert (proj / "data" / "hits.txt").read_text() == "changed|report.txt|True\n"


def test_wait_for_file_event_polling_coalesces_burst(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "watch"
    root.mkdir()

    import vhk.system.watch as watch_mod

    monkeypatch.setattr(watch_mod, "_which", lambda name: None)

    def mutate():
        time.sleep(0.03)
        (root / "a.txt").write_text("one")
        time.sleep(0.03)
        (root / "b.txt").write_text("two")

    t = threading.Thread(target=mutate, daemon=True)
    t.start()
    ev, snap = watch_mod.wait_for_file_event(
        root,
        event="new",
        pattern="*.txt",
        timeout_ms=1000,
        poll_ms=10,
        max_poll_ms=20,
        jitter_ms=0,
        quiet_ms=80,
    )
    t.join(timeout=1)

    assert ev.kind == "new"
    assert ev.name == "b.txt"
    assert ev.batch_count == 2
    assert [Path(x).name for x in ev.batch_paths] == ["a.txt", "b.txt"]
    assert ev.batch_names == ["a.txt", "b.txt"]
    assert ev.batch_kinds == ["new", "new"]
    assert str((root / "b.txt").resolve()) in snap
