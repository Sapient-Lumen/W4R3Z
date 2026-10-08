from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.init_project import init_project


runner = CliRunner()


class _FakeCapture:
    def __init__(self, payload: dict[str, object] | None):
        self.payload = payload

    def finish(self) -> dict[str, object] | None:
        return self.payload


def _patch_x11_recording(monkeypatch, *, steps: list[dict[str, object]], payload: dict[str, object] | None):
    import shutil
    import vhk.cli as cli
    import vhk.system.record_x11 as rx11
    import vhk.system.session as session_mod

    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(session_mod, "detect_backend", lambda: "x11")
    monkeypatch.setattr(rx11, "resolve_recording_smoothing", lambda *args, **kwargs: (25, 4))
    monkeypatch.setattr(rx11, "record_x11_steps", lambda **kwargs: list(steps))
    monkeypatch.setattr(cli, "_start_window_context_capture", lambda **kwargs: _FakeCapture(payload))


def test_record_x11_project_applies_window_context(monkeypatch, tmp_path: Path):
    init_project(tmp_path, template="minimal")
    payload = {
        "duration_ms": 3000,
        "samples": [
            {"class": "Firefox", "title": "Mozilla Firefox"},
            {"class": "Firefox", "title": "Mozilla Firefox — Docs"},
        ],
        "suggested": {
            "stable": {"class": "Firefox", "focused": True},
            "exact": {"class": "Firefox", "title": "^(?:Mozilla\\ Firefox|Mozilla\\ Firefox\\ —\\ Docs)$", "title_regex": True},
            "title_strategy": "alternation",
            "stats": {"samples": 2},
        },
    }
    _patch_x11_recording(monkeypatch, steps=[{"type": "Log", "message": "hi"}], payload=payload)

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--project",
            str(tmp_path),
            "--macro",
            "rec",
            "--capture-window-context",
            "--apply-window-context",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    doc = yaml.safe_load((tmp_path / "macros" / "rec.yaml").read_text())
    assert doc["when"] == {"class": "Firefox", "focused": True}
    assert doc["steps"] == [{"type": "Log", "message": "hi"}]


def test_record_x11_can_write_window_context_sidecar(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [{"class": "kitty", "title": "shell"}],
        "suggested": {
            "stable": {"class": "kitty", "focused": True},
            "exact": {"class": "kitty", "title": "shell", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 1},
        },
    }
    sidecar = tmp_path / "ctx.json"
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(monkeypatch, steps=[{"type": "Log", "message": "x"}], payload=payload)

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--capture-window-context",
            "--window-context-out",
            str(sidecar),
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    assert macro_doc["steps"] == [{"type": "Log", "message": "x"}]

    payload_doc = json.loads(sidecar.read_text())
    assert payload_doc["suggested"]["stable"] == {"class": "kitty", "focused": True}


def test_record_x11_rejects_apply_without_project(monkeypatch):
    _patch_x11_recording(monkeypatch, steps=[], payload=None)

    result = runner.invoke(app, ["record-x11", "--capture-window-context", "--apply-window-context"])
    assert result.exit_code != 0
    assert "requires --project" in result.output


