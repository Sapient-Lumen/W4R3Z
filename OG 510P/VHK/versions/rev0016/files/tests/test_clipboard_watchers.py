from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from vhk.core.clipboard_watchers import run_clipboard_watcher
from vhk.project.loader import load_project



def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj



def test_project_loads_clipboard_watchers(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "clipboard_watchers": [
                {
                    "name": "urls",
                    "macro": "open_url",
                    "pattern": r"https?://\\S+",
                    "flags": ["IGNORECASE"],
                    "selection": "clipboard",
                    "vars": {"source": "watcher"},
                }
            ],
            "macros": {"open_url": "macros/open_url.yaml"},
        },
        {"open_url": {"name": "open_url", "steps": [{"type": "Log", "message": "${clipboard_text}"}]}},
    )

    project = load_project(proj)
    assert len(project.clipboard_watchers) == 1
    watcher = project.clipboard_watchers[0]
    assert watcher.name == "urls"
    assert watcher.flags == ["IGNORECASE"]
    assert watcher.vars["source"] == "watcher"



def test_clipboard_watcher_runs_matching_macro_and_logs(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False, "log_dir": "logs"},
            "clipboard_watchers": [
                {
                    "name": "urls",
                    "macro": "on_url",
                    "pattern": r"https?://(\S+)",
                    "selection": "clipboard",
                    "vars": {"source": "clipboard_rule"},
                }
            ],
            "macros": {"on_url": "macros/on_url.yaml"},
        },
        {
            "on_url": {
                "name": "on_url",
                "steps": [
                    {"type": "AppendFile", "path": "data/hits.txt", "text": "${clipboard_text}|${source}|${clipboard_match_groups.0}\n"}
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.clipboard_watchers as cw

    events = iter([
        "https://example.com/path",
        "https://example.com/path",
        "not a url",
    ])

    monkeypatch.setattr(cw.clipboard_mod, "read", lambda selection="clipboard": "initial")
    monkeypatch.setattr(
        cw.watch_mod,
        "wait_for_clipboard_change",
        lambda read_func, **kwargs: next(events),
    )

    stats = run_clipboard_watcher(project, "urls", max_events=3)
    assert stats.events_seen == 3
    assert stats.macro_runs == 1
    assert stats.skipped_duplicates == 1
    assert stats.skipped_nonmatching == 1
    assert stats.macro_failures == 0

    assert (proj / "data" / "hits.txt").read_text() == "https://example.com/path|clipboard_rule|example.com/path\n"

    log_path = proj / "logs" / "clipboard_watcher_urls.jsonl"
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [line["action"] for line in lines] == ["run_macro", "skip_duplicate", "skip_nonmatching"]
    assert lines[0]["ok"] is True
    assert lines[2]["pattern"] == r"https?://(\S+)"



def test_clipboard_watcher_stops_when_macro_fails_and_configured_to_fail_fast(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "clipboard_watchers": [
                {
                    "name": "fails",
                    "macro": "boom",
                    "continue_on_macro_error": False,
                }
            ],
            "macros": {"boom": "macros/boom.yaml"},
        },
        {
            "boom": {
                "name": "boom",
                "steps": [
                    {"type": "ReadFile", "path": "missing.txt", "out_var": "x"},
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.clipboard_watchers as cw

    monkeypatch.setattr(cw.clipboard_mod, "read", lambda selection="clipboard": "initial")
    monkeypatch.setattr(cw.watch_mod, "wait_for_clipboard_change", lambda read_func, **kwargs: "trigger")

    with pytest.raises(RuntimeError):
        run_clipboard_watcher(project, "fails", max_events=1)
