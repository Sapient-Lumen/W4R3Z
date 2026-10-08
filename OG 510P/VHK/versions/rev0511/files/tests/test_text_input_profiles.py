from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system import input as input_mod


def _mkexe(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_xvkbd_type_text_uses_utf16_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "xvkbd")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    calls: list[dict] = []

    def fake_run(cmd, capture_output=True, text=True, input=None):
        file_arg = cmd[cmd.index("-file") + 1]
        payload = Path(file_arg).read_bytes()
        calls.append({"cmd": cmd, "payload": payload, "path": file_arg})

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(input_mod.subprocess, "run", fake_run)

    used = input_mod.type_text("héllo", delay_ms_per_char=9, backend="xvkbd")
    assert used == "xvkbd"
    assert calls
    cmd = calls[-1]["cmd"]
    assert cmd[:1] == [str(tmp_path / "xvkbd")]
    assert "-file" in cmd
    assert "-utf16" in cmd
    assert "-delay" in cmd
    assert calls[-1]["payload"].startswith(b"\xff\xfe")
    assert not Path(calls[-1]["path"]).exists()


def test_runner_turbo_prefers_clipboard_for_large_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {
        "name": "p",
        "settings": {
            "event_log": False,
            "runner_profile": "turbo",
            "turbo_type_clipboard_threshold": 5,
        },
        "macros": {"m": "macros/m.yaml"},
    }
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {
                    "type": "TypeText",
                    "text": "hello world",
                    "preserve_clipboard": True,
                }
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    reads: list[str] = []
    writes: list[tuple[str, str]] = []
    pastes: list[tuple[str, str, bool]] = []
    typed: list[str] = []

    monkeypatch.setattr("vhk.core.runner.clipboard_mod.read", lambda selection="clipboard": reads.append(selection) or "OLD")
    monkeypatch.setattr("vhk.core.runner.clipboard_mod.write", lambda text, selection="clipboard": writes.append((selection, text)))
    monkeypatch.setattr("vhk.core.runner.input_mod.paste", lambda selection="clipboard", shortcut="auto", clearmodifiers=False: pastes.append((selection, shortcut, clearmodifiers)))
    monkeypatch.setattr("vhk.core.runner.input_mod.type_text", lambda *args, **kwargs: typed.append(args[0]) or "xdotool")

    res = Runner(project).run("m")
    assert res.ok
    assert reads == ["clipboard"]
    assert writes == [("clipboard", "hello world"), ("clipboard", "OLD")]
    assert pastes == [("clipboard", "auto", False)]
    assert typed == []
    assert res.vars["last_type_backend"] == "clipboard"


def test_runner_turbo_scales_inter_step_delay(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = {
        "name": "p",
        "settings": {
            "event_log": False,
            "runner_profile": "turbo",
            "turbo_delay_scale": 0.1,
        },
        "macros": {"m": "macros/m.yaml"},
    }
    macros = {
        "m": {
            "name": "m",
            "steps": [
                {"type": "Log", "message": "a", "delay_ms": 100},
            ],
        }
    }
    proj = _write_project(tmp_path, manifest, macros)
    project = load_project(proj)

    sleeps: list[float] = []
    monkeypatch.setattr("vhk.core.runner.time.sleep", lambda seconds: sleeps.append(seconds))

    res = Runner(project).run("m")
    assert res.ok
    assert sleeps == [0.01]
