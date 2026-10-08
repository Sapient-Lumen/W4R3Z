from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app
from vhk.system.cursor_pos import CursorPos

runner = CliRunner()


def test_window_at_cursor_cli_json(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_window_at_cursor_snapshot",
        lambda **kwargs: (
            {
                "id": "0x1",
                "title": "Firefox",
                "class": "Firefox",
                "app_id": "Firefox",
                "workspace": "1:web",
                "geometry": {"rect": {"x": 10, "y": 20, "w": 800, "h": 600}, "client": None},
            },
            "x11",
            CursorPos(x=44, y=55, backend="xdotool"),
        ),
    )

    result = runner.invoke(app, ["window-at-cursor"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["wm"] == "x11"
    assert payload["cursor"]["x"] == 44
    assert payload["window"]["title"] == "Firefox"
    assert payload["suggested"]["stable"]["app_id"] == "Firefox"



def test_window_at_cursor_cli_no_json_without_window(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_window_at_cursor_snapshot",
        lambda **kwargs: (None, "hyprland", CursorPos(x=9, y=9, backend="hyprctl")),
    )

    result = runner.invoke(app, ["window-at-cursor", "--no-json"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "null"
