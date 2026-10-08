from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_window_list_json(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_window_list_snapshot",
        lambda **kwargs: (
            [
                {"id": "0x1", "title": "Firefox", "class": "Firefox", "workspace": "1", "focused": True},
                {"id": "0x2", "title": "shell", "class": "Alacritty", "workspace": "2", "focused": False},
            ],
            "x11",
        ),
    )

    result = runner.invoke(app, ["window-list"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["wm"] == "x11"
    assert payload["count"] == 2
    assert payload["windows"][0]["title"] == "Firefox"



def test_window_list_no_json_prints_rows(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_window_list_snapshot",
        lambda **kwargs: (
            [{"id": "0x1", "title": "Firefox", "class": "Firefox", "workspace": "1", "focused": True}],
            "x11",
        ),
    )

    result = runner.invoke(app, ["window-list", "--no-json"])
    assert result.exit_code == 0, result.output
    assert "Firefox" in result.output
    assert "0x1" in result.output
