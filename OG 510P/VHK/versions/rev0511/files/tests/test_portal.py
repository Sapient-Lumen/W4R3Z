from __future__ import annotations

from pathlib import Path

import pytest

import vhk.system.portal as portal_mod
from vhk.system import screenshot as screenshot_mod


def test_parse_portal_response_extracts_uri():
    text = """signal time=1601192691.739126 sender=:1.53 -> destination=:1.50 serial=143 path=/org/freedesktop/portal/desktop/request/1_50/u3; interface=org.freedesktop.portal.Request; member=Response
       uint32 0
       array [
          dict entry(
             string \"uri\"
             variant             string \"file:///home/user/Screenshot_20200927_094451.png\"
          )
       ]
"""
    resp = portal_mod._parse_response_text(text)
    assert resp is not None
    assert resp.response == 0
    assert resp.uri == "file:///home/user/Screenshot_20200927_094451.png"


def test_parse_portal_response_extracts_color():
    text = """signal time=1.0 sender=:1.2 -> destination=(null destination) serial=10 path=/org/freedesktop/portal/desktop/request/1_2/u1; interface=org.freedesktop.portal.Request; member=Response
       uint32 0
       array [
          dict entry(
             string \"color\"
             variant             struct {
                double 0.1
                double 0.2
                double 0.3
             }
          )
       ]
"""
    resp = portal_mod._parse_response_text(text)
    assert resp is not None
    assert resp.response == 0
    assert resp.color == (0.1, 0.2, 0.3)
    assert portal_mod.rgb01_to_hex(resp.color) == "#1a334c"


def test_screenshot_capture_supports_portal_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Force screenshot module to use a portal backend, but stub portal capture.
    backend = screenshot_mod.ScreenshotBackend(name="portal", exe="/usr/bin/gdbus", supports_geometry=False)
    monkeypatch.setattr(screenshot_mod, "choose_backend", lambda: backend)

    def fake_save(out_path: Path, interactive=True, modal=True, timeout_s=90.0):
        out_path.write_bytes(b"PNG")
        return out_path, "file:///tmp/fake.png"

    monkeypatch.setattr(portal_mod, "save_portal_screenshot", fake_save)

    out = tmp_path / "shot.png"
    screenshot_mod.capture(out)
    assert out.exists()
    assert out.read_bytes() == b"PNG"
