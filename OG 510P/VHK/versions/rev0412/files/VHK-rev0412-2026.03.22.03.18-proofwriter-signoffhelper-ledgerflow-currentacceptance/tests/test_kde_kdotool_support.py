from __future__ import annotations

import os
from pathlib import Path

from vhk.system import active_window
from vhk.system import cursor_pos


def _write_fake_kdotool(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    exe = bin_dir / "kdotool"
    exe.write_text(
        """#!/usr/bin/env python3
import sys

args = sys.argv[1:]
if args[:2] == ['getmouselocation', '--shell']:
    sys.stdout.write('X=11\\nY=22\\n')
    sys.exit(0)

if args[:2] == ['getactivewindow', 'getwindowid']:
    sys.stdout.write('{deadbeef-dead-beef-dead-beefdeadbeef}\\n')
    sys.exit(0)

if args[:2] == ['getactivewindow', 'getwindowname']:
    sys.stdout.write('My Window Title\\n')
    sys.exit(0)

if args[:2] == ['getactivewindow', 'getwindowclassname']:
    sys.stdout.write('org.kde.MyApp\\n')
    sys.exit(0)

if args[:2] == ['getactivewindow', 'getwindowpid']:
    sys.stdout.write('1234\\n')
    sys.exit(0)

if args[:2] == ['getactivewindow', 'getwindowgeometry']:
    sys.stdout.write('Window {deadbeef-dead-beef-dead-beefdeadbeef}\\n')
    sys.stdout.write('  Position: 10,20 (screen: 0)\\n')
    sys.stdout.write('  Geometry: 800x600\\n')
    sys.exit(0)

sys.stderr.write('unsupported args: %r\\n' % (args,))
sys.exit(2)
"""
    )
    exe.chmod(0o755)
    return bin_dir


def test_kdotool_cursorpos_and_active_window(monkeypatch, tmp_path: Path):
    bin_dir = _write_fake_kdotool(tmp_path)

    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
    monkeypatch.setenv("KDE_FULL_SESSION", "true")

    pos = cursor_pos.get_cursor_pos()
    assert pos.backend == "kdotool"
    assert (pos.x, pos.y) == (11, 22)

    info, wm = active_window.get_active_window_info()
    assert wm == "kwin"
    assert info.get("class") == "org.kde.MyApp"
    assert info.get("app_id") == "org.kde.MyApp"
    assert info.get("title") == "My Window Title"
    assert info.get("pid") == 1234
    assert info.get("focused") is True

    rect, client, wm2 = active_window.get_active_window_geometry()
    assert wm2 == "kwin"
    assert client is None
    assert rect == {"x": 10, "y": 20, "w": 800, "h": 600}
