from __future__ import annotations

from pathlib import Path

import pytest

from vhk.core.models import Region
from vhk.system import screenshot as screenshot_mod
from vhk.system.session import set_preferred_backend


@pytest.fixture(autouse=True)
def _reset_backend():
    set_preferred_backend("auto")
    yield
    set_preferred_backend("auto")


def _mkexe(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


def _write_png(path: Path, w: int, h: int) -> None:
    from PIL import Image

    im = Image.new("RGB", (w, h))
    im.save(path)


def test_capture_wayland_spectacle_fullscreen_builds_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "spectacle")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("--output") + 1])
        _write_png(out_path, 40, 30)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out)
    assert calls == [[str(tmp_path / "spectacle"), "--background", "--nonotify", "--fullscreen", "--output", str(out)]]
    assert out.exists()


def test_capture_wayland_spectacle_region_crops(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "spectacle")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("--output") + 1])
        _write_png(out_path, 200, 100)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "cropped.png"
    screenshot_mod.capture(out, region=Region(x=10, y=20, w=50, h=40))
    assert calls and calls[0][:4] == [str(tmp_path / "spectacle"), "--background", "--nonotify", "--fullscreen"]
    from PIL import Image

    with Image.open(out) as im:
        assert im.size == (50, 40)


def test_capture_wayland_gnome_screenshot_fullscreen_builds_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "gnome-screenshot")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("-f") + 1])
        _write_png(out_path, 80, 60)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out)
    assert calls == [[str(tmp_path / "gnome-screenshot"), "-f", str(out)]]
    assert out.exists()


def test_capture_interactive_region_wayland_prefers_spectacle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "spectacle")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("--output") + 1])
        _write_png(out_path, 25, 25)

        class R:
            returncode = 0
            stderr = ""
            stdout = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "region.png"
    screenshot_mod.capture_interactive_region(out)
    assert calls == [[str(tmp_path / "spectacle"), "--background", "--nonotify", "--region", "--output", str(out)]]
    assert out.exists()


def test_capture_interactive_region_x11_uses_scrot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "scrot")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[cmd.index("--file") + 1])
        _write_png(out_path, 10, 12)

        class R:
            returncode = 0
            stderr = ""
            stdout = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "region.png"
    screenshot_mod.capture_interactive_region(out)
    assert calls == [[str(tmp_path / "scrot"), "--select", "--overwrite", "--silent", "--file", str(out)]]
    assert out.exists()


def test_capture_wayland_grim_fullscreen_uses_scale_1_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "grim")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("VHK_GRIM_SCALE", raising=False)

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[-1])
        _write_png(out_path, 64, 48)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out)
    assert calls == [[str(tmp_path / "grim"), "-s", "1", str(out)]]
    assert out.exists()



def test_capture_wayland_grim_scale_auto_omits_s_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "grim")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setenv("VHK_GRIM_SCALE", "auto")

    calls: list[list[str]] = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)
        out_path = Path(cmd[-1])
        _write_png(out_path, 10, 10)

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(screenshot_mod.subprocess, "run", fake_run)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out, region=Region(x=1, y=2, w=3, h=4))
    assert calls == [[str(tmp_path / "grim"), "-g", "1,2 3x4", str(out)]]
    assert out.exists()