def test_record_x11_coord_mode_mouse_window_prefixes_coordmode_and_translates(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [
            {
                "wm": "x11",
                "class": "Firefox",
                "title": "Mozilla Firefox",
                "geometry": {
                    "rect": {"x": 100, "y": 200, "w": 800, "h": 600},
                    "client": {"x": 102, "y": 205, "w": 796, "h": 590},
                },
            }
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Mozilla Firefox", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 1},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[{"type": "MouseMove", "x": 110, "y": 220}, {"type": "MouseClickAt", "x": 125, "y": 240, "button": 1}],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--coord-mode-mouse",
            "window",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    assert macro_doc["steps"] == [
        {"type": "CoordMode", "target": "mouse", "mode": "window"},
        {"type": "MouseMove", "x": 10, "y": 20},
        {"type": "MouseClickAt", "x": 25, "y": 40, "button": 1},
    ]


def test_record_x11_coord_mode_mouse_requires_geometry(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [{"wm": "x11", "class": "Firefox", "title": "Mozilla Firefox"}],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Mozilla Firefox", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 1},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(monkeypatch, steps=[{"type": "MouseMove", "x": 110, "y": 220}], payload=payload)

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--coord-mode-mouse",
            "window",
        ],
    )
    assert result.exit_code != 0
    assert "usable geometry" in result.output



def test_record_x11_segment_by_window_context_injects_waits_and_splits_delays(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x2", "class": "kitty", "title": "shell"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1500},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    assert macro_doc["steps"] == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, stable)",
        },
        {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
        {"type": "Delay", "ms": 1000},
        {
            "type": "WaitForWindow",
            "selector": {"class": "kitty", "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, stable)",
        },
        {"type": "Delay", "ms": 500},
        {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
    ]


def test_record_x11_segment_by_window_context_uses_exact_selectors_when_stable_is_ambiguous(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Alpha"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x2", "class": "Firefox", "title": "Beta"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "^(?:Alpha|Beta)$", "title_regex": True},
            "title_strategy": "alternation",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") == "WaitForWindow"]
    assert waits[0]["selector"] == {"class": "Firefox", "title": "Alpha", "title_regex": False, "focused": True}
    assert waits[1]["selector"] == {"class": "Firefox", "title": "Beta", "title_regex": False, "focused": True}
    assert waits[0]["comment"] == "recorded window segment (active, exact)"
    assert waits[1]["comment"] == "recorded window segment (active, exact)"


def test_record_x11_same_window_title_change_stays_flat_without_opt_in(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Inbox"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Compose"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "^(?:Inbox|Compose)$", "title_regex": True},
            "title_strategy": "alternation",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") == "WaitForWindow"]
    assert len(waits) == 1
    assert waits[0]["selector"] == {"class": "Firefox", "focused": True}


def test_record_x11_segment_on_title_change_splits_same_window_identity(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Inbox"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Compose"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "^(?:Inbox|Compose)$", "title_regex": True},
            "title_strategy": "alternation",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    sidecar = tmp_path / "ctx.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--segment-on-title-change",
            "--window-context-out",
            str(sidecar),
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") == "WaitForWindow"]
    assert waits[0]["selector"] == {"class": "Firefox", "title": "Inbox", "title_regex": False, "focused": True}
    assert waits[1]["selector"] == {"class": "Firefox", "title": "Compose", "title_regex": False, "focused": True}
    assert waits[0]["comment"] == "recorded window segment (active, exact)"
    assert waits[1]["comment"] == "recorded window segment (active, exact)"

    sidecar_doc = yaml.safe_load(sidecar.read_text())
    assert sidecar_doc["segment_on_title_change"] is True
    assert len(sidecar_doc["segments"]) == 2
    assert sidecar_doc["window_guard_scope"] == "active"


def test_record_x11_segment_by_window_context_can_use_present_scope(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 1500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x2", "class": "kitty", "title": "shell"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--window-guard-scope",
            "present",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") == "WaitForWindow"]
    assert waits[0]["selector"] == {"class": "Firefox"}
    assert waits[1]["selector"] == {"class": "kitty"}
    assert waits[0]["comment"] == "recorded window segment (present, stable)"
    assert waits[1]["comment"] == "recorded window segment (present, stable)"



def test_record_x11_segment_by_window_context_can_emit_event_guards(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x2", "class": "kitty", "title": "shell"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    sidecar = tmp_path / "ctx.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1500},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--window-context-out",
            str(sidecar),
            "--segment-by-window-context",
            "--window-guard-mode",
            "event",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    assert macro_doc["steps"] == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, stable)",
        },
        {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
        {"type": "Delay", "ms": 1000},
        {
            "type": "WaitForWindowEvent",
            "event": "focus",
            "selector": {"class": "kitty", "focused": True},
            "timeout_ms": 3000,
            "comment": "recorded window transition (event, focus, stable)",
        },
        {"type": "Delay", "ms": 500},
        {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
    ]

    sidecar_doc = yaml.safe_load(sidecar.read_text())
    assert sidecar_doc["window_guard_mode"] == "event"
    assert sidecar_doc["segments"][1]["transition_reason"] == "focus"



def test_record_x11_title_segments_can_emit_title_event_guards(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Inbox"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Compose"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "^(?:Inbox|Compose)$", "title_regex": True},
            "title_strategy": "alternation",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--segment-on-title-change",
            "--window-guard-mode",
            "event",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") in {"WaitForWindow", "WaitForWindowEvent"}]
    assert waits == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "title": "Inbox", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, exact)",
        },
        {
            "type": "WaitForWindowEvent",
            "event": "title",
            "selector": {"class": "Firefox", "title": "Compose", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "comment": "recorded window transition (event, title, exact)",
        },
    ]


def test_record_x11_geometry_refresh_segments_can_emit_geometry_event_guards(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {
                "capture_elapsed_ms": 0,
                "wm": "x11",
                "id": "0x1",
                "class": "Firefox",
                "title": "Docs",
                "geometry": {
                    "rect": {"x": 100, "y": 200, "w": 800, "h": 600},
                    "client": {"x": 102, "y": 205, "w": 796, "h": 590},
                },
            },
            {
                "capture_elapsed_ms": 1000,
                "wm": "x11",
                "id": "0x1",
                "class": "Firefox",
                "title": "Docs",
                "geometry": {
                    "rect": {"x": 140, "y": 230, "w": 900, "h": 640},
                    "client": {"x": 142, "y": 235, "w": 896, "h": 630},
                },
            },
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 125, "y": 240, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 165, "y": 270, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--coord-mode-mouse",
            "window",
            "--window-guard-mode",
            "event",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") in {"WaitForWindow", "WaitForWindowEvent"}]
    assert waits == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "title": "Docs", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, exact)",
        },
        {
            "type": "WaitForWindowEvent",
            "event": "geometry",
            "selector": {"class": "Firefox", "title": "Docs", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "comment": "recorded window transition (event, geometry, exact)",
        },
    ]





