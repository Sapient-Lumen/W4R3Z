from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from vhk.core.models import I3WindowSelector
from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _cp(args: list[str], rc: int = 0, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=rc, stdout=out, stderr=err)


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_focus_window_matching_uses_xdotool_activation_and_verifies_target(monkeypatch: pytest.MonkeyPatch) -> None:
    import vhk.system.active_window as aw

    row = {"id": "0x3039", "class": "Firefox", "title": "Docs", "workspace": "1", "focused": False}
    monkeypatch.setattr(aw, "get_window_list_snapshot", lambda **kwargs: ([dict(row)], "x11"))

    calls: list[list[str]] = []
    activated = {"done": False}

    def fake_which(name: str) -> str | None:
        if name == "xdotool":
            return "/bin/xdotool"
        return None

    def fake_run(cmd, capture_output=True, text=True, timeout=None, **kwargs):
        calls.append(list(cmd))
        activated["done"] = True
        return _cp(list(cmd), 0)

    def fake_active_info():
        if activated["done"]:
            return ({"id": "0x3039", "class": "Firefox", "title": "Docs", "focused": True}, "x11")
        return ({"id": "0x7777", "class": "Alacritty", "title": "shell", "focused": True}, "x11")

    monkeypatch.setattr(aw.shutil, "which", fake_which)
    monkeypatch.setattr(aw.subprocess, "run", fake_run)
    monkeypatch.setattr(aw, "get_active_window_info", fake_active_info)
    monkeypatch.setattr(aw.time, "sleep", lambda *_args, **_kwargs: None)

    focused_row, wm = aw.focus_window_matching(I3WindowSelector(wm_class="Firefox", title="Docs"), timeout_ms=250, poll_ms=10)
    assert wm == "x11"
    assert focused_row["id"] == "0x3039"
    assert calls == [["/bin/xdotool", "windowactivate", "--sync", "12345"]]


def test_focus_window_matching_uses_kdotool_on_kwin(monkeypatch: pytest.MonkeyPatch) -> None:
    import vhk.system.active_window as aw
    import vhk.system.kdotool as kdotool_mod

    row = {"id": "{abc}", "class": "konsole", "title": "Work", "workspace": "2", "focused": False}
    monkeypatch.setattr(aw, "get_window_list_snapshot", lambda **kwargs: ([dict(row)], "kwin"))

    calls: list[list[str]] = []
    activated = {"done": False}

    def fake_run_kdotool(args: list[str], *, timeout_s: float = 3.0) -> str:
        calls.append(list(args))
        activated["done"] = True
        return ""

    def fake_active_info():
        if activated["done"]:
            return ({"id": "{abc}", "class": "konsole", "title": "Work", "focused": True}, "kwin")
        return ({"id": "{zzz}", "class": "konsole", "title": "Other", "focused": True}, "kwin")

    monkeypatch.setattr(kdotool_mod, "run_kdotool", fake_run_kdotool)
    monkeypatch.setattr(aw, "get_active_window_info", fake_active_info)
    monkeypatch.setattr(aw.time, "sleep", lambda *_args, **_kwargs: None)

    focused_row, wm = aw.focus_window_matching(I3WindowSelector(wm_class="konsole", title="Work"), timeout_ms=250, poll_ms=10)
    assert wm == "kwin"
    assert focused_row["id"] == "{abc}"
    assert calls == [["windowactivate", "{abc}"]]


def test_wait_for_window_x11_uses_snapshot_fallback_and_can_focus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "WaitForWindow",
                    "selector": {"class": "Firefox", "title": "Docs"},
                    "timeout_ms": 500,
                    "poll_ms": 10,
                    "use_events": False,
                    "focus": True,
                }
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    import vhk.system.active_window as aw

    row = {"id": "0x4040", "class": "Firefox", "title": "Docs", "workspace": "Web", "focused": False}
    seen = {"count": 0}

    def fake_snapshot(*, selector=None, include_geometry=False, focused_first=True):
        seen["count"] += 1
        if seen["count"] == 1:
            return ([], "x11")
        return ([dict(row)], "x11")

    focused_calls: list[dict] = []

    def fake_focus(selector, *, timeout_ms=3000, poll_ms=100, focused_first=True):
        focused_calls.append({
            "wm_class": selector.wm_class,
            "title": selector.title,
            "timeout_ms": timeout_ms,
            "poll_ms": poll_ms,
        })
        return (dict(row, focused=True), "x11")

    monkeypatch.setattr(aw, "detect_compositor", lambda: "x11")
    monkeypatch.setattr(aw, "get_window_list_snapshot", fake_snapshot)
    monkeypatch.setattr(aw, "focus_window_matching", fake_focus)

    res = Runner(project).run("m")
    assert res.ok is True
    assert res.vars["i3_con_id"] == "0x4040"
    assert res.vars["i3_workspace"] == "Web"
    assert res.vars["i3_window"]["title"] == "Docs"
    assert focused_calls == [
        {
            "wm_class": "Firefox",
            "title": "Docs",
            "timeout_ms": 500,
            "poll_ms": 50,
        }
    ]
