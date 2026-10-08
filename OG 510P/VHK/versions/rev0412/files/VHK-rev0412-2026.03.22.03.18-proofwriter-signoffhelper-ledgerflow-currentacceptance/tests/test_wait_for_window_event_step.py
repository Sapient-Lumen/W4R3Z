from __future__ import annotations

from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.wm_events import WmEvent


def _write_project(tmp_path: Path, steps: list[dict]) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump({"name": "main", "steps": steps}, sort_keys=False)
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump({"name": "proj", "settings": {"event_log": False}, "macros": {"main": "macros/main.yaml"}}, sort_keys=False)
    )
    return project_dir


def test_wait_for_window_event_matches_new_window_selector(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(
        tmp_path,
        [
            {
                "type": "WaitForWindowEvent",
                "event": "new",
                "selector": {"class": "Firefox", "title": "Docs"},
                "timeout_ms": 500,
                "out_event": "event_payload",
                "out_window": "event_window",
            }
        ],
    )
    project = load_project(project_dir)

    import vhk.system.wm_events as wm_mod

    def fake_iter(*, kinds, poll_ms):
        assert kinds == {"new"}
        yield WmEvent(
            wm="sway",
            kind="new",
            name="window",
            data={
                "change": "new",
                "container": {
                    "id": 55,
                    "name": "Docs",
                    "focused": False,
                    "urgent": False,
                    "window_properties": {"class": "Firefox", "title": "Docs"},
                },
            },
        )

    monkeypatch.setattr(wm_mod, "iter_wm_events", fake_iter)

    result = Runner(project).run("main")
    assert result.ok, result.error
    payload = result.vars["event_payload"]
    assert payload["kind"] == "new"
    assert payload["name"] == "window"
    assert result.vars["event_window"]["class"] == "Firefox"
    assert result.vars["event_window"]["title"] == "Docs"


def test_wait_for_window_event_supports_raw_name_and_condition(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(
        tmp_path,
        [
            {
                "type": "WaitForWindowEvent",
                "event": "custom",
                "raw_name": "custom",
                "condition": '"ready" in wm_event["data"]',
                "timeout_ms": 500,
            }
        ],
    )
    project = load_project(project_dir)

    import vhk.system.wm_events as wm_mod

    def fake_iter(*, kinds, poll_ms):
        assert kinds == {"custom"}
        yield WmEvent(wm="hyprland", kind="custom", name="custom", data="phase=boot")
        yield WmEvent(wm="hyprland", kind="custom", name="custom", data="phase=ready")

    monkeypatch.setattr(wm_mod, "iter_wm_events", fake_iter)

    result = Runner(project).run("main")
    assert result.ok, result.error
    assert result.vars["wm_event_payload"]["data"] == "phase=ready"
    assert result.vars["wm_name"] == "hyprland"


def test_wait_for_window_event_times_out_when_no_event_matches(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(
        tmp_path,
        [
            {
                "type": "WaitForWindowEvent",
                "event": "new",
                "selector": {"class": "Firefox"},
                "timeout_ms": 50,
            }
        ],
    )
    project = load_project(project_dir)

    import vhk.system.wm_events as wm_mod

    def fake_iter(*, kinds, poll_ms):
        yield WmEvent(
            wm="sway",
            kind="new",
            name="window",
            data={
                "change": "new",
                "container": {
                    "id": 11,
                    "name": "term",
                    "focused": False,
                    "urgent": False,
                    "window_properties": {"class": "Alacritty", "title": "term"},
                },
            },
        )

    monkeypatch.setattr(wm_mod, "iter_wm_events", fake_iter)

    result = Runner(project).run("main")
    assert not result.ok
    assert "WaitForWindowEvent timed out" in str(result.error)


def test_wait_for_window_event_matches_generic_close_payload(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(
        tmp_path,
        [
            {
                "type": "WaitForWindowEvent",
                "event": "close",
                "selector": {"class": "Firefox", "title": "Docs"},
                "timeout_ms": 500,
                "out_event": "event_payload",
                "out_window": "event_window",
            }
        ],
    )
    project = load_project(project_dir)

    import vhk.system.wm_events as wm_mod

    def fake_iter(*, kinds, poll_ms):
        assert kinds == {"close"}
        yield WmEvent(
            wm="x11",
            kind="close",
            name="poll",
            data={"id": "0x3039", "class": "Firefox", "title": "Docs", "workspace": "Web"},
        )

    monkeypatch.setattr(wm_mod, "iter_wm_events", fake_iter)

    result = Runner(project).run("main")
    assert result.ok, result.error
    payload = result.vars["event_payload"]
    assert payload["kind"] == "close"
    assert payload["name"] == "poll"
    assert result.vars["event_window"]["class"] == "Firefox"
    assert result.vars["event_window"]["title"] == "Docs"


def test_wait_for_window_event_matches_geometry_payload(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(
        tmp_path,
        [
            {
                "type": "WaitForWindowEvent",
                "event": "geometry",
                "selector": {"class": "Firefox", "title": "Docs", "focused": True},
                "timeout_ms": 500,
                "out_event": "event_payload",
                "out_window": "event_window",
            }
        ],
    )
    project = load_project(project_dir)

    import vhk.system.wm_events as wm_mod

    def fake_iter(*, kinds, poll_ms):
        assert kinds == {"geometry"}
        yield WmEvent(
            wm="x11",
            kind="geometry",
            name="poll",
            data={
                "id": "0x3039",
                "class": "Firefox",
                "title": "Docs",
                "focused": True,
                "geometry": {"rect": {"x": 40, "y": 60, "w": 900, "h": 700}, "client": None},
                "old_geometry": {"rect": {"x": 10, "y": 20, "w": 800, "h": 600}},
                "geometry_reason": "geometry",
            },
        )

    monkeypatch.setattr(wm_mod, "iter_wm_events", fake_iter)

    result = Runner(project).run("main")
    assert result.ok, result.error
    payload = result.vars["event_payload"]
    assert payload["kind"] == "geometry"
    assert payload["name"] == "poll"
    assert result.vars["event_window"]["geometry"]["rect"] == {"x": 40, "y": 60, "w": 900, "h": 700}
    assert result.vars["event_window"]["geometry_reason"] == "geometry"