def test_record_x11_same_window_workspace_change_stays_flat_without_opt_in(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs", "workspace": "1:web"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs", "workspace": "2:mail"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") == "WaitForWindow"]
    assert len(waits) == 1
    assert waits[0]["selector"] == {"class": "Firefox", "focused": True}


def test_record_x11_workspace_segments_can_emit_workspace_event_guards(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 2500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs", "workspace": "1:web"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs", "workspace": "2:mail"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    sidecar = tmp_path / "ctx.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
            {"type": "Delay", "ms": 1000},
            {"type": "MouseClickAt", "x": 30, "y": 40, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--window-context-out",
            str(sidecar),
            "--segment-by-window-context",
            "--segment-on-workspace-change",
            "--window-guard-mode",
            "event",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    waits = [step for step in macro_doc["steps"] if step.get("type") in {"WaitForWindow", "WaitForWindowEvent"}]
    assert waits == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "title": "Docs", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, exact)",
        },
        {
            "type": "WaitForWindowEvent",
            "event": "workspace",
            "selector": {"class": "Firefox", "title": "Docs", "title_regex": False, "focused": True},
            "timeout_ms": 3000,
            "comment": "recorded window transition (event, workspace, exact)",
        },
    ]

    sidecar_doc = yaml.safe_load(sidecar.read_text())
    assert sidecar_doc["segment_on_workspace_change"] is True
    assert sidecar_doc["segments"][1]["transition_reason"] == "workspace"


