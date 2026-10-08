from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from vhk.core.window_watchers import run_window_watcher
from vhk.project.loader import load_project
from vhk.system.wm_events import WmEvent


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "data").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_project_loads_window_watchers(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "window_watchers": [
                {"name": "focus_any", "macro": "on_focus", "event": "focus"},
                {"name": "ws", "macro": "on_ws", "event": "workspace", "enabled": False},
            ],
            "macros": {"on_focus": "macros/on_focus.yaml", "on_ws": "macros/on_ws.yaml"},
        },
        {
            "on_focus": {"name": "on_focus", "steps": [{"type": "Log", "message": "${window_title}"}]},
            "on_ws": {"name": "on_ws", "steps": [{"type": "Log", "message": "${workspace}"}]},
        },
    )

    project = load_project(proj)
    assert len(project.window_watchers) == 2
    assert project.window_watchers[0].name == "focus_any"
    assert project.window_watchers[1].event == "workspace"
    assert project.window_watchers[1].enabled is False


def test_window_watcher_runs_macro_and_logs(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False, "log_dir": "logs"},
            "window_watchers": [
                {
                    "name": "focus_firefox",
                    "macro": "hit",
                    "event": "focus",
                    "when": {"class": "Firefox"},
                    "vars": {"source": "window_rule"},
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {
                        "type": "AppendFile",
                        "path": "data/hits.txt",
                        "text": "${window_class}|${window_title}|${source}\n",
                    }
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    # Two focus events, first is a terminal (skipped), second is firefox (runs).
    schedule = [0.0, 0.1]
    t = {"v": 0.0}

    def gen_events():
        for _ in range(2):
            t["v"] = schedule.pop(0)
            yield WmEvent(wm="i3", kind="focus", name="window", data={"change": "focus"})

    events = gen_events()

    infos = iter(
        [
            ({"id": 1, "class": "Alacritty", "title": "term", "workspace": "1"}, "i3"),
            ({"id": 2, "class": "Firefox", "title": "web", "workspace": "2"}, "i3"),
        ]
    )

    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: next(infos))

    # Match using the real selector matcher.
    stats = run_window_watcher(project, "focus_firefox", max_events=2)
    assert stats.events_seen == 2
    assert stats.macro_runs == 1
    assert stats.skipped_nonmatching == 1
    assert stats.macro_failures == 0

    assert (proj / "data" / "hits.txt").read_text() == "Firefox|web|window_rule\n"

    log_path = proj / "logs" / "window_watcher_focus_firefox.jsonl"
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [line["action"] for line in lines] == ["skip_nonmatching", "run_macro"]
    assert lines[1]["ok"] is True


def test_window_watcher_stops_when_macro_fails_if_configured(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "window_watchers": [
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
                "steps": [{"type": "ReadFile", "path": "missing.txt", "out_var": "x"}],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    events = iter([WmEvent(wm="i3", kind="focus", name="window", data={"change": "focus"})])
    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: ({"id": 1, "class": "Firefox", "title": "x"}, "i3"))

    with pytest.raises(RuntimeError):
        run_window_watcher(project, "fails", max_events=1)



def test_window_watcher_title_events_use_event_payload_and_signature_changes(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False, "log_dir": "logs"},
            "window_watchers": [
                {
                    "name": "title_firefox",
                    "macro": "hit",
                    "event": "title",
                    "when": {"class": "Firefox"},
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {
                        "type": "AppendFile",
                        "path": "data/hits.txt",
                        "text": "${window_class}|${window_title}\n",
                    }
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    events = iter(
        [
            WmEvent(
                wm="i3",
                kind="title",
                name="window",
                data={
                    "change": "title",
                    "container": {
                        "id": 2,
                        "name": "t1",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Firefox", "title": "t1"},
                    },
                },
            ),
            WmEvent(
                wm="i3",
                kind="title",
                name="window",
                data={
                    "change": "title",
                    "container": {
                        "id": 2,
                        "name": "t2",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Firefox", "title": "t2"},
                    },
                },
            ),
            WmEvent(
                wm="i3",
                kind="title",
                name="window",
                data={
                    "change": "title",
                    "container": {
                        "id": 2,
                        "name": "t2",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Firefox", "title": "t2"},
                    },
                },
            ),
        ]
    )

    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: (_ for _ in ()).throw(RuntimeError("should not probe")))

    stats = run_window_watcher(project, "title_firefox", max_events=3)
    assert stats.events_seen == 3
    assert stats.macro_runs == 2
    assert stats.skipped_duplicates == 1

    assert (proj / "data" / "hits.txt").read_text() == "Firefox|t1\nFirefox|t2\n"



def test_window_watcher_urgent_signature_includes_state(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "window_watchers": [
                {
                    "name": "urgent_any",
                    "macro": "hit",
                    "event": "urgent",
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {
                        "type": "AppendFile",
                        "path": "data/hits.txt",
                        "text": "${window_class}|${urgent}\n",
                    }
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    events = iter(
        [
            WmEvent(
                wm="i3",
                kind="urgent",
                name="window",
                data={
                    "change": "urgent",
                    "container": {
                        "id": 2,
                        "urgent": True,
                        "focused": True,
                        "window_properties": {"class": "Alacritty", "title": "term"},
                    },
                },
            ),
            WmEvent(
                wm="i3",
                kind="urgent",
                name="window",
                data={
                    "change": "urgent",
                    "container": {
                        "id": 2,
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Alacritty", "title": "term"},
                    },
                },
            ),
        ]
    )

    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: (_ for _ in ()).throw(RuntimeError("should not probe")))

    stats = run_window_watcher(project, "urgent_any", max_events=2)
    assert stats.macro_runs == 2

    assert (proj / "data" / "hits.txt").read_text() == "Alacritty|True\nAlacritty|False\n"


def test_window_watcher_cooldown_throttles_macro_runs(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False, "log_dir": "logs"},
            "window_watchers": [
                {
                    "name": "cool",
                    "macro": "hit",
                    "event": "focus",
                    "when": {"class": "Firefox"},
                    "cooldown_ms": 1000,
                    "debounce_ms": 0,
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [{"type": "AppendFile", "path": "data/hits.txt", "text": "${window_title}\n"}],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    schedule = [0.0, 0.1]
    t = {"v": 0.0}

    def gen_events():
        for _ in range(2):
            t["v"] = schedule.pop(0)
            yield WmEvent(wm="i3", kind="focus", name="window", data={"change": "focus"})

    events = gen_events()
    infos = iter(
        [
            ({"id": 1, "class": "Firefox", "title": "t1", "workspace": "1"}, "i3"),
            ({"id": 2, "class": "Firefox", "title": "t2", "workspace": "1"}, "i3"),
        ]
    )
    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: next(infos))
    monkeypatch.setattr(ww.time, "time", lambda: t["v"])

    stats = run_window_watcher(project, "cool", max_events=2)
    assert stats.macro_runs == 1
    assert stats.skipped_cooldown == 1
    assert (proj / "data" / "hits.txt").read_text() == "t1\n"

    log_path = proj / "logs" / "window_watcher_cool.jsonl"
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [line["action"] for line in lines] == ["run_macro", "skip_cooldown"]


def test_window_watcher_new_events_use_event_payload(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "window_watchers": [
                {
                    "name": "new_any",
                    "macro": "hit",
                    "event": "new",
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {
                        "type": "AppendFile",
                        "path": "data/hits.txt",
                        "text": "${wm_event}|${window_class}|${window_title}|${workspace}\n",
                    }
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    events = iter(
        [
            WmEvent(
                wm="i3",
                kind="new",
                name="window",
                data={
                    "change": "new",
                    "container": {
                        "id": 10,
                        "name": "Welcome",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Firefox", "title": "Welcome"},
                    },
                },
            )
        ]
    )

    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    # Ensure we do not fall back to probing the active window for new events.
    monkeypatch.setattr(ww, "get_active_window_info", lambda: (_ for _ in ()).throw(RuntimeError("should not probe")))

    stats = run_window_watcher(project, "new_any", max_events=1)
    assert stats.events_seen == 1
    assert stats.macro_runs == 1

    assert (proj / "data" / "hits.txt").read_text() == "new|Firefox|Welcome|None\n"



def test_window_watcher_close_events_use_event_payload(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "window_watchers": [
                {
                    "name": "close_any",
                    "macro": "hit",
                    "event": "close",
                }
            ],
            "macros": {"hit": "macros/hit.yaml"},
        },
        {
            "hit": {
                "name": "hit",
                "steps": [
                    {
                        "type": "AppendFile",
                        "path": "data/hits.txt",
                        "text": "${wm_event}|${window_class}|${window_title}\n",
                    }
                ],
            }
        },
    )
    project = load_project(proj)

    import vhk.core.window_watchers as ww

    events = iter(
        [
            WmEvent(
                wm="i3",
                kind="close",
                name="window",
                data={
                    "change": "close",
                    "container": {
                        "id": 11,
                        "name": "bye",
                        "urgent": False,
                        "focused": True,
                        "window_properties": {"class": "Alacritty", "title": "bye"},
                    },
                },
            )
        ]
    )

    monkeypatch.setattr(ww, "iter_wm_events", lambda **kwargs: events)
    monkeypatch.setattr(ww, "get_active_window_info", lambda: (_ for _ in ()).throw(RuntimeError("should not probe")))

    stats = run_window_watcher(project, "close_any", max_events=1)
    assert stats.events_seen == 1
    assert stats.macro_runs == 1

    assert (proj / "data" / "hits.txt").read_text() == "close|Alacritty|bye\n"
