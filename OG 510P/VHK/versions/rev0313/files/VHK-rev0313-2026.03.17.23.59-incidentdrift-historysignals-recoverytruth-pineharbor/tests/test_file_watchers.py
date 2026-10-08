from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from vhk.core.file_watchers import run_file_watcher
from vhk.project.loader import load_project
from vhk.system import watch as watch_mod
from vhk.system.watch import FileEvent



def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "data").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj



def test_project_loads_file_watchers(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "file_watchers": [
                {
                    "name": "exports",
                    "macro": "on_export",
                    "directory": "data",
                    "pattern": "*.csv",
                    "event": "new",
                    "recursive": True,
                    "exclude": ["*.tmp"],
                }
            ],
            "macros": {"on_export": "macros/on_export.yaml"},
        },
        {"on_export": {"name": "on_export", "steps": [{"type": "Log", "message": "${file_path}"}]}},
    )

    project = load_project(proj)
    assert len(project.file_watchers) == 1
    watcher = project.file_watchers[0]
    assert watcher.name == "exports"
    assert watcher.pattern == "*.csv"
    assert watcher.event == "new"
    assert watcher.recursive is True
    assert watcher.exclude == ["*.tmp"]



def test_file_watcher_runs_macro_and_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False, "log_dir": "logs"},
            "file_watchers": [
                {
                    "name": "exports",
                    "macro": "hit",
                    "directory": "data",
                    "pattern": "*.txt",
                    "event": "any",
                    "quiet_ms": 75,
                    "vars": {"source": "file_rule"},
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {"type": "AppendFile", "path": "data/hits.txt", "text": "${file_event}|${file_name}|${file_batch_count}|${source}\n"}
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.file_watchers as fw

    events = iter(
        [
            FileEvent(kind="new", path=proj / "data" / "a.txt", name="a.txt", directory=str(proj / "data"), exists=True, mtime_ns=1, size=5, helper="poll", batch_count=2, batch_paths=[str(proj / "data" / "a.txt"), str(proj / "data" / "a.part")], batch_names=["a.txt", "a.part"], batch_kinds=["new", "changed"]),
            FileEvent(kind="new", path=proj / "data" / "a.txt", name="a.txt", directory=str(proj / "data"), exists=True, mtime_ns=1, size=5, helper="poll", batch_count=2, batch_paths=[str(proj / "data" / "a.txt"), str(proj / "data" / "a.part")], batch_names=["a.txt", "a.part"], batch_kinds=["new", "changed"]),
            FileEvent(kind="deleted", path=proj / "data" / "b.txt", name="b.txt", directory=str(proj / "data"), exists=False, mtime_ns=2, size=7, helper="poll", batch_count=1, batch_paths=[str(proj / "data" / "b.txt")], batch_names=["b.txt"], batch_kinds=["deleted"]),
        ]
    )

    seen = []
    def fake_wait(*args, baseline=None, **kwargs):
        seen.append(kwargs)
        return next(events), baseline
    monkeypatch.setattr(fw.watch_mod, "wait_for_file_event", fake_wait)

    stats = run_file_watcher(project, "exports", max_events=3)
    assert stats.events_seen == 3
    assert stats.macro_runs == 2
    assert stats.skipped_duplicates == 1
    assert stats.macro_failures == 0
    assert seen[0]["quiet_ms"] == 75
    assert (proj / "data" / "hits.txt").read_text() == "new|a.txt|2|file_rule\ndeleted|b.txt|1|file_rule\n"

    log_path = proj / "logs" / "file_watcher_exports.jsonl"
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [line["action"] for line in lines] == ["run_macro", "skip_duplicate", "run_macro"]
    assert lines[0]["helper"] == "poll"
    assert lines[0]["batch_count"] == 2
    assert [Path(x).name for x in lines[0]["batch_paths"]] == ["a.txt", "a.part"]
    assert lines[2]["event"] == "deleted"



def test_file_watcher_stops_when_macro_fails_if_configured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "file_watchers": [
                {
                    "name": "fails",
                    "macro": "boom",
                    "directory": "data",
                    "event": "new",
                    "continue_on_macro_error": False,
                }
            ],
            "macros": {"boom": "macros/boom.yaml"},
        },
        {
            "boom": {
                "name": "boom",
                "steps": [{"type": "ReadFile", "path": "missing.txt", "out_var": "x"}],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.file_watchers as fw

    ev = FileEvent(kind="new", path=proj / "data" / "a.txt", name="a.txt", directory=str(proj / "data"), exists=True, mtime_ns=1, size=5, helper="poll")
    monkeypatch.setattr(fw.watch_mod, "wait_for_file_event", lambda *args, baseline=None, **kwargs: (ev, baseline))

    with pytest.raises(RuntimeError):
        run_file_watcher(project, "fails", max_events=1)



def test_wait_for_file_event_polling_detects_changed_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "watch"
    root.mkdir()
    target = root / "report.txt"
    target.write_text("one")

    monkeypatch.setattr(watch_mod, "_which", lambda name: None)
    baseline = watch_mod._scan_file_snapshot(root, pattern="*.txt", recursive=False, exclude=None)

    target.write_text("two")
    ev, snap = watch_mod.wait_for_file_event(
        root,
        event="changed",
        pattern="*.txt",
        baseline=baseline,
        timeout_ms=10,
        poll_ms=0,
        max_attempts=1,
    )

    assert ev.kind == "changed"
    assert ev.name == "report.txt"
    assert ev.exists is True
    assert str(target.resolve()) in snap
