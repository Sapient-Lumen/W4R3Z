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