def test_record_x11_event_guard_mode_requires_active_scope(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 1500,
        "samples": [
            {"capture_elapsed_ms": 0, "wm": "x11", "id": "0x1", "class": "Firefox", "title": "Docs"},
            {"capture_elapsed_ms": 1000, "wm": "x11", "id": "0x2", "class": "kitty", "title": "shell"},
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[{"type": "MouseClickAt", "x": 10, "y": 20, "button": 1}],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--window-guard-mode",
            "event",
            "--window-guard-scope",
            "present",
            "--quiet",
        ],
    )
    assert result.exit_code != 0
    assert "--window-guard-mode event requires --window-guard-scope" in result.output
    assert "active." in result.output

def test_record_x11_rejects_segment_on_workspace_change_without_segmenting(monkeypatch, tmp_path: Path):
    _patch_x11_recording(monkeypatch, steps=[], payload=None)

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(tmp_path / "recorded.yaml"),
            "--segment-on-workspace-change",
        ],
    )
    assert result.exit_code != 0
    assert "segment-on-workspace-change" in result.output
    assert "segment-by-window-context" in result.output


def test_record_x11_rejects_segment_on_title_change_without_segmenting(monkeypatch, tmp_path: Path):
    _patch_x11_recording(monkeypatch, steps=[], payload=None)

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(tmp_path / "recorded.yaml"),
            "--segment-on-title-change",
        ],
    )
    assert result.exit_code != 0
    assert "segment-on-title-change" in result.output
    assert "segment-by-window-context" in result.output


def test_record_x11_segment_by_window_context_relativizes_each_window_segment(monkeypatch, tmp_path: Path):
    payload = {
        "duration_ms": 3000,
        "samples": [
            {
                "capture_elapsed_ms": 0,
                "wm": "x11",
                "id": "0x1",
                "class": "Firefox",
                "title": "Docs",
                "geometry": {
                    "rect": {"x": 100, "y": 200, "w": 800, "h": 600},
                    "client": {"x": 102, "y": 205, "w": 796, "h": 590},
                },
            },
            {
                "capture_elapsed_ms": 1000,
                "wm": "x11",
                "id": "0x2",
                "class": "kitty",
                "title": "shell",
                "geometry": {
                    "rect": {"x": 500, "y": 100, "w": 900, "h": 700},
                    "client": {"x": 502, "y": 105, "w": 896, "h": 690},
                },
            },
        ],
        "suggested": {
            "stable": {"class": "Firefox"},
            "exact": {"class": "Firefox", "title": "Docs", "title_regex": False},
            "title_strategy": "exact",
            "stats": {"samples": 2},
        },
    }
    out = tmp_path / "recorded.yaml"
    _patch_x11_recording(
        monkeypatch,
        steps=[
            {"type": "MouseClickAt", "x": 125, "y": 240, "button": 1},
            {"type": "Delay", "ms": 1500},
            {"type": "MouseClickAt", "x": 515, "y": 125, "button": 1},
        ],
        payload=payload,
    )

    result = runner.invoke(
        app,
        [
            "record-x11",
            "--out",
            str(out),
            "--segment-by-window-context",
            "--coord-mode-mouse",
            "window",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output

    macro_doc = yaml.safe_load(out.read_text())
    assert macro_doc["steps"] == [
        {
            "type": "WaitForWindow",
            "selector": {"class": "Firefox", "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, stable)",
        },
        {"type": "CoordMode", "target": "mouse", "mode": "window"},
        {"type": "MouseClickAt", "x": 25, "y": 40, "button": 1},
        {"type": "Delay", "ms": 1000},
        {
            "type": "WaitForWindow",
            "selector": {"class": "kitty", "focused": True},
            "timeout_ms": 3000,
            "stable_ms": 0,
            "stable_attempts": 1,
            "comment": "recorded window segment (active, stable)",
        },
        {"type": "Delay", "ms": 500},
        {"type": "MouseClickAt", "x": 15, "y": 25, "button": 1},
    ]
